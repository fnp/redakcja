from django.db import models
from django.utils.translation import ugettext_lazy as _


class ButtonGroup(models.Model):
    name = models.CharField(max_length = 32)
    slug = models.SlugField()
    position = models.IntegerField(default = 0)

    class Meta:
        ordering = ('position', 'name',)
        verbose_name, verbose_name_plural = _('button group'), _('button groups')

    def __unicode__(self):
        return self.name

    def to_dict(self, with_buttons = False):
        d = {'name': self.name, 'position': self.position}

        if with_buttons:
            d['buttons'] = [ b.to_dict() for b in self.button_set.all() ]

        return d

#class ButtonGroupManager(models.Manager):
#
#    def with_buttons(self):
#        from django.db import connection
#        cursor = connection.cursor()
#        cursor.execute("""
#            SELECT g.name, g.slug, CONCAT(b.slug),
#            FROM toolbar_buttongroup as g LEFT JOIN toolbar_button as b
#
#            WHERE p.id = r.poll_id
#            GROUP BY 1, 2, 3
#            ORDER BY 3 DESC""")
#        result_list = []
#        for row in cursor.fetchall():
#            p = self.model(id=row[0], question=row[1], poll_date=row[2])
#            p.num_responses = row[3]
#            result_list.append(p)
#        return result_list

class Button(models.Model):
    label = models.CharField(max_length = 32)
    slug = models.SlugField(unique = True) #unused

    # behaviour
    params = models.TextField(default = '[]') # TODO: should be a JSON field
    scriptlet = models.ForeignKey('Scriptlet', null = True, blank = True)
    link = models.CharField(max_length = 256, blank = True, default = '')

    # ui related stuff
    key = models.CharField(blank = True, max_length = 1)
    key_mod = models.PositiveIntegerField(blank = True, default = 1)
    tooltip = models.CharField(blank = True, max_length = 120)

    # Why the button is restricted to have the same position in each group ?
    # position = models.IntegerField(default=0)   
    group = models.ManyToManyField(ButtonGroup)

    class Meta:
        ordering = ('slug',)
        verbose_name, verbose_name_plural = _('button'), _('buttons')

    @property
    def hotkey_code(self):
        return ord(self.key.upper()) | (self.key_mod << 8)

    @property
    def hotkey_name(self):
        if not self.key:
            return ''

        mods = []
        if self.key_mod & 0x01: mods.append('Alt')
        if self.key_mod & 0x02: mods.append('Ctrl')
        if self.key_mod & 0x04: mods.append('Shift')
        mods.append(str(self.key))
        return '[' + '+'.join(mods) + ']'

    @property
    def full_tooltip(self):
        return self.tooltip + (' ' + self.hotkey_name if self.key else '')

    def to_dict(self):
        return {
            'label': self.label,
            'tooltip': (self.tooltip or '') + self.hotkey_name(),
            'key': self.key,
            'key_mod': self.key_mod,
            'params': self.params,
            'scriptlet_id': self.scriptlet_id
        }

    def __unicode__(self):
        return self.label

class Scriptlet(models.Model):
    name = models.CharField(max_length = 64, primary_key = True)
    code = models.TextField()

    # TODO: add this later and remap code property to this
    # code_min = models.TextField()

    def __unicode__(self):
        return _(u'javascript') + u':' + self.name
