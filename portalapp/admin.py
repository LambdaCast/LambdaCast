from portalapp.models import Video
from portalapp.models import Comment
from portalapp.models import Channel
from portalapp.models import Hotfolder
from portalapp.models import Collection

from django.contrib import admin

def make_published(modeladmin, request, queryset):
    queryset.update(published=True)
make_published.short_description = "Markierte Videos veroeffentlichen"

def make_torrent_done(modeladmin, request, queryset):
    queryset.update(torrentDone=True)
make_torrent_done.short_description = "Markierte Videos also mit Torrent markieren"

class VideoAdmin (admin.ModelAdmin):
    list_display = ['title','published','encodingDone', 'channel' ,'date']
    ordering = ['-date','-created']
    actions = [make_published,make_torrent_done]
    list_filter = ('kind', 'published', 'channel')
    fieldsets = (
        (None, {
            'fields': ('title', 'date', 'description', 'channel', 'linkURL', 'tags','published')
        }),
        ('Erweiterte Optionen', {
            'classes': ('collapse',),
            'fields': ('kind','user','torrentURL','mp4URL','webmURL','mp3URL','oggURL','videoThumbURL','audioThumbURL','duration','autoPublish','encodingDone','torrentDone')
        }),
    )
admin.site.register(Video,VideoAdmin)

def make_moderated(modeladmin,request, queryset):
    queryset.update(moderated=True)
make_moderated.short_description = "Markierte Kommentare zulassen"

class CommentAdmin (admin.ModelAdmin):
    list_display = ['comment','video','created','name','ip','moderated']
    ordering = ['-created']
    actions = [make_moderated]

admin.site.register(Comment,CommentAdmin)

class ChannelAdmin (admin.ModelAdmin):
    list_display = ['name','description','featured']
    ordering = ['-created']

admin.site.register(Channel,ChannelAdmin)

class HotfolderAdmin (admin.ModelAdmin):
    list_display = ['folderName','activated','autoPublish','kind','channel']
    ordering = ['-created']

admin.site.register(Hotfolder,HotfolderAdmin)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','date','channel']
    ordering = ['-date','-created']

admin.site.register(Collection,CollectionAdmin)
