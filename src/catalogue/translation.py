from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Author)
class AuthorTranslationOptions(TranslationOptions):
    fields = (
        'first_name',
        'last_name',
        'description',
    )


@register(models.Place)
class PlaceTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'locative',
    )
