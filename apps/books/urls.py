from django.urls import path

from apps.books import views

app_name = "books"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_book, name="create"),
    path("<int:book_id>/", views.detail, name="detail"),
    path("<int:book_id>/edit/", views.edit_book, name="edit"),
    path("<int:book_id>/delete/", views.delete_book, name="delete"),
    path("asset/<int:asset_id>/read/", views.read_asset, name="read_asset"),
    path("asset/<int:asset_id>/download/", views.download_asset, name="download_asset"),
    path("asset/<int:asset_id>/delete/", views.delete_asset, name="delete_asset"),
]
