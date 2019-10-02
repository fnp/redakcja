# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from librarian import RDFNS, WLURI, ValidationError
from librarian.dcparser import BookInfo
from catalogue.management import XmlUpdater
from catalogue.management.commands import XmlUpdaterCommand


class FixDC(XmlUpdater):
    commit_desc = "auto-fixing DC"
    retain_publishable = True
    only_first_chunk = True

    def fix_wluri(elem, change, verbose):
        try:
            WLURI.strict(elem.text)
        except ValidationError:
            correct_field = str(WLURI.from_slug(
                                WLURI(elem.text.strip()).slug))
            try:
                WLURI.strict(correct_field)
            except ValidationError:
                # Can't make a valid WLURI out of it, leave as is.
                return False
            if verbose:
                print("Changing %s from %s to %s" % (
                        elem.tag, elem.text, correct_field
                    ))
            elem.text = correct_field
            return True
    for field in BookInfo.FIELDS:
        if field.validator == WLURI:
            XmlUpdater.fixes_elements('.//' + field.uri)(fix_wluri)

    @XmlUpdater.fixes_elements(".//" + RDFNS("Description"))
    def fix_rdfabout(elem, change, verbose):
        correct_about = change.tree.book.correct_about()
        attr_name = RDFNS("about")
        current_about = elem.get(attr_name)
        if current_about != correct_about:
            if verbose:
                print("Changing rdf:about from %s to %s" % (
                        current_about, correct_about
                    ))
            elem.set(attr_name, correct_about)
            return True


class Command(XmlUpdaterCommand):
    updater = FixDC
    help = 'Fixes obvious errors in DC: rdf:about and WLURI format.'
