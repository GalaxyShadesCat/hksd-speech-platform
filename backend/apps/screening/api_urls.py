from django.urls import path

from .views import (
    AgeBandListView,
    ScreeningSessionCreateView,
    ScreeningSessionDetailView,
    ScreeningSessionSubmitView,
    ScreeningSessionSummaryView,
)

urlpatterns = [
    path("screening/age-bands/", AgeBandListView.as_view(), name="screening-age-bands"),
    path("screening/sessions/", ScreeningSessionCreateView.as_view(), name="screening-session-create"),
    path("screening/sessions/<int:session_id>/", ScreeningSessionDetailView.as_view(), name="screening-session-detail"),
    path(
        "screening/sessions/<int:session_id>/submit/",
        ScreeningSessionSubmitView.as_view(),
        name="screening-session-submit",
    ),
    path(
        "screening/sessions/<int:session_id>/summary/",
        ScreeningSessionSummaryView.as_view(),
        name="screening-session-summary",
    ),
]
