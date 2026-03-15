from django import forms

from apps.books.models import Book, BookAsset


class BookEditorForm(forms.ModelForm):
    asset_file = forms.FileField(
        label="上传文件",
        required=False,
        widget=forms.ClearableFileInput(
            attrs={"accept": ".epub,.pdf,.txt,.md,.mobi,.azw3"}
        ),
    )
    asset_type = forms.ChoiceField(
        label="文件类型",
        choices=BookAsset.AssetType.choices,
        required=False,
        initial=BookAsset.AssetType.EBOOK,
    )
    asset_visibility = forms.ChoiceField(
        label="文件权限",
        choices=BookAsset.Visibility.choices,
        required=False,
        initial=BookAsset.Visibility.LOGIN_REQUIRED,
    )
    reader_enabled = forms.BooleanField(label="允许在线阅读", required=False, initial=True)
    download_enabled = forms.BooleanField(label="允许下载", required=False, initial=True)

    class Meta:
        model = Book
        fields = [
            "title",
            "subtitle",
            "author",
            "translator",
            "publisher",
            "publish_year",
            "cover_image_url",
            "status",
            "rating",
            "tags",
            "short_review",
            "why_it_matters",
            "long_note",
            "reading_started_at",
            "reading_finished_at",
            "visibility",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "例如：沉思录"}),
            "subtitle": forms.TextInput(attrs={"placeholder": "可选"}),
            "author": forms.TextInput(attrs={"placeholder": "作者"}),
            "translator": forms.TextInput(attrs={"placeholder": "译者，可选"}),
            "publisher": forms.TextInput(attrs={"placeholder": "出版社"}),
            "publish_year": forms.NumberInput(attrs={"placeholder": "年份"}),
            "cover_image_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "status": forms.Select(),
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5, "placeholder": "1-5"}),
            "tags": forms.TextInput(attrs={"placeholder": "例如：哲学, 自我管理, 反思"}),
            "short_review": forms.TextInput(
                attrs={"placeholder": "一句短评，适合出现在列表卡片里"}
            ),
            "why_it_matters": forms.Textarea(attrs={"rows": 4}),
            "long_note": forms.Textarea(attrs={"rows": 8}),
            "reading_started_at": forms.DateInput(attrs={"type": "date"}),
            "reading_finished_at": forms.DateInput(attrs={"type": "date"}),
            "visibility": forms.Select(),
        }
        labels = {
            "title": "书名",
            "subtitle": "副标题",
            "author": "作者",
            "translator": "译者",
            "publisher": "出版社",
            "publish_year": "出版年份",
            "cover_image_url": "封面图链接",
            "status": "阅读状态",
            "rating": "评分",
            "tags": "标签",
            "short_review": "一句短评",
            "why_it_matters": "为什么重要",
            "long_note": "长笔记",
            "reading_started_at": "开始阅读",
            "reading_finished_at": "完成阅读",
            "visibility": "可见性",
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data.get("tags", "")
        tags = [item.strip() for item in raw_tags.split(",") if item.strip()]
        return ", ".join(dict.fromkeys(tags))

    def clean_asset_file(self):
        asset_file = self.cleaned_data.get("asset_file")
        if asset_file is not None and asset_file.size == 0:
            raise forms.ValidationError("上传的文件为空。")
        return asset_file

    def save(self, commit=True):
        book = super().save(commit=commit)
        asset_file = self.cleaned_data.get("asset_file")
        if commit and asset_file:
            BookAsset.objects.create(
                book=book,
                file=asset_file,
                asset_type=self.cleaned_data.get("asset_type") or BookAsset.AssetType.EBOOK,
                visibility=self.cleaned_data.get("asset_visibility")
                or BookAsset.Visibility.LOGIN_REQUIRED,
                reader_enabled=self.cleaned_data.get("reader_enabled", True),
                download_enabled=self.cleaned_data.get("download_enabled", True),
            )
        return book
