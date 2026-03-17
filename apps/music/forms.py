import re

from django import forms

from apps.music.models import MusicAsset, MusicTag, MusicTrack


TAG_SPLIT_PATTERN = re.compile(r"[\n,，]+")


class MusicEditorForm(forms.ModelForm):
    tag_links = forms.ModelMultipleChoiceField(
        label="已有标签",
        queryset=MusicTag.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    new_tags = forms.CharField(
        label="新增标签",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "例如：夜晚, 疗愈, 独处"}),
    )
    asset_file = forms.FileField(
        label="上传音乐文件",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": ".mp3,.flac,.wav,.m4a,.aac,.ogg,.ape"}
        ),
    )
    asset_visibility = forms.ChoiceField(
        label="文件权限",
        choices=MusicAsset.Visibility.choices,
        required=False,
        initial=MusicAsset.Visibility.LOGIN_REQUIRED,
    )
    download_enabled = forms.BooleanField(label="允许下载", required=False, initial=True)

    class Meta:
        model = MusicTrack
        fields = [
            "title",
            "artist",
            "album",
            "cover_image_url",
            "tag_links",
            "short_review",
            "why_it_matters",
            "long_note",
            "visibility",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "例如：夜航星"}),
            "artist": forms.TextInput(attrs={"placeholder": "歌手 / 创作者"}),
            "album": forms.TextInput(attrs={"placeholder": "专辑名，可选"}),
            "cover_image_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "short_review": forms.TextInput(
                attrs={"placeholder": "一句短评，适合出现在列表卡片里"}
            ),
            "why_it_matters": forms.Textarea(attrs={"rows": 4}),
            "long_note": forms.Textarea(attrs={"rows": 8}),
            "visibility": forms.Select(),
        }
        labels = {
            "title": "曲名",
            "artist": "歌手 / 创作者",
            "album": "专辑",
            "cover_image_url": "封面图链接",
            "short_review": "一句短评",
            "why_it_matters": "为什么喜欢",
            "long_note": "长说明",
            "visibility": "可见性",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tag_links"].queryset = MusicTag.objects.order_by("name")
        if self.instance.pk:
            self.fields["tag_links"].initial = self.instance.tag_links.all()

    def clean_new_tags(self):
        raw_value = self.cleaned_data.get("new_tags", "")
        parsed_tags = [
            item.strip()
            for item in TAG_SPLIT_PATTERN.split(raw_value)
            if item.strip()
        ]
        deduped_tags = []
        seen = set()
        for tag_name in parsed_tags:
            normalized = tag_name.casefold()
            if normalized in seen:
                continue
            seen.add(normalized)
            deduped_tags.append(tag_name)
        return deduped_tags

    def clean_asset_file(self):
        asset_file = self.cleaned_data.get("asset_file")
        if asset_file is not None and asset_file.size == 0:
            raise forms.ValidationError("上传的文件为空。")
        return asset_file

    def save(self, commit=True):
        track = super().save(commit=False)
        selected_tags = list(self.cleaned_data.get("tag_links") or [])
        resolved_tags = {tag.name.casefold(): tag for tag in selected_tags}

        for tag_name in self.cleaned_data.get("new_tags", []):
            normalized = tag_name.casefold()
            if normalized in resolved_tags:
                continue
            existing_tag = MusicTag.objects.filter(name__iexact=tag_name).first()
            if existing_tag is None:
                existing_tag = MusicTag.objects.create(name=tag_name)
            resolved_tags[normalized] = existing_tag

        if commit:
            track.save()
            track.tag_links.set(resolved_tags.values())
        else:
            self.save_m2m = lambda: track.tag_links.set(resolved_tags.values())

        asset_file = self.cleaned_data.get("asset_file")
        if commit and asset_file:
            MusicAsset.objects.create(
                track=track,
                file=asset_file,
                visibility=self.cleaned_data.get("asset_visibility")
                or MusicAsset.Visibility.LOGIN_REQUIRED,
                download_enabled=self.cleaned_data.get("download_enabled", True),
            )
        return track
