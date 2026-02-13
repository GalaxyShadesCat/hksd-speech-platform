from rest_framework import serializers

from .models import Word, WordComponent


class WordComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordComponent
        fields = ("position", "component_word_id", "component_word")
        depth = 1


class WordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = (
            "id",
            "hanzi",
            "jyutping",
            "meaning",
            "image_url",
            "audio_url",
            "sound_group",
            "hierarchy_stage",
            "is_active",
        )


class WordDetailSerializer(serializers.ModelSerializer):
    components = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = (
            "id",
            "hanzi",
            "jyutping",
            "meaning",
            "image_url",
            "audio_url",
            "sound_group",
            "hierarchy_stage",
            "is_active",
            "components",
        )

    def get_components(self, obj):
        return [
            {
                "position": c.position,
                "word": {
                    "id": c.component_word_id,
                    "hanzi": c.component_word.hanzi,
                    "jyutping": c.component_word.jyutping,
                    "meaning": c.component_word.meaning,
                },
            }
            for c in obj.components.all().order_by("position")
        ]
