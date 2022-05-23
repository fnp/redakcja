import re
from django.utils.translation import gettext_lazy as _


class Check:
    def check_meta(self, meta):
        return False


class CheckParse(Check):
    tag = 'parse'
    description = _('Book parse error.')


class CheckMeta(Check):
    tag = 'meta'
    description = _('Metadata parse error.')


class CheckCoverLocal(Check):
    tag = 'cover-local'
    description = _('Cover is not local')

    def check_meta(self, meta):
        print(meta)
        if meta.cover_source is None:
            print('no cover_source')
            return False
        return not re.match(r'https?://redakcja.wolnelektury.pl/cover/image/', meta.cover_source)


rules = [
    CheckParse(),
    CheckMeta(),
    CheckCoverLocal(),
]

rules_by_tag = {
    r.tag: r
    for r in rules
}
