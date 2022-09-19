from modeltranslation.translator import register, TranslationOptions
from . import models


@register(models.Author)
class AuthorTranslationOptions(TranslationOptions):
    fields = (
        'first_name',
        'last_name',
        'place_of_birth',
        'place_of_death',
        'description',
    )
