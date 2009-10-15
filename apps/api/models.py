from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PartCache(models.Model):
    document_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=64, blank=True)    
    part_id = models.CharField(max_length=255)

    @classmethod
    def update_cache(me, docid, userid, old, new):
        old = set(old)
        new = set(new)

        related = me.objects.filter(user_id=userid, document_id=docid)

        missing = old.difference(new)
        related.filter(part_id__in=missing).delete()

        created = new.difference(old)

        for part in created:
            me.objects.create(user_id=userid, document_id=docid, part_id=part)


class PullRequest(models.Model):
    REQUEST_STATUSES = {
        "N": "New",
        "E": "Edited/Conflicting",
        "R": "Rejected",
        "A": "Accepted & merged",
    }

    comitter = models.ForeignKey(User) # the user who request the pull
    comment = models.TextField() # addtional comments to the request

    timestamp = models.DateTimeField(auto_now_add=True)

    # document to merge
    document = models.CharField(max_length=255)

    # revision to be merged into the main branch
    source_revision = models.CharField(max_length=40, unique=True)
    target_revision = models.CharField(max_length=40)

    # current status
    status = models.CharField(max_length=1, choices=REQUEST_STATUSES.items())

    # comment to the status change of request (if applicable)
    response_comment = models.TextField(blank=True)

    # revision number in which the changes were merged (if any)
    merged_revision = models.CharField(max_length=40, blank=True, null=True)
    merge_timestamp = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        return unicode(self.comitter) + u':' + self.document


    class Meta:
        permissions = (           
            ("pullrequest.can_view", "Can view pull request's contents."),
        )


# This is actually an abstract Model, but if we declare
# it as so Django ignores the permissions :(
class Document(models.Model):
    class Meta:
        permissions = (
            ("document.can_share", "Can share documents without pull requests."),
            ("document.can_view_other", "Can view other's documents."),
        )    