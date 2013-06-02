from django.contrib import admin
from kodare.blog.models import *

class EntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    
admin.site.register(Entry, EntryAdmin)