from django.contrib import admin

from .models import Word, WordComponent


class WordComponentInline(admin.TabularInline):
    model = WordComponent
    fk_name = "parent_word"
    extra = 1


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("id", "hanzi", "jyutping", "sound_group", "hierarchy_stage", "is_active")
    list_filter = ("sound_group", "hierarchy_stage", "is_active")
    search_fields = ("hanzi", "jyutping", "meaning")
    inlines = [WordComponentInline]


@admin.register(WordComponent)
class WordComponentAdmin(admin.ModelAdmin):
    list_display = ("parent_word", "component_word", "position")
    list_filter = ("parent_word",)
    search_fields = ("parent_word__hanzi", "component_word__hanzi", "parent_word__jyutping", "component_word__jyutping")
