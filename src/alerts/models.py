from django.db import models
from django.dispatch import receiver
from dvcs.models import post_commit
from .rules import rules, rules_by_tag


class Alert(models.Model):
    book = models.ForeignKey('documents.Book', models.CASCADE)
    tag = models.CharField(max_length=32)
    comment = models.TextField(blank=True)

    def get_absolute_url(self):
        return self.book.get_absolute_url()

    @property
    def rule(self):
        return rules_by_tag[self.tag]

    @classmethod
    def validate_book(cls, book):
        cls.objects.filter(book=book).delete()
        try:
            wlbook = book.wldocument(publishable=False, librarian2=True)
        except Exception as e:
            cls.objects.create(book=book, tag='parse', comment=str(e))
            return

        try:
            meta = wlbook.meta
        except Exception as e:
            cls.objects.create(book=book, tag='meta', comment=str(e))
            return
        
        for rule in rules:
            if rule.check_meta(meta):
                print(rule.tag, book)
                cls.objects.create(book=book, tag=rule.tag)


@receiver(post_commit)
def validate_post_commit(sender, **kwargs):
    if hasattr(sender.tree, 'book'):
        Alert.validate_book(sender.tree.book)
