from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

class Context(models.Model): 
    # normally this would be something like the app and then the device/username/whatever
    # [[NSBundle mainBundle] bundleIdentifier]
    name = models.CharField(blank=True, max_length=500, db_index=True)
    email = models.EmailField(db_index=True)
    code = models.CharField(db_index=True, max_length=40, blank=True)
    def __unicode__(self):
        return self.name
        
class Entity(models.Model):
    name = models.CharField(blank=False, max_length=100, db_index=True)
    def __unicode__(self):
        return self.name

class ManagedObject(models.Model):
    context = models.ForeignKey(Context)
    entity = models.ForeignKey(Entity)
    objectURI = models.CharField(blank=True, max_length=500, db_index=True)
    data = models.TextField(blank=True)
    created = models.DateTimeField(blank=True, default=datetime.datetime.now)
    modified = models.DateTimeField(blank=True, default=datetime.datetime.now)
    def __unicode__(self):
        return self.objectURI
    
    @property    
    def decoded_data(self):
        import urllib
        if not hasattr(self, '_decoded_data'):
            self._decoded_data = {}
            for keyvalue in self.data.split('&'):
                key, value = keyvalue.split(':')
                self._decoded_data[urllib.url2pathname(key)] = urllib.url2pathname(value)
        return self._decoded_data

# class SyncLog(models.Model): # server side changes
#     context = models.ForeignKey(Context)
#     entity = models.ForeignKey(Entity)
#     objectURI = models.CharField(blank=True, max_length=500)
#     operation = models.CharField(blank=True, max_length=100)
#     synched = models.BooleanField(default=True, db_index=True)
#     time = models.DateTimeField(blank=True, default=datetime.datetime.now)
#     def __unicode__(self):
#         return u'%s %s' % (self.command, self.objectURI)
