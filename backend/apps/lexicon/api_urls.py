from django.urls import path

from .views import WordDetailView, WordListView

urlpatterns = [
    path("words/", WordListView.as_view(), name="word-list"),
    path("words/<int:pk>/", WordDetailView.as_view(), name="word-detail"),
]
