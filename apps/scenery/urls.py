from django.urls import path

from apps.scenery import views

app_name = "scenery"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_entry, name="create"),
    path("photo/<int:photo_id>/image/", views.photo_image, name="photo_image"),
    path("photo/<int:photo_id>/delete/", views.delete_photo, name="delete_photo"),
    path("<int:entry_id>/", views.detail, name="detail"),
    path("<int:entry_id>/edit/", views.edit_entry, name="edit"),
    path("<int:entry_id>/delete/", views.delete_entry, name="delete"),
]

