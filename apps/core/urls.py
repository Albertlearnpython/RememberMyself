from django.urls import path

from apps.core import views

app_name = "core"

urlpatterns = [
    path("food/", views.placeholder, {"module_key": "food"}, name="food"),
    path("music/", views.placeholder, {"module_key": "music"}, name="music"),
    path("scenery/", views.placeholder, {"module_key": "scenery"}, name="scenery"),
    path("fitness/", views.placeholder, {"module_key": "fitness"}, name="fitness"),
    path("finance/", views.placeholder, {"module_key": "finance"}, name="finance"),
    path("schedule/", views.placeholder, {"module_key": "schedule"}, name="schedule"),
    path("methods/", views.placeholder, {"module_key": "methods"}, name="methods"),
]
