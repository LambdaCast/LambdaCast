from django.utils.translation import ugettext_lazy as _
from django.db import models

from autoslug import AutoSlugField

import lambdaproject.settings as settings

import datetime



class Page(models.Model):
    DISPLAY_CONTENT = (
        (_(u'link'), _(u'link to another website')),
        (_(u'body'), _(u'display the content of body'))
    )
    ICONS = (
        ('icon-glass', 'icon-glass'),
        ('icon-music', 'icon-music'),
        ('icon-search', 'icon-search'),
        ('icon-envelope', 'icon-envelope'),
        ('icon-heart', 'icon-heart'),
        ('icon-star', 'icon-star'),
        ('icon-star-empty', 'icon-star-empty'),
        ('icon-user', 'icon-user'),
        ('icon-film', 'icon-film'),
        ('icon-th-large', 'icon-th-large'),
        ('icon-th', 'icon-th'),
        ('icon-th-list', 'icon-th-list'),
        ('icon-ok', 'icon-ok'),
        ('icon-remove', 'icon-remove'),
        ('icon-zoom-in', 'icon-zoom-in'),
        ('icon-zoom-out', 'icon-zoom-out'),
        ('icon-off', 'icon-off'),
        ('icon-signal', 'icon-signal'),
        ('icon-cog', 'icon-cog'),
        ('icon-trash', 'icon-trash'),
        ('icon-home', 'icon-home'),
        ('icon-file', 'icon-file'),
        ('icon-time', 'icon-time'),
        ('icon-road', 'icon-road'),
        ('icon-download-alt', 'icon-download-alt'),
        ('icon-download', 'icon-download'),
        ('icon-upload', 'icon-upload'),
        ('icon-inbox', 'icon-inbox'),
        ('icon-play-circle', 'icon-play-circle'),
        ('icon-repeat', 'icon-repeat'),
        ('icon-refresh', 'icon-refresh'),
        ('icon-list-alt', 'icon-list-alt'),
        ('icon-lock', 'icon-lock'),
        ('icon-flag', 'icon-flag'),
        ('icon-headphones', 'icon-headphones'),
        ('icon-volume-off', 'icon-volume-off'),
        ('icon-volume-down', 'icon-volume-down'),
        ('icon-volume-up', 'icon-volume-up'),
        ('icon-qrcode', 'icon-qrcode'),
        ('icon-barcode', 'icon-barcode'),
        ('icon-tag', 'icon-tag'),
        ('icon-tags', 'icon-tags'),
        ('icon-book', 'icon-book'),
        ('icon-bookmark', 'icon-bookmark'),
        ('icon-print', 'icon-print'),
        ('icon-camera', 'icon-camera'),
        ('icon-font', 'icon-font'),
        ('icon-bold', 'icon-bold'),
        ('icon-italic', 'icon-italic'),
        ('icon-text-height', 'icon-text-height'),
        ('icon-text-width', 'icon-text-width'),
        ('icon-align-left', 'icon-align-left'),
        ('icon-align-center', 'icon-align-center'),
        ('icon-align-right', 'icon-align-right'),
        ('icon-align-justify', 'icon-align-justify'),
        ('icon-list', 'icon-list'),
        ('icon-indent-left', 'icon-indent-left'),
        ('icon-indent-right', 'icon-indent-right'),
        ('icon-facetime-video', 'icon-facetime-video'),
        ('icon-picture', 'icon-picture'),
        ('icon-pencil', 'icon-pencil'),
        ('icon-map-marker', 'icon-map-marker'),
        ('icon-adjust', 'icon-adjust'),
        ('icon-tint', 'icon-tint'),
        ('icon-edit', 'icon-edit'),
        ('icon-share', 'icon-share'),
        ('icon-check', 'icon-check'),
        ('icon-move', 'icon-move'),
        ('icon-step-backward', 'icon-step-backward'),
        ('icon-fast-backward', 'icon-fast-backward'),
        ('icon-backward', 'icon-backward'),
        ('icon-play', 'icon-play'),
        ('icon-pause', 'icon-pause'),
        ('icon-stop', 'icon-stop'),
        ('icon-forward', 'icon-forward'),
        ('icon-fast-forward', 'icon-fast-forward'),
        ('icon-step-forward', 'icon-step-forward'),
        ('icon-eject', 'icon-eject'),
        ('icon-chevron-left', 'icon-chevron-left'),
        ('icon-chevron-right', 'icon-chevron-right'),
        ('icon-plus-sign', 'icon-plus-sign'),
        ('icon-minus-sign', 'icon-minus-sign'),
        ('icon-remove-sign', 'icon-remove-sign'),
        ('icon-ok-sign', 'icon-ok-sign'),
        ('icon-question-sign', 'icon-question-sign'),
        ('icon-info-sign', 'icon-info-sign'),
        ('icon-screenshot', 'icon-screenshot'),
        ('icon-remove-circle', 'icon-remove-circle'),
        ('icon-ok-circle', 'icon-ok-circle'),
        ('icon-ban-circle', 'icon-ban-circle'),
        ('icon-arrow-left', 'icon-arrow-left'),
        ('icon-arrow-right', 'icon-arrow-right'),
        ('icon-arrow-up', 'icon-arrow-up'),
        ('icon-arrow-down', 'icon-arrow-down'),
        ('icon-share-alt', 'icon-share-alt'),
        ('icon-resize-full', 'icon-resize-full'),
        ('icon-resize-small', 'icon-resize-small'),
        ('icon-plus', 'icon-plus'),
        ('icon-minus', 'icon-minus'),
        ('icon-asterisk', 'icon-asterisk'),
        ('icon-exclamation-sign', 'icon-exclamation-sign'),
        ('icon-gift', 'icon-gift'),
        ('icon-leaf', 'icon-leaf'),
        ('icon-fire', 'icon-fire'),
        ('icon-eye-open', 'icon-eye-open'),
        ('icon-eye-close', 'icon-eye-close'),
        ('icon-warning-sign', 'icon-warning-sign'),
        ('icon-plane', 'icon-plane'),
        ('icon-calendar', 'icon-calendar'),
        ('icon-random', 'icon-random'),
        ('icon-comment', 'icon-comment'),
        ('icon-magnet', 'icon-magnet'),
        ('icon-chevron-up', 'icon-chevron-up'),
        ('icon-chevron-down', 'icon-chevron-down'),
        ('icon-retweet', 'icon-retweet'),
        ('icon-shopping-cart', 'icon-shopping-cart'),
        ('icon-folder-close', 'icon-folder-close'),
        ('icon-folder-open', 'icon-folder-open'),
        ('icon-resize-vertical', 'icon-resize-vertical'),
        ('icon-resize-horizontal', 'icon-resize-horizontal'),
        ('icon-hdd', 'icon-hdd'),
        ('icon-bullhorn', 'icon-bullhorn'),
        ('icon-bell', 'icon-bell'),
        ('icon-certificate', 'icon-certificate'),
        ('icon-thumbs-up', 'icon-thumbs-up'),
        ('icon-thumbs-down', 'icon-thumbs-down'),
        ('icon-hand-right', 'icon-hand-right'),
        ('icon-hand-left', 'icon-hand-left'),
        ('icon-hand-up', 'icon-hand-up'),
        ('icon-hand-down', 'icon-hand-down'),
        ('icon-circle-arrow-right', 'icon-circle-arrow-right'),
        ('icon-circle-arrow-left', 'icon-circle-arrow-left'),
        ('icon-circle-arrow-up', 'icon-circle-arrow-up'),
        ('icon-circle-arrow-down', 'icon-circle-arrow-down'),
        ('icon-globe', 'icon-globe'),
        ('icon-wrench', 'icon-wrench'),
        ('icon-tasks', 'icon-tasks'),
        ('icon-filter', 'icon-filter'),
        ('icon-briefcase', 'icon-briefcase'),
        ('icon-fullscreen', 'icon-fullscreen'),
    )
    
    DEFAULT_CONTENT = """
        <div class="row">
        <div class="span12">
        <dib class="row">
        <div class="span3">
        <h3>Title 1</h3>
        <p>This is sample content</p>
        </div>
        <div class="span3">
        <h3>Title 2</h3>
        <p>This is sample content</p>
        </div>
        <div class="span3">
        <h3>Title</h3>
        <p>This is sample content</p>
        </div>
        </div>
        </div>
        </div>
    """   

    activated = models.BooleanField(verbose_name=_(u"Activated"))
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    slug = AutoSlugField(verbose_name=_(u"Slug"),populate_from='title',unique=True,help_text=_(u"Is part of the URL that you can define"))
    title = models.CharField(_(u"Title"),max_length=200)
    description = models.CharField(_(u"Description"),blank=True,max_length=200)
    display = models.CharField(_(u"Display"),max_length=20,choices=DISPLAY_CONTENT,default='body')
    body = models.TextField(_(u"Body"),blank=True,max_length=10000,default=DEFAULT_CONTENT)
    icon = models.CharField(_(u"Icon"),blank=True,max_length=200,choices=ICONS)
    link = models.URLField(_(u"URL"),help_text=_(u"URL that links to an external website"),blank=True)
    orderid = models.DecimalField(verbose_name=_(u"Order"),unique=True,max_digits=2,decimal_places=1,help_text=_(u"Set the order of the menu items"))
    
    def __unicode__(self):
        return self.title
