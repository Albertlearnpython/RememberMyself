from django.urls import path

from apps.articles import views

app_name = "articles"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create_article, name="create"),
    path("<int:article_id>/", views.detail, name="detail"),
    path("<int:article_id>/edit/", views.edit_article, name="edit"),
    path("<int:article_id>/delete/", views.delete_article, name="delete"),
    path("<int:article_id>/download/", views.download_source, name="download_source"),
]

