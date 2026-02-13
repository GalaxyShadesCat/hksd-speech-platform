from rest_framework import serializers

from apps.lexicon.models import SoundGroup

from .models import AgeBand, ScreeningItem, ScreeningSession


class AgeBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeBand
        fields = ("id", "label", "min_months", "max_months")


class ScreeningWordSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    hanzi = serializers.CharField(allow_blank=True)
    jyutping = serializers.CharField(allow_blank=True)
    meaning = serializers.CharField(allow_blank=True)
    sound_group = serializers.ChoiceField(choices=SoundGroup.choices)


class ScreeningItemSerializer(serializers.ModelSerializer):
    word = ScreeningWordSerializer(read_only=True)

    class Meta:
        model = ScreeningItem
        fields = ("position", "word")


class ScreeningSessionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = ScreeningSession
        fields = ("id", "age_band", "started_at", "submitted_at", "items")

    def get_items(self, obj):
        items = obj.screening_set.items.select_related("word").order_by("position")
        return ScreeningItemSerializer(items, many=True).data
