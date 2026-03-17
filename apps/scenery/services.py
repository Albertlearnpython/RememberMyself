from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import requests
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import ExifTags, Image, ImageOps
from pillow_heif import register_heif_opener

from apps.scenery.models import SceneryEntry, SceneryPhoto


register_heif_opener()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
DATETIME_FORMAT = "%Y:%m:%d %H:%M:%S"
OFFSET_PATTERN = re.compile(r"^(?P<sign>[+-])(?P<hours>\d{2}):(?P<minutes>\d{2})$")
EXIF_TAGS = ExifTags.TAGS
GPS_TAGS = ExifTags.GPSTAGS
EXIF_IFD = getattr(getattr(ExifTags, "IFD", None), "Exif", 34665)
GPS_IFD = getattr(getattr(ExifTags, "IFD", None), "GPSInfo", 34853)


def apply_uploaded_photos(entry: SceneryEntry, uploaded_files) -> dict:
    uploads = list(uploaded_files or [])
    created_photos = []
    start_order = entry.photos.count()

    for index, uploaded_file in enumerate(uploads, start=start_order):
        payload = build_photo_payload(uploaded_file)
        photo = SceneryPhoto.objects.create(
            entry=entry,
            image=payload["content"],
            original_filename=payload["original_filename"],
            width=payload["width"],
            height=payload["height"],
            taken_at=payload["captured_at"],
            latitude=_to_decimal(payload["latitude"]),
            longitude=_to_decimal(payload["longitude"]),
            exif_payload=payload["exif_payload"],
            sort_order=index,
        )
        created_photos.append(photo)

    summary = sync_entry_metadata(entry, created_photos)
    summary["uploaded_count"] = len(created_photos)
    summary["created_photo_ids"] = [photo.pk for photo in created_photos]
    return summary


def sync_entry_metadata(entry: SceneryEntry, uploaded_photos=None) -> dict:
    ordered_photos = list(uploaded_photos or entry.photos.order_by("sort_order", "id"))
    first_timed_photo = next((photo for photo in ordered_photos if photo.taken_at), None)
    first_geo_photo = next(
        (photo for photo in ordered_photos if photo.latitude is not None and photo.longitude is not None),
        None,
    )

    changed_fields = []
    detected_time = first_timed_photo is not None
    detected_location = first_geo_photo is not None

    if entry.captured_at is None and first_timed_photo is not None:
        entry.captured_at = first_timed_photo.taken_at
        changed_fields.append("captured_at")

    if not entry.timezone_name and entry.captured_at is not None and entry.captured_at.tzinfo is not None:
        entry.timezone_name = entry.captured_at.tzinfo.tzname(entry.captured_at) or ""
        if entry.timezone_name:
            changed_fields.append("timezone_name")

    if entry.latitude is None and first_geo_photo is not None:
        entry.latitude = first_geo_photo.latitude
        changed_fields.append("latitude")

    if entry.longitude is None and first_geo_photo is not None:
        entry.longitude = first_geo_photo.longitude
        changed_fields.append("longitude")

    if (
        (not entry.place_name or not entry.location_text or not entry.city)
        and entry.latitude is not None
        and entry.longitude is not None
    ):
        reverse_data = reverse_geocode(float(entry.latitude), float(entry.longitude))
        for field_name in ("country", "province", "city", "district", "place_name", "location_text"):
            if not getattr(entry, field_name) and reverse_data.get(field_name):
                setattr(entry, field_name, reverse_data[field_name])
                changed_fields.append(field_name)

    if not entry.location_text and entry.latitude is not None and entry.longitude is not None:
        entry.location_text = f"{entry.latitude}, {entry.longitude}"
        changed_fields.append("location_text")

    if not entry.title:
        entry.title = generate_entry_title(entry)
        changed_fields.append("title")

    unique_fields = list(dict.fromkeys(changed_fields))
    if unique_fields:
        entry.save(update_fields=unique_fields + ["updated_at"])

    return {
        "detected_time": detected_time,
        "detected_location": detected_location,
        "changed_fields": unique_fields,
    }


def build_photo_payload(uploaded_file) -> dict:
    filename = getattr(uploaded_file, "name", "") or "scenery-photo"
    suffix = Path(filename).suffix.lower()
    content_type = getattr(uploaded_file, "content_type", "") or ""
    if suffix not in IMAGE_EXTENSIONS and not content_type.startswith("image/"):
        raise ValidationError("请上传图片文件，支持 JPG、PNG、WEBP、HEIC。")

    try:
        uploaded_file.seek(0)
        image = Image.open(uploaded_file)
        image.load()
    except Exception as exc:
        raise ValidationError("图片无法解析，请换一张原图重新上传。") from exc

    exif_payload = _extract_exif_payload(image)
    captured_at = _parse_captured_at(exif_payload)
    latitude, longitude = _parse_coordinates(exif_payload)
    rendered = _render_image_file(image, filename)

    return {
        "content": rendered["content"],
        "width": rendered["width"],
        "height": rendered["height"],
        "captured_at": captured_at,
        "latitude": latitude,
        "longitude": longitude,
        "original_filename": filename,
        "exif_payload": exif_payload,
    }


def resequence_photos(entry: SceneryEntry):
    for index, photo in enumerate(entry.photos.order_by("sort_order", "id")):
        if photo.sort_order != index:
            photo.sort_order = index
            photo.save(update_fields=["sort_order"])


