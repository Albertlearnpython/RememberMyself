from django import forms
from django.db import transaction
from django.utils import timezone

from apps.scenery.models import SceneryEntry
from apps.scenery.services import apply_uploaded_photos


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if not isinstance(data, (list, tuple)):
            data = [data]
        single_clean = super().clean
        return [single_clean(item, initial) for item in data]


class SceneryEditorForm(forms.ModelForm):
    photos = MultipleFileField(
        label="上传图片",
        required=False,
        widget=MultipleFileInput(
            attrs={
                "accept": "image/*,.heic,.heif,.jpg,.jpeg,.png,.webp",
                "multiple": True,
            }
        ),
    )
    captured_at = forms.DateTimeField(
        label="拍摄时间",
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = SceneryEntry
        fields = [
            "title",
            "short_note",
            "why_it_matters",
            "long_note",
            "captured_at",
            "place_name",
            "location_text",
            "country",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "visibility",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "可留空，系统会按地点和日期自动生成"}),
            "short_note": forms.TextInput(attrs={"placeholder": "例如：那天的风很轻，海面刚好发亮"}),
            "why_it_matters": forms.Textarea(attrs={"rows": 4}),
            "long_note": forms.Textarea(attrs={"rows": 8}),
            "place_name": forms.TextInput(attrs={"placeholder": "例如：深圳湾公园"}),
            "location_text": forms.TextInput(attrs={"placeholder": "可自动填入详细地点，也可手动改"}),
            "country": forms.TextInput(attrs={"placeholder": "国家"}),
            "province": forms.TextInput(attrs={"placeholder": "省份 / 州"}),
            "city": forms.TextInput(attrs={"placeholder": "城市"}),
            "district": forms.TextInput(attrs={"placeholder": "区县 / 区域"}),
            "latitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "纬度"}),
            "longitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "经度"}),
            "visibility": forms.Select(),
        }
        labels = {
            "title": "标题",
            "short_note": "一句说明",
            "why_it_matters": "为什么记得这里",
            "long_note": "长说明",
            "place_name": "地点名",
            "location_text": "地址说明",
            "country": "国家",
            "province": "省份 / 州",
            "city": "城市",
            "district": "区县 / 区域",
            "latitude": "纬度",
            "longitude": "经度",
            "visibility": "可见性",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.captured_at:
            self.initial["captured_at"] = timezone.localtime(self.instance.captured_at).strftime(
                "%Y-%m-%dT%H:%M"
            )
        self.upload_summary = {}

    def clean(self):
        cleaned_data = super().clean()
        uploads = cleaned_data.get("photos") or []
        has_existing_photos = bool(self.instance.pk and self.instance.photos.exists())
        if not uploads and not has_existing_photos:
            self.add_error("photos", "至少上传一张图片。")
        if uploads and len(uploads) > 12:
            self.add_error("photos", "第一版一次最多上传 12 张图片。")
        return cleaned_data

    def save(self, commit=True):
        entry = super().save(commit=False)
        if not commit:
            return entry

        uploads = self.cleaned_data.get("photos") or []
        with transaction.atomic():
            entry.save()
            self.upload_summary = apply_uploaded_photos(entry, uploads)
        return entry

