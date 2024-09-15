from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("commingsoon.urls")),
    path("", include("accounts.urls")),
    path("", include("pages.urls")),
    path("", include("helpcenter.urls")),
    path("user/", include("userarea.urls")),
    path("user/", include("chatapp.urls")),
    path("", include("orders.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