def generate_entry_title(entry: SceneryEntry) -> str:
    location = entry.place_name or entry.city or entry.province or entry.country
    if entry.captured_at and location:
        local_dt = timezone.localtime(entry.captured_at)
        return f"{location} · {local_dt:%Y-%m-%d}"
    if location:
        return location
    if entry.captured_at:
        local_dt = timezone.localtime(entry.captured_at)
        return f"{local_dt:%Y-%m-%d} 的风景"
    return "未命名风景"


def _render_image_file(image: Image.Image, original_filename: str) -> dict:
    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA"}:
        background = Image.new("RGB", image.size, (248, 246, 241))
        alpha = image.getchannel("A")
        background.paste(image.convert("RGB"), mask=alpha)
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")

    image.thumbnail((2200, 2200))

    stem = Path(original_filename).stem or "scenery-photo"
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-") or "scenery-photo"
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=88, optimize=True)
    buffer.seek(0)
    content = ContentFile(buffer.read(), name=f"{safe_stem}.jpg")
    return {
        "content": content,
        "width": image.width,
        "height": image.height,
    }


def _extract_exif_payload(image: Image.Image) -> dict:
    raw_exif = image.getexif()
    payload = {}
    for key, value in raw_exif.items():
        name = EXIF_TAGS.get(key, str(key))
        if name in {"GPSInfo", "ExifOffset", "InteropOffset"}:
            continue
        payload[name] = _serialize_exif_value(value)

    payload.update(_extract_ifd_payload(raw_exif, EXIF_IFD, EXIF_TAGS))
    gps_payload = _extract_ifd_payload(raw_exif, GPS_IFD, GPS_TAGS)
    if gps_payload:
        payload["GPSInfo"] = gps_payload
    return payload


def _extract_ifd_payload(raw_exif, ifd_key, tag_map):
    try:
        ifd_payload = raw_exif.get_ifd(ifd_key)
    except Exception:
        return {}
    if not isinstance(ifd_payload, dict):
        return {}
    return {
        tag_map.get(key, str(key)): _serialize_exif_value(value)
        for key, value in ifd_payload.items()
    }


def _serialize_exif_value(value):
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, tuple):
        return [_serialize_exif_value(item) for item in value]
    if isinstance(value, list):
        return [_serialize_exif_value(item) for item in value]
    try:
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return float(value)
    except Exception:
        return str(value)
    return value


def _parse_captured_at(exif_payload: dict):
    raw_value = (
        exif_payload.get("DateTimeOriginal")
        or exif_payload.get("DateTimeDigitized")
        or exif_payload.get("DateTime")
    )
    if not raw_value:
        return None

    try:
        naive_dt = datetime.strptime(str(raw_value), DATETIME_FORMAT)
    except ValueError:
        return None

    offset_value = exif_payload.get("OffsetTimeOriginal") or exif_payload.get("OffsetTime")
    tzinfo = None
    if offset_value:
        match = OFFSET_PATTERN.match(str(offset_value))
        if match:
            sign = 1 if match.group("sign") == "+" else -1
            delta = timedelta(
                hours=int(match.group("hours")),
                minutes=int(match.group("minutes")),
            )
            tzinfo = dt_timezone(sign * delta)

    if tzinfo is not None:
        return naive_dt.replace(tzinfo=tzinfo)
    return timezone.make_aware(naive_dt, timezone.get_current_timezone())


def _parse_coordinates(exif_payload: dict):
    gps = exif_payload.get("GPSInfo")
    if not isinstance(gps, dict):
        return None, None

    latitude = _convert_gps_coordinate(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
    longitude = _convert_gps_coordinate(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
    return latitude, longitude


def _convert_gps_coordinate(values, ref):
    if not values or len(values) != 3:
        return None

    try:
        degrees = float(values[0])
        minutes = float(values[1])
        seconds = float(values[2])
    except (TypeError, ValueError):
        return None

    decimal_value = degrees + minutes / 60 + seconds / 3600
    if ref in {"S", "W"}:
        decimal_value *= -1
    return round(decimal_value, 6)


def _to_decimal(value):
    if value is None:
        return None
    return Decimal(str(value))


@lru_cache(maxsize=128)
def reverse_geocode(latitude: float, longitude: float) -> dict:
    rounded_lat = round(latitude, 5)
    rounded_lon = round(longitude, 5)
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": rounded_lat,
                "lon": rounded_lon,
                "format": "jsonv2",
                "addressdetails": 1,
                "zoom": 17,
            },
            headers={"User-Agent": "RememberMyself/1.0 (scenery metadata lookup)"},
            timeout=6,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return {}

    address = payload.get("address") or {}
    city = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("county")
        or ""
    )
    district = (
        address.get("suburb")
        or address.get("city_district")
        or address.get("district")
        or address.get("county")
        or ""
    )
    place_name = (
        payload.get("name")
        or address.get("attraction")
        or address.get("tourism")
        or address.get("road")
        or ""
    )
    return {
        "country": address.get("country") or "",
        "province": address.get("state") or address.get("province") or address.get("region") or "",
        "city": city,
        "district": district,
        "place_name": place_name,
        "location_text": payload.get("display_name") or "",
    }
