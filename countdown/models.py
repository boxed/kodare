from django.db import models
from django.utils.translation import ugettext as _

class Countdown(models.Model):
    title = models.CharField(max_length=1024, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    target_time = models.DateTimeField(verbose_name=_('Target time'))
    creator = models.EmailField(verbose_name=_('Your e-mail'), help_text=_('We will send you a link so you can edit the countdown later.'))
    password = models.CharField(max_length=100, editable=False)
    
    def __unicode__(self):
        return '%s - %s' % (self.title, self.creator)
        
    def get_absolute_url(self):
        return '/%s/' % self.id
    
class Notify(models.Model):
    countdown = models.ForeignKey(Countdown)
    email = models.EmailField(name=_('E-mail address'))