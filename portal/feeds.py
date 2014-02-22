from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import *
from django.http import Http404

from string import upper

from portal.models import MediaItem, Channel, Collection, Comment, MediaFile
import models

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
    author_name = settings.AUTHOR_NAME

    def items(self):
        mediaitems = MediaItem.objects.filter(published=True).order_by('-created')
        returneditems = []
        for mediaitem in mediaitems:
            mediafiles = MediaFile.objects.filter(media_item=mediaitem,file_format=self.fileformat)
            for mediafile in mediafiles:
                returneditems.append(mediafile.media_item)
        return returneditems

    def feed_extra_kwargs(self, obj):
        extra = {}
        extra['iTunes_name'] = settings.AUTHOR_NAME
        extra['iTunes_email'] = settings.CONTACT_EMAIL
        extra['iTunes_image_url'] = settings.LOGO_URL
        extra['iTunes_explicit'] = 'no'
        return extra

    def item_extra_kwargs(self, item):
        extra = {}
        extra['duration'] = str(item.duration)
        extra['summary'] = self.item_description(item)
        extra['explicit'] = 'no'
        return extra

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        mediafiles = item.mediafiles()
        output_link = ""
        for mediafile in mediafiles:
            if mediafile.file_format == self.fileformat:
                output_link = mediafile.url
        return output_link

    def item_link(self, item):
        mediafiles = item.mediafiles()
        output_link = ""
        for mediafile in mediafiles:
            if mediafile.file_format == self.fileformat:
                output_link = mediafile.url
        return output_link

    def item_enclosure_length(self, item):
        mediafiles = item.mediafiles()
        output_length = 0
        for mediafile in mediafiles:
            if mediafile.file_format == self.fileformat:
                output_length = mediafile.size
        return output_length

    def item_pubdate(self, item):
        return item.created

    def item_enclosure_length(self, item):
        return item.duration

    def item_enclosure_mime_type(self, item):
        mediafiles = item.mediafiles()
        output_htmltype = ""
        for mediafile in mediafiles:
            if mediafile.file_format == self.fileformat:
                output_htmltype = mediafile.html_type()
        return output_htmltype

class LatestMedia(MainFeed):
    title = _("Latest Episodes")
    link = "/"
    description = _(u"The newest episodes from your beloved podcast")
  
    def get_object(self, request, fileformat):
        fileformat = upper(fileformat)
        self.fileformat = ""
        for list_row in models.FORMATINFO_LIST:
            if list_row[0] == fileformat:
                self.fileformat = fileformat

class TorrentFeed(Feed):
    title = _(u"TorrentFeed")
    link = "/"
    description = _("Torrent files from your beloved podcast")
    item_enclosure_mime_type = "application/x-bittorrent"
	
    def items(self):
        return MediaItem.objects.filter(published=True, torrentDone=True).exclude(torrentURL='').order_by('-created')

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
        fileformat = upper(fileformat)
        self.fileformat = ""
        for list_row in models.FORMATINFO_LIST:
            if list_row[0] == fileformat:
                self.fileformat = fileformat
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description
    
    def items(self, obj):
        return MediaItem.objects.filter(encodingDone=True, published=True, channel=obj).order_by('-created')


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
        return MediaItem.objects.filter(published=True, channel=obj, torrentDone=True ).exclude(torrentURL='').order_by('-created')

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
        fileformat = upper(fileformat)
        self.fileformat = ""
        for list_row in models.FORMATINFO_LIST:
            if list_row[0] == fileformat:
                self.fileformat = fileformat
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"Media Items in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return obj.items.filter(encodingDone=True, published=True).order_by('-created')


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
        return obj.items.filter(torrentDone=True, published=True).exclude(torrentURL='').order_by('-created')

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


class CommentsFeed(Feed):
    title = _(u"Latest comments from your podcast portal")
    link = "/"
    description = _(u"Latest comments from your podcast portal")

    def items(self):
        return Comment.objects.filter(moderated=True).order_by('-created')

    def item_title(self, comment):
        title = _(u"New comment to %s") % comment.item.title
        return title

    def item_description(self, item):
        return markdown.markdown(item.comment, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_pubdate(self, item):
        return item.created
