from pathlib import Path

from django import forms
from django.core.files.base import ContentFile

from apps.articles.models import ArticleEntry


ALLOWED_SOURCE_SUFFIXES = {".md", ".markdown", ".txt"}
SOURCE_DECODE_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "utf-16")


class ArticleEditorForm(forms.ModelForm):
    source_upload = forms.FileField(
        label="上传 Markdown 文件",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": ".md,.markdown,.txt"}),
    )

    class Meta:
        model = ArticleEntry
        fields = [
            "title",
            "summary",
            "markdown_content",
            "visibility",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "例如：我与长期记录"}),
            "summary": forms.TextInput(
                attrs={"placeholder": "一句摘要，会出现在列表卡片和首页溪流里"}
            ),
            "markdown_content": forms.Textarea(
                attrs={
                    "rows": 22,
                    "placeholder": "# 标题\n\n在这里直接粘贴或编辑 Markdown 正文。",
                }
            ),
            "visibility": forms.Select(),
        }
        labels = {
            "title": "标题",
            "summary": "摘要",
            "markdown_content": "Markdown 正文",
            "visibility": "可见性",
        }

    def clean_source_upload(self):
        source_upload = self.cleaned_data.get("source_upload")
        if source_upload is None:
            return None
        if source_upload.size == 0:
            raise forms.ValidationError("上传的 Markdown 文件为空。")

        suffix = Path(source_upload.name).suffix.lower()
        if suffix not in ALLOWED_SOURCE_SUFFIXES:
            raise forms.ValidationError("目前只支持上传 .md / .markdown / .txt 文件。")
        return source_upload

    def clean(self):
        cleaned_data = super().clean()
        source_upload = cleaned_data.get("source_upload")
        markdown_content = (cleaned_data.get("markdown_content") or "").strip()

        if source_upload is not None:
            cleaned_data["markdown_content"] = self._decode_source_upload(source_upload)
        elif not markdown_content:
            self.add_error("markdown_content", "请填写 Markdown 正文，或上传一个 .md 文件。")

        return cleaned_data

    def save(self, commit=True):
        article = super().save(commit=False)
        source_upload = self.cleaned_data.get("source_upload")
        article.markdown_content = self.cleaned_data.get("markdown_content", "")

        if not commit:
            return article

        article.save()

        if source_upload is not None:
            if article.source_file.name and article.download_name != source_upload.name:
                article.source_file.delete(save=False)
                article.source_file.name = ""
            article.source_filename = source_upload.name
            self._persist_source_file(article, filename=source_upload.name)
        else:
            article.source_filename = article.source_filename or article.default_source_filename
            self._persist_source_file(article, filename=article.source_filename)

        article.save(update_fields=["source_file", "source_filename", "updated_at"])
        return article

    def _decode_source_upload(self, source_upload):
        raw_bytes = source_upload.read()
        source_upload.seek(0)

        for encoding in SOURCE_DECODE_ENCODINGS:
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise forms.ValidationError("这个 Markdown 文件无法识别编码，请优先使用 UTF-8。")

    def _persist_source_file(self, article, filename):
        payload = ContentFile((article.markdown_content or "").encode("utf-8"))
        storage = article.source_file.storage

        if article.source_file.name:
            with storage.open(article.source_file.name, "wb") as file_handle:
                file_handle.write(payload.read())
            return

        generated_name = article.source_file.field.generate_filename(
            article,
            filename or article.default_source_filename,
        )
        article.source_file.name = storage.save(generated_name, payload)

