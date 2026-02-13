from rest_framework import generics, permissions

from .models import Word
from .serializers import WordDetailSerializer, WordListSerializer


class WordListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WordListSerializer

    def get_queryset(self):
        return Word.objects.filter(is_active=True).order_by("hierarchy_stage", "id")


class WordDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = WordDetailSerializer

    def get_queryset(self):
        return Word.objects.filter(is_active=True).prefetch_related("components__component_word")
