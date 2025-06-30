from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("main_page.urls")),
    path("about_us", include("about_us.urls")),
    path("account", include("account.urls")),
    path('get_access/', admin.site.urls),
]
