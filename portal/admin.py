from portal.models import MediaItem, MediaFile, Comment, Channel, Hotfolder, Collection, Submittal

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from django import forms
from django.forms.widgets import Select

class MediaItemForm(forms.ModelForm):
    class Meta:
        widgets = {
            'license': Select(attrs={'class': 'vLargeTextField'}),
        }

def make_published(modeladmin, request, queryset):
    queryset.update(published=True)
make_published.short_description = _(u"Publish marked media")

def make_torrent_done(modeladmin, request, queryset):
    queryset.update(torrentDone=True)
make_torrent_done.short_description = _(u"Marked media all get a torrent")

class MediaFileInline(admin.TabularInline):
    model = MediaFile
    extra = 0
    fieldsets = (
        (None, {
            'fields': ('title', 'url', 'file_format', 'media_item')
        }),
    )

class MediaItemAdmin (admin.ModelAdmin):
    form = MediaItemForm
    list_display = ['title','published','encodingDone', 'channel' ,'date']
    ordering = ['-date','-created']
    actions = [make_published,make_torrent_done]
    list_filter = ('published', 'channel')
    fieldsets = (
        (None, {
            'fields': ('title', 'date', 'description', 'channel', 'license', 'linkURL', 'tags', 'published')
        }),
        (_(u'Advanced options'), {
            'classes': ('collapse',),
            'fields': ('user','torrentURL','videoThumbURL','audioThumbURL','duration','autoPublish','encodingDone','torrentDone')
        }),
    )
    inlines = [
        MediaFileInline,
    ]
admin.site.register(MediaItem,MediaItemAdmin)

def make_moderated(modeladmin,request, queryset):
    queryset.update(moderated=True)
make_moderated.short_description = _(u"Moderate marked comments")

class CommentAdmin (admin.ModelAdmin):
    list_display = ['comment','item','created','name','ip','moderated']
    ordering = ['-created']
    actions = [make_moderated]

admin.site.register(Comment,CommentAdmin)

class ChannelAdmin (admin.ModelAdmin):
    list_display = ['name','description','featured']
    ordering = ['-created']

admin.site.register(Channel,ChannelAdmin)

class HotfolderAdmin (admin.ModelAdmin):
    list_display = ['folderName','activated','autoPublish','channel']
    ordering = ['-created']

admin.site.register(Hotfolder,HotfolderAdmin)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','date','channel']
    ordering = ['-date','-created']

admin.site.register(Collection,CollectionAdmin)

class SubmittalAdmin(admin.ModelAdmin):
    list_display = ['title','description']

admin.site.register(Submittal,SubmittalAdmin)
