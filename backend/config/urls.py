from pathlib import Path

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("config.api_urls")),
]

frontend_index = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"
if frontend_index.exists():
    urlpatterns.append(path("", TemplateView.as_view(template_name="index.html"), name="home"))
else:
    urlpatterns.append(path("", lambda request: HttpResponse("HKSD Speech Platform API"), name="home"))
