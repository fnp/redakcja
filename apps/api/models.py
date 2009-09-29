from django.db import models

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


            
        

        

            
        
        
        