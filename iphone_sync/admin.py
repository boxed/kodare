from django.contrib import admin
from kodare.iphone_sync.models import *

admin.site.register(Context)
admin.site.register(Entity)
admin.site.register(ManagedObject)
#admin.site.register(SyncLog)