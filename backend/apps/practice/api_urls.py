from django.urls import path

from .views import (
    PracticeHistoryView,
    PracticeMissedView,
    PracticeReviewCreateView,
    PracticeSessionCreateView,
    PracticeSessionDetailView,
    PracticeSessionSubmitView,
)

urlpatterns = [
    path("practice/sessions/", PracticeSessionCreateView.as_view(), name="practice-session-create"),
    path("practice/sessions/<int:session_id>/", PracticeSessionDetailView.as_view(), name="practice-session-detail"),
    path("practice/sessions/<int:session_id>/submit/", PracticeSessionSubmitView.as_view(), name="practice-session-submit"),
    path("practice/history/", PracticeHistoryView.as_view(), name="practice-history"),
    path("practice/missed/", PracticeMissedView.as_view(), name="practice-missed"),
    path("practice/review/", PracticeReviewCreateView.as_view(), name="practice-review-create"),
]
