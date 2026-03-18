from pathlib import Path

import markdown
from django.core.files.base import ContentFile
from django.db import models
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class ArticleEntryQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return self
        if getattr(user, "is_authenticated", False):
            return self.exclude(visibility=ArticleEntry.Visibility.PRIVATE)
        return self.filter(visibility=ArticleEntry.Visibility.PUBLIC)


class ArticleEntry(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开可见"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    title = models.CharField("标题", max_length=200)
    summary = models.CharField("摘要", max_length=280, blank=True)
    markdown_content = models.TextField("Markdown 正文", blank=True)
    source_file = models.FileField(
        "Markdown 源文件",
        upload_to="articles/source/%Y/%m/%d/",
        blank=True,
    )
    source_filename = models.CharField("源文件名", max_length=255, blank=True)
    visibility = models.CharField(
        "可见性",
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = ArticleEntryQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at", "title"]
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title

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

    @property
    def rendered_markdown(self):
        html = markdown.markdown(
            self.markdown_content or "",
            extensions=["extra", "sane_lists"],
            output_format="html5",
        )
        return mark_safe(html)

    @property
    def excerpt(self):
        if self.summary:
            return self.summary
        plain_text = strip_tags(self.rendered_markdown)
        compact = " ".join(plain_text.split())
        return compact[:140] + ("…" if len(compact) > 140 else "")

    @property
    def fallback_label(self):
        first_char = (self.title or "").strip()[:1]
        return first_char or "文"

    @property
    def download_name(self):
        if self.source_filename:
            return self.source_filename
        if self.source_file:
            return Path(self.source_file.name).name
        return self.default_source_filename

    @property
    def default_source_filename(self):
        base = slugify(self.title or "", allow_unicode=True).strip("-")
        if not base:
            base = f"article-{self.pk or 'entry'}"
        return f"{base}.md"

    @property
    def formatted_source_size(self):
        try:
            size = self.source_file.size
        except (ValueError, OSError):
            size = 0

        units = ["B", "KB", "MB", "GB"]
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024

    def ensure_source_file(self):
        if self.source_file.name:
            return

        filename = self.source_filename or self.default_source_filename
        payload = ContentFile((self.markdown_content or "").encode("utf-8"))
        generated_name = self.source_file.field.generate_filename(self, filename)
        self.source_file.name = self.source_file.storage.save(generated_name, payload)
        self.source_filename = filename
        self.save(update_fields=["source_file", "source_filename", "updated_at"])
