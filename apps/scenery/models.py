from django.db import models
from django.urls import reverse


class SceneryEntryQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return self
        if getattr(user, "is_authenticated", False):
            return self.exclude(visibility=SceneryEntry.Visibility.PRIVATE)
        return self.filter(visibility=SceneryEntry.Visibility.PUBLIC)


class SceneryEntry(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开可见"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    title = models.CharField("标题", max_length=200, blank=True)
    short_note = models.CharField("一句说明", max_length=240, blank=True)
    why_it_matters = models.TextField("为什么记得这里", blank=True)
    long_note = models.TextField("长说明", blank=True)
    captured_at = models.DateTimeField("拍摄时间", blank=True, null=True)
    timezone_name = models.CharField("时区", max_length=64, blank=True)
    latitude = models.DecimalField("纬度", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("经度", max_digits=9, decimal_places=6, blank=True, null=True)
    country = models.CharField("国家", max_length=80, blank=True)
    province = models.CharField("省份 / 州", max_length=80, blank=True)
    city = models.CharField("城市", max_length=80, blank=True)
    district = models.CharField("区县 / 区域", max_length=80, blank=True)
    place_name = models.CharField("地点名", max_length=160, blank=True)
    location_text = models.CharField("地址说明", max_length=255, blank=True)
    visibility = models.CharField(
        "可见性",
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = SceneryEntryQuerySet.as_manager()

    class Meta:
        ordering = ["-captured_at", "-updated_at", "-created_at"]
        verbose_name = "景色记录"
        verbose_name_plural = "景色记录"

    def __str__(self):
        return self.display_title

    @property
    def primary_photo(self):
        photos_manager = getattr(self, "photos", None)
        if photos_manager is None:
            return None
        cached_photos = getattr(self, "_prefetched_objects_cache", {}).get("photos")
        if cached_photos:
            return cached_photos[0]
        return photos_manager.order_by("sort_order", "id").first()

    @property
    def cover_image_url(self):
        photo = self.primary_photo
        if photo is None:
            return ""
        return reverse("scenery:photo_image", args=[photo.pk])

    @property
    def display_title(self):
        if self.title:
            return self.title
        location = self.place_name or self.city or self.province
        if self.captured_at and location:
            return f"{location} · {self.captured_at:%Y-%m-%d}"
        if location:
            return location
        if self.captured_at:
            return f"{self.captured_at:%Y-%m-%d} 的风景"
        return "未命名风景"

    @property
    def location_summary(self):
        parts = []
        for value in (self.place_name, self.city, self.province):
            if value and value not in parts:
                parts.append(value)
        if parts:
            return " · ".join(parts)
        if self.latitude is not None and self.longitude is not None:
            return f"{self.latitude}, {self.longitude}"
        return "地点待补充"

    @property
    def photo_count(self):
        cached_count = getattr(self, "_photo_count", None)
        if cached_count is not None:
            return cached_count
        photos_manager = getattr(self, "photos", None)
        if photos_manager is None:
            return 0
        return photos_manager.count()

    def is_visible_to(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        if self.visibility == self.Visibility.PUBLIC:
            return True
        if self.visibility == self.Visibility.LOGIN_REQUIRED:
            return getattr(user, "is_authenticated", False)
        return False

    def can_edit(self, user):
        return getattr(user, "is_authenticated", False) and (
            getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
        )


class SceneryPhoto(models.Model):
    entry = models.ForeignKey(
        SceneryEntry,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="所属景色",
    )
    image = models.ImageField("图片", upload_to="scenery/photos/%Y/%m/%d/")
    original_filename = models.CharField("原始文件名", max_length=255, blank=True)
    width = models.PositiveIntegerField("宽度", default=0)
    height = models.PositiveIntegerField("高度", default=0)
    taken_at = models.DateTimeField("该图拍摄时间", blank=True, null=True)
    latitude = models.DecimalField("纬度", max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField("经度", max_digits=9, decimal_places=6, blank=True, null=True)
    exif_payload = models.JSONField("EXIF 信息", default=dict, blank=True)
    sort_order = models.PositiveIntegerField("排序", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "景色图片"
        verbose_name_plural = "景色图片"

    def __str__(self):
        return self.original_filename or f"{self.entry.display_title} 图片"

    @property
    def image_url(self):
        return reverse("scenery:photo_image", args=[self.pk])

    @property
    def coordinates(self):
        if self.latitude is None or self.longitude is None:
            return ""
        return f"{self.latitude}, {self.longitude}"

    def save(self, *args, **kwargs):
        if self.image and (not self.width or not self.height):
            self.width = self.width or getattr(self.image, "width", 0) or 0
            self.height = self.height or getattr(self.image, "height", 0) or 0
        super().save(*args, **kwargs)

