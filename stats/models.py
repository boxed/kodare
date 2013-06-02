from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=1024)
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.name
        
    def __repr__(self):
        return self.name
        
    def get_absolute_url(self):
        return '/%s/' % self.id
    
class Entry(models.Model):
    category = models.ForeignKey(Category, blank=True)
    value = models.TextField(blank=False)
    created = models.DateField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s: %s' % (self.category, self.value)
    