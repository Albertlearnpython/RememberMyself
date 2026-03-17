from django.urls import path

from apps.music import views

app_name = "music"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_track, name="create"),
    path("<int:track_id>/", views.detail, name="detail"),
    path("<int:track_id>/edit/", views.edit_track, name="edit"),
    path("<int:track_id>/delete/", views.delete_track, name="delete"),
    path("asset/<int:asset_id>/download/", views.download_asset, name="download_asset"),
    path("asset/<int:asset_id>/delete/", views.delete_asset, name="delete_asset"),
]
