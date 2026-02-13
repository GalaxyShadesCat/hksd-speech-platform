from django.urls import include, path

urlpatterns = [
    path("", include("apps.accounts.api_urls")),
    path("", include("apps.lexicon.api_urls")),
    path("", include("apps.screening.api_urls")),
    path("", include("apps.practice.api_urls")),
    path("", include("apps.accounts.staff_api_urls")),
]
