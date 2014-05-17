from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import Rss201rev2Feed
from django.http import Http404

from string import upper

from portal.models import MediaItem, Channel, Collection, Comment, MediaFile
from portal.media_formats import MEDIA_FORMATS

import lambdaproject.settings as settings

import markdown
from datetime import datetime, time
import os

class iTunesFeed(Rss201rev2Feed):
    def rss_attributes(self):
        return {u"version": self._version, u"xmlns:content": "http://purl.org/rss/1.0/modules/content", u"xmlns:sy": "http://purl.org/rss/1.0/modules/syndication/", u"xmlns:atom": u"http://www.w3.org/2005/Atom", u'xmlns:itunes': u'http://www.itunes.com/dtds/podcast-1.0.dtd'}

    def add_root_elements(self, handler):
        super(iTunesFeed, self).add_root_elements(handler)
        handler.addQuickElement(u'itunes:subtitle', self.feed['subtitle'])
        handler.addQuickElement(u'itunes:author', self.feed['author_name'])
        handler.addQuickElement(u'itunes:summary', self.feed['description'])
        handler.addQuickElement(u'itunes:explicit', self.feed['iTunes_explicit'])
        handler.startElement(u"itunes:owner", {})
        handler.addQuickElement(u'itunes:name', self.feed['iTunes_name'])
        handler.addQuickElement(u'itunes:email', self.feed['iTunes_email'])
        handler.endElement(u"itunes:owner")
        handler.addQuickElement(u'itunes:image', self.feed['iTunes_image_url'])
        handler.startElement('image', {})
        handler.addQuickElement('title', self.feed['title'])
        handler.addQuickElement('url', self.feed['iTunes_image_url'])
        handler.addQuickElement('link', self.feed['site_url'])
        handler.endElement('image')

    def add_item_elements(self,  handler, item):
        super(iTunesFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'itunes:summary',item['summary'])
        handler.addQuickElement(u'itunes:duration',item['duration'])
        handler.addQuickElement(u'itunes:explicit',item['explicit'])
        handler.addQuickElement(u'itunes:image', item['item_thumb'])

class MediaFeed(Feed):
    feed_type = iTunesFeed
    title = ''
    description = ''
    subtitle = description
    author_name = settings.AUTHOR_NAME

    def get_object(self, request, fileformat):
        fileformat = upper(fileformat)
        if fileformat not in MEDIA_FORMATS:
            raise Http404
        self.fileformat = fileformat

    def items(self):
        return MediaFile.objects.select_related('media_item').filter(media_item__published=True, file_format=self.fileformat).exclude(size__isnull=True).order_by('-media_item__date', '-media_item__created')

    def feed_extra_kwargs(self, obj):
        extra = {}
        extra['iTunes_name'] = settings.AUTHOR_NAME
        extra['iTunes_email'] = settings.CONTACT_EMAIL
        extra['iTunes_image_url'] = settings.LOGO_URL
        extra['iTunes_explicit'] = 'no'
        extra['site_url'] = settings.WEBSITE_URL
        return extra

    def item_extra_kwargs(self, item):
        extra = {}
        media_item = item.media_item
        extra['duration'] = str(media_item.duration)
        extra['summary'] = self.item_description(item)
        extra['explicit'] = 'no'
        if media_item.videoThumbURL:
            extra['item_thumb'] = media_item.videoThumbURL
        elif media_item.audioThumbURL:
            extra['item_thumb'] = media_item.audioThumbURL
        elif media_item.channel and media_item.channel.channelThumbURL:
            extra['item_thumb'] = media_item.channel.channelThumbURL
        else:
            extra['item_thumb'] = ''
        return extra

    def item_title(self, item):
        return item.media_item.title

    def item_description(self, item):
        return markdown.markdown(item.media_item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_link(self, item):
        return '/item/' + item.media_item.slug

    def item_pubdate(self, item):
        return datetime.combine(item.media_item.date, time())

    def item_enclosure_url(self, item):
        return item.url

    def item_enclosure_length(self, item):
        return item.size

    def item_enclosure_mime_type(self, item):
        return MEDIA_FORMATS[self.fileformat].mime_type

class LatestMedia(MediaFeed):
    title = _("%s - Latest Episodes")  % (settings.SITE_NAME)
    link = "/"
    description = _(u"The latest episodes from %s") % (settings.SITE_NAME)

    def items(self):
        return MediaFeed.items(self)[:15]

class TorrentFeed(Feed):
    title = _(u"%s - Latest Episodes (Torrent)") % (settings.SITE_NAME)
    link = "/"
    description = _("Torrent feed for the latest episodes from %s") % (settings.SITE_NAME)
    item_enclosure_mime_type = "application/x-bittorrent"

    def items(self):
        return MediaItem.objects.filter(published=True, torrentDone=True).exclude(torrentURL='').order_by('-date', '-created')[:15]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.torrentURL

    def item_enclosure_length(self, item):
        return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')

    def item_pubdate(self, item):
        return datetime.combine(item.media_item.date, time())

class ChannelFeed(MediaFeed):
    ''' This class (like the next one) gives the feeds for channels"'''
    def get_object(self, request, channel_slug, fileformat):
        MediaFeed.get_object(self, request, fileformat)
        return get_object_or_404(Channel, slug=channel_slug)

    def feed_extra_kwargs(self, obj):
        extra = {}
        extra['iTunes_name'] = settings.AUTHOR_NAME
        extra['iTunes_email'] = settings.CONTACT_EMAIL
        extra['iTunes_image_url'] = obj.channelThumbURL if not obj.channelThumbURL == '' else settings.LOGO_URL
        extra['iTunes_explicit'] = 'no'
        extra['site_url'] = settings.WEBSITE_URL
        return extra

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return MediaFeed.items(self).filter(media_item__channel=obj)

class ChannelFeedTorrent(Feed):

    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return _(u"Torrents for Channel %s") % obj.name

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "application/x-bittorrent"

    def items(self, obj):
        return MediaItem.objects.filter(published=True, channel=obj, torrentDone=True ).exclude(torrentURL='').order_by('-date', '-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.torrentURL

    def item_enclosure_length(self, item):
        return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')

    def item_pubdate(self, item):
        return datetime.combine(item.media_item.date, time())

class CollectionFeed(MediaFeed):
    def get_object(self, request, collection_slug, fileformat):
        MediaFeed.get_object(self, request, fileformat)
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"Media Items in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return MediaFeed.items(self).filter(media_item__in=obj.items.all())


class CollectionFeedTorrent(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"Torrents for items in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "application/x-bittorrent"

    def items(self, obj):
        return obj.items.filter(torrentDone=True, published=True).exclude(torrentURL='').order_by('-date', '-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.torrentURL

    def item_enclosure_length(self, item):
        return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')

    def item_pubdate(self, item):
        return datetime.combine(item.media_item.date, time())


class CommentsFeed(Feed):
    title = _(u"Latest comments from %s") % (settings.SITE_NAME)
    link = "/"
    description = _(u"Latest comments from %s") % (settings.SITE_NAME)

    def items(self):
        return Comment.objects.filter(moderated=True).order_by('-created')[:15]

    def item_title(self, comment):
        title = _(u"New comment to %s") % comment.item.title
        return title

    def item_description(self, item):
        return markdown.markdown(item.comment, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_pubdate(self, item):
        return item.created
