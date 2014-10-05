from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    title = models.CharField(max_length=1024, verbose_name=_('Title'))
    content = models.TextField(blank=True, verbose_name=_('Content'))
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation time'))
    slug = models.SlugField()
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('creation_time',)
        
    def get_absolute_url(self):
        return self.creation_time.strftime('/%Y/%b/%d/') + unicode(self.slug) + '/'        