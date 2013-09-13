from django.utils.translation import ugettext_lazy as _
from django.db import models

from autoslug import AutoSlugField

import lambdaproject.settings as settings

import datetime



class Page(models.Model):
    DISPLAY_CONTENT = (
        ('link', _(u'link to another website')),
        ('body', _(u'display the content of body'))
    )
    ICONS = (
        ('glass', 'icon-glass'),
        ('music', 'icon-music'),
        ('search', 'icon-search'),
        ('envelope', 'icon-envelope'),
        ('heart', 'icon-heart'),
        ('star', 'icon-star'),
        ('star-empty', 'icon-star-empty'),
        ('user', 'icon-user'),
        ('film', 'icon-film'),
        ('th-large', 'icon-th-large'),
        ('th', 'icon-th'),
        ('th-list', 'icon-th-list'),
        ('ok', 'icon-ok'),
        ('remove', 'icon-remove'),
        ('zoom-in', 'icon-zoom-in'),
        ('zoom-out', 'icon-zoom-out'),
        ('off', 'icon-off'),
        ('signal', 'icon-signal'),
        ('cog', 'icon-cog'),
        ('trash', 'icon-trash'),
        ('home', 'icon-home'),
        ('file', 'icon-file'),
        ('time', 'icon-time'),
        ('road', 'icon-road'),
        ('download-alt', 'icon-download-alt'),
        ('download', 'icon-download'),
        ('upload', 'icon-upload'),
        ('inbox', 'icon-inbox'),
        ('play-circle', 'icon-play-circle'),
        ('repeat', 'icon-repeat'),
        ('refresh', 'icon-refresh'),
        ('list-alt', 'icon-list-alt'),
        ('lock', 'icon-lock'),
        ('flag', 'icon-flag'),
        ('headphones', 'icon-headphones'),
        ('volume-off', 'icon-volume-off'),
        ('volume-down', 'icon-volume-down'),
        ('volume-up', 'icon-volume-up'),
        ('qrcode', 'icon-qrcode'),
        ('barcode', 'icon-barcode'),
        ('tag', 'icon-tag'),
        ('tags', 'icon-tags'),
        ('book', 'icon-book'),
        ('bookmark', 'icon-bookmark'),
        ('print', 'icon-print'),
        ('camera', 'icon-camera'),
        ('font', 'icon-font'),
        ('bold', 'icon-bold'),
        ('italic', 'icon-italic'),
        ('text-height', 'icon-text-height'),
        ('text-width', 'icon-text-width'),
        ('align-left', 'icon-align-left'),
        ('align-center', 'icon-align-center'),
        ('align-right', 'icon-align-right'),
        ('align-justify', 'icon-align-justify'),
        ('list', 'icon-list'),
        ('indent-left', 'icon-indent-left'),
        ('indent-right', 'icon-indent-right'),
        ('facetime-video', 'icon-facetime-video'),
        ('picture', 'icon-picture'),
        ('pencil', 'icon-pencil'),
        ('map-marker', 'icon-map-marker'),
        ('adjust', 'icon-adjust'),
        ('tint', 'icon-tint'),
        ('edit', 'icon-edit'),
        ('share', 'icon-share'),
        ('check', 'icon-check'),
        ('move', 'icon-move'),
        ('step-backward', 'icon-step-backward'),
        ('fast-backward', 'icon-fast-backward'),
        ('backward', 'icon-backward'),
        ('play', 'icon-play'),
        ('pause', 'icon-pause'),
        ('stop', 'icon-stop'),
        ('forward', 'icon-forward'),
        ('fast-forward', 'icon-fast-forward'),
        ('step-forward', 'icon-step-forward'),
        ('eject', 'icon-eject'),
        ('chevron-left', 'icon-chevron-left'),
        ('chevron-right', 'icon-chevron-right'),
        ('plus-sign', 'icon-plus-sign'),
        ('minus-sign', 'icon-minus-sign'),
        ('remove-sign', 'icon-remove-sign'),
        ('ok-sign', 'icon-ok-sign'),
        ('question-sign', 'icon-question-sign'),
        ('info-sign', 'icon-info-sign'),
        ('screenshot', 'icon-screenshot'),
        ('remove-circle', 'icon-remove-circle'),
        ('ok-circle', 'icon-ok-circle'),
        ('ban-circle', 'icon-ban-circle'),
        ('arrow-left', 'icon-arrow-left'),
        ('arrow-right', 'icon-arrow-right'),
        ('arrow-up', 'icon-arrow-up'),
        ('arrow-down', 'icon-arrow-down'),
        ('share-alt', 'icon-share-alt'),
        ('resize-full', 'icon-resize-full'),
        ('resize-small', 'icon-resize-small'),
        ('plus', 'icon-plus'),
        ('minus', 'icon-minus'),
        ('asterisk', 'icon-asterisk'),
        ('exclamation-sign', 'icon-exclamation-sign'),
        ('gift', 'icon-gift'),
        ('leaf', 'icon-leaf'),
        ('fire', 'icon-fire'),
        ('eye-open', 'icon-eye-open'),
        ('eye-close', 'icon-eye-close'),
        ('warning-sign', 'icon-warning-sign'),
        ('plane', 'icon-plane'),
        ('calendar', 'icon-calendar'),
        ('random', 'icon-random'),
        ('comment', 'icon-comment'),
        ('magnet', 'icon-magnet'),
        ('chevron-up', 'icon-chevron-up'),
        ('chevron-down', 'icon-chevron-down'),
        ('retweet', 'icon-retweet'),
        ('shopping-cart', 'icon-shopping-cart'),
        ('folder-close', 'icon-folder-close'),
        ('folder-open', 'icon-folder-open'),
        ('resize-vertical', 'icon-resize-vertical'),
        ('resize-horizontal', 'icon-resize-horizontal'),
        ('hdd', 'icon-hdd'),
        ('bullhorn', 'icon-bullhorn'),
        ('bell', 'icon-bell'),
        ('certificate', 'icon-certificate'),
        ('thumbs-up', 'icon-thumbs-up'),
        ('thumbs-down', 'icon-thumbs-down'),
        ('hand-right', 'icon-hand-right'),
        ('hand-left', 'icon-hand-left'),
        ('hand-up', 'icon-hand-up'),
        ('hand-down', 'icon-hand-down'),
        ('circle-arrow-right', 'icon-circle-arrow-right'),
        ('circle-arrow-left', 'icon-circle-arrow-left'),
        ('circle-arrow-up', 'icon-circle-arrow-up'),
        ('circle-arrow-down', 'icon-circle-arrow-down'),
        ('globe', 'icon-globe'),
        ('wrench', 'icon-wrench'),
        ('tasks', 'icon-tasks'),
        ('filter', 'icon-filter'),
        ('briefcase', 'icon-briefcase'),
        ('fullscreen', 'icon-fullscreen'),
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
    orderid = models.DecimalField(verbose_name=_(u"Order"),unique=True,max_digits=2,decimal_places=0,help_text=_(u"Set the order of the menu items with smallest number first"))
    
    def __unicode__(self):
        return self.title
