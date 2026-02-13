from rest_framework import serializers

from .models import PracticeSession


class PracticeSessionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = PracticeSession
        fields = (
            "id",
            "session_type",
            "child_display_name",
            "planned_item_count",
            "started_at",
            "submitted_at",
            "items",
        )

    def get_items(self, obj):
        return [
            {
                "position": item.position,
                "word": {
                    "id": item.word_id,
                    "hanzi": item.word.hanzi,
                    "jyutping": item.word.jyutping,
                    "meaning": item.word.meaning,
                    "sound_group": item.word.sound_group,
                },
            }
            for item in obj.items.select_related("word").order_by("position")
        ]
