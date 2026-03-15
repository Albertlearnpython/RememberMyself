import os
from pathlib import Path
import mimetypes

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

mimetypes.add_type("application/epub+zip", ".epub", strict=True)


class BookQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return self
        if getattr(user, "is_authenticated", False):
            return self.exclude(visibility=Book.Visibility.PRIVATE)
        return self.filter(visibility=Book.Visibility.PUBLIC)


class Book(models.Model):
    class Status(models.TextChoices):
        PLANNED = "planned", "想读"
        READING = "reading", "在读"
        PAUSED = "paused", "暂停"
        FINISHED = "finished", "读完"
        REVISITING = "revisiting", "重读"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开可见"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    title = models.CharField("书名", max_length=200)
    subtitle = models.CharField("副标题", max_length=200, blank=True)
    author = models.CharField("作者", max_length=120, blank=True)
    translator = models.CharField("译者", max_length=120, blank=True)
    publisher = models.CharField("出版社", max_length=120, blank=True)
    publish_year = models.PositiveIntegerField("出版年份", blank=True, null=True)
    cover_image_url = models.URLField("封面图链接", blank=True)
    status = models.CharField(
        "阅读状态",
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    rating = models.PositiveSmallIntegerField(
        "评分",
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    tags = models.CharField("标签", max_length=255, blank=True)
    short_review = models.CharField("一句短评", max_length=240, blank=True)
    why_it_matters = models.TextField("为什么重要", blank=True)
    long_note = models.TextField("长笔记", blank=True)
    reading_started_at = models.DateField("开始阅读", blank=True, null=True)
    reading_finished_at = models.DateField("完成阅读", blank=True, null=True)
    visibility = models.CharField(
        "可见性",
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at", "title"]
        verbose_name = "书籍"
        verbose_name_plural = "书籍"

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [item.strip() for item in self.tags.split(",") if item.strip()]

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


class BookAsset(models.Model):
    class AssetType(models.TextChoices):
        EBOOK = "ebook", "书籍文件"
        NOTE = "note", "笔记附件"
        AUDIO = "audio", "音频"
        OTHER = "other", "其他"

    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name="所属书籍",
    )
    asset_type = models.CharField(
        "资源类型",
        max_length=20,
        choices=AssetType.choices,
        default=AssetType.EBOOK,
    )
    file = models.FileField("文件", upload_to="books/assets/%Y/%m/%d/")
    file_name = models.CharField("文件名", max_length=255, blank=True)
    file_size = models.PositiveBigIntegerField("文件大小", default=0)
    download_enabled = models.BooleanField("允许下载", default=True)
    visibility = models.CharField(
        "可见性",
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.LOGIN_REQUIRED,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "书籍资源"
        verbose_name_plural = "书籍资源"

    def __str__(self):
        return self.file_name or os.path.basename(self.file.name)

    @property
    def file_extension(self):
        target = self.file_name or self.file.name
        return Path(target).suffix.lower()

    @property
    def mime_type(self):
        guessed_type = mimetypes.guess_type(self.file_name or self.file.name)[0]
        return guessed_type or "application/octet-stream"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file_name or os.path.basename(self.file.name)
            try:
                self.file_size = self.file.size
            except OSError:
                pass
        super().save(*args, **kwargs)

    def can_access(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        if self.visibility == self.Visibility.PRIVATE:
            return False
        return getattr(user, "is_authenticated", False)

    @property
    def formatted_file_size(self):
        size = self.file_size or 0
        units = ["B", "KB", "MB", "GB"]
        value = float(size)
        for unit in units:
            if value < 1024 or unit == units[-1]:
                if unit == "B":
                    return f"{int(value)} {unit}"
                return f"{value:.1f} {unit}"
            value /= 1024
