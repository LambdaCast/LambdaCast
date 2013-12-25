from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import *

from portal.models import Video, Channel, Collection

from django.utils.feedgenerator import Rss201rev2Feed

import lambdaproject.settings as settings

import markdown

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
        

    def add_item_elements(self,  handler, item):
        super(iTunesFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'itunes:summary',item['summary'])
        handler.addQuickElement(u'itunes:duration',item['duration'])
        handler.addQuickElement(u'itunes:explicit',item['explicit'])

class MainFeed(Feed):
    feed_type = iTunesFeed
    description = ''
    subtitle = description
    author_name = str(settings.AUTHOR_NAME)

    def items(self):
        return Video.objects.filter(published=True).exclude(mp3URL='', oggURL='', webmURL='', mp4URL='').order_by('-created')

    def feed_extra_kwargs(self, obj):
        extra = {}
        extra['iTunes_name'] = str(settings.AUTHOR_NAME)
        extra['iTunes_email'] = str(settings.CONTACT_EMAIL)
        extra['iTunes_image_url'] = str(settings.LOGO_URL)
        extra['iTunes_explicit'] = 'no'
        return extra

    def item_extra_kwargs(self, item):
        extra = {}
        extra['duration'] = str(item.duration)
        extra['summary'] = str(item.description)
        extra['explicit'] = 'no'
        return extra

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        if self.fileformat == 'mp3':
            return item.mp3URL
        elif self.fileformat == 'mp4':
            return item.mp4URL
        elif self.fileformat == 'ogg':
            return item.oggURL
        elif self.fileformat == 'webm':
            return item.webmURL
        else:
            return Exception

    def item_link(self, item):
        if self.fileformat == 'mp3':
            return item.mp3URL
        elif self.fileformat == 'mp4':
            return item.mp4URL
        elif self.fileformat == 'ogg':
            return item.oggURL
        elif self.fileformat == 'webm':
            return item.webmURL
        else:
            return Exception

    def item_enclosure_length(self, item):
        if self.fileformat == 'mp3':
            return item.mp3Size
        elif self.fileformat == 'mp4':
           return item.mp4Size
        elif self.fileformat == 'ogg':
            return item.oggSize
        elif self.fileformat == 'webm':
            return item.webmSize
        else:
            return Exception

    def item_pubdate(self, item):
        return item.created

    def item_enclosure_length(self, item):
        return item.duration

    def item_enclosure_mime_type(self):
        if self.fileformat == 'mp4' or self.fileformat == 'webm':
            return 'video/%s' % self.fileformat
        else:
            return 'audio/%s' % self.fileformat


class LatestVideos(MainFeed):
    title = _("Latest Episodes")
    link = "/"
    description = _(u"The newest episodes from your beloved podcast")
  
    def get_object(self, request, fileformat):
        self.fileformat = fileformat


class TorrentFeed(Feed):
    title = _(u"TorrentFeed")
    link = "/"
    description = _("Torrent files from your beloved podcast")
    item_enclosure_mime_type = "application/x-bittorrent"
	
    def items(self):
        return Video.objects.filter(published=True, torrentDone=True).exclude(torrentURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')
        
    def item_enclosure_url(self, item):
    	return item.torrentURL
    	
    def item_enclosure_length(self, item):
    	return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')
    	
    def item_pubdate(self, item):
    	return item.created

class ChannelFeed(MainFeed):
    ''' This class (like the next one) gives the feeds for channels"'''
    def get_object(self, request, channel_slug, fileformat):
        self.fileformat = fileformat
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description
    
    def items(self, obj):
        return Video.objects.filter(encodingDone=True, published=True, channel=obj).exclude(mp3URL='', oggURL='', webmURL='', mp4URL='').order_by('-created')


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
        return Video.objects.filter(published=True, channel=obj, torrentDone=True ).exclude(torrentURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.torrentURL

    def item_enclosure_length(self, item):
        return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')

    def item_pubdate(self, item):
        return item.created

class CollectionFeed(MainFeed):
    def get_object(self, request, collection_slug, fileformat):
        self.fileformat = fileformat
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"Videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return obj.videos.filter(encodingDone=True, published=True).exclude(mp3URL='', oggURL='', webmURL='', mp4URL='').order_by('-created')


class CollectionFeedTorrent(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"Torrents for videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "application/x-bittorrent"

    def items(self, obj):
        return obj.videos.filter(torrentDone=True, published=True).exclude(torrentURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.torrentURL

    def item_enclosure_length(self, item):
        return os.path.getsize(settings.BITTORRENT_FILES_DIR + item.slug + '.torrent')

    def item_pubdate(self, item):
        return item.created
