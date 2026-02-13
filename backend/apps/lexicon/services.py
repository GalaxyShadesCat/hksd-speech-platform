from apps.lexicon.models import Word


def get_word_components(word_id: int):
    word = Word.objects.prefetch_related("components__component_word").get(pk=word_id)
    return [
        {
            "position": component.position,
            "word_id": component.component_word_id,
            "hanzi": component.component_word.hanzi,
            "jyutping": component.component_word.jyutping,
            "meaning": component.component_word.meaning,
        }
        for component in word.components.all().order_by("position")
    ]
