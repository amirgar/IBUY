from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard")
    # path("/accounts", include("django.contrib.auth.urls")),
]