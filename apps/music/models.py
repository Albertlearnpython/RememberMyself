import mimetypes
import os
from pathlib import Path

from django.db import models


mimetypes.add_type("audio/flac", ".flac", strict=False)
mimetypes.add_type("audio/x-m4a", ".m4a", strict=False)


class MusicTrackQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return self
        if getattr(user, "is_authenticated", False):
            return self.exclude(visibility=MusicTrack.Visibility.PRIVATE)
        return self.filter(visibility=MusicTrack.Visibility.PUBLIC)


class MusicTag(models.Model):
    name = models.CharField("标签名", max_length=50, unique=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "音乐标签"
        verbose_name_plural = "音乐标签"

    def __str__(self):
        return self.name


class MusicTrack(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开可见"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    title = models.CharField("曲名", max_length=200)
    artist = models.CharField("歌手 / 创作者", max_length=120, blank=True)
    album = models.CharField("专辑", max_length=120, blank=True)
    cover_image_url = models.URLField("封面图链接", blank=True)
    tag_links = models.ManyToManyField(
        MusicTag,
        blank=True,
        related_name="tracks",
        verbose_name="标签",
    )
    short_review = models.CharField("一句短评", max_length=240, blank=True)
    why_it_matters = models.TextField("为什么喜欢", blank=True)
    long_note = models.TextField("长说明", blank=True)
    visibility = models.CharField(
        "可见性",
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = MusicTrackQuerySet.as_manager()

    class Meta:
        ordering = ["-updated_at", "title"]
        verbose_name = "音乐"
        verbose_name_plural = "音乐"

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [tag.name for tag in self.tag_links.all()]

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


class MusicAsset(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = "public", "公开"
        LOGIN_REQUIRED = "login_required", "登录后可见"
        PRIVATE = "private", "仅编辑者可见"

    track = models.ForeignKey(
        MusicTrack,
        on_delete=models.CASCADE,
        related_name="assets",
        verbose_name="所属音乐",
    )
    file = models.FileField("文件", upload_to="music/assets/%Y/%m/%d/")
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
        verbose_name = "音乐文件"
        verbose_name_plural = "音乐文件"

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
