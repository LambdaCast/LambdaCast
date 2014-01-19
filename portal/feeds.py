from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from portal.models import Video, Channel, Collection, Comment

import lambdaproject.settings as settings

import markdown

import os

class LatestMP4Videos(Feed):
    ''' This class (like the following) are handling the feed requests from urls.py.
    TODO:
    Better handling: We sould only use one Feed class and get the desired format with GET
    Dynamic Title for the Feed'''
    title = _(u"LambdaCast Latest Videos")
    link = "/"
    description = _(u"The newest media from LambdaCast")
    item_enclosure_mime_type = "video/mp4"
	
    def items(self):
        return Video.objects.filter(published=True).exclude(mp4URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')
        
    def item_enclosure_url(self, item):
    	return item.mp4URL
    	
    def item_enclosure_length(self, item):
    	return item.mp4Size
    	
    def item_pubdate(self, item):
    	return item.created
    	
class LatestWEBMVideos(Feed):
    title = _(u"LambdaCast Latest Videos")
    link = "/"
    description = _(u"The newest media from LambdaCast")
    item_enclosure_mime_type = "video/webm"
	
    def items(self):
        return Video.objects.filter(published=True).exclude(webmURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')
        
    def item_enclosure_url(self, item):
    	return item.webmURL
    	
    def item_enclosure_length(self, item):
    	return item.webmSize
    	
    def item_pubdate(self, item):
    	return item.created
    	
class LatestMP3Audio(Feed):
    title = _(u"LambdaCast Latest Audio Files")
    link = "/"
    description = _(u"The newest media from LambdaCast")
    item_enclosure_mime_type = "audio/mp3"
	
    def items(self):
        return Video.objects.filter(published=True).exclude(mp3URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')
        
    def item_enclosure_url(self, item):
    	return item.mp3URL
    	
    def item_enclosure_length(self, item):
    	return item.mp3Size
    	
    def item_pubdate(self, item):
    	return item.created
    	
class LatestOGGAudio(Feed):
    title = _(u"LambdaCast Latest Audio Files")
    link = "/"
    description = _(u"The newest media from LambdaCast")
    item_enclosure_mime_type = "audio/ogg"
	
    def items(self):
        return Video.objects.filter(published=True).exclude(oggURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')
        
    def item_enclosure_url(self, item):
    	return item.oggURL
    	
    def item_enclosure_length(self, item):
    	return item.oggSize
    	
    def item_pubdate(self, item):
    	return item.created

class TorrentFeed(Feed):
    title = _(u"LambdaCast TorrentFeed")
    link = "/"
    description = _("Torrent files from LambdaCast")
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

class ChannelFeedMP4(Feed):
    ''' This class (like the next one) gives the feeds for channels"'''
    
    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "video/mp4"
    author_name = settings.AUTHOR_NAME

    def items(self, obj):
        return Video.objects.filter(encodingDone=True, published=True, channel=obj ).exclude(mp4URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.mp4URL

    def item_enclosure_length(self, item):
        return item.mp4Size

    def item_pubdate(self, item):
        return item.created

class ChannelFeedWEBM(Feed):

    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "video/webm"
    author_name = settings.AUTHOR_NAME

    def items(self, obj):
        return Video.objects.filter(encodingDone=True, published=True, channel=obj ).exclude(webmURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.webmURL

    def item_enclosure_length(self, item):
        return item.webmSize

    def item_pubdate(self, item):
        return item.created

class ChannelFeedMP3(Feed):

    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "audio/mp3"
    author_name = settings.AUTHOR_NAME

    def items(self, obj):
        return Video.objects.filter(encodingDone=True, published=True, channel=obj ).exclude(mp3URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.mp3URL

    def item_enclosure_length(self, item):
        return item.mp3Size

    def item_pubdate(self, item):
        return item.created

class ChannelFeedOGG(Feed):

    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return "%s: %s" % (settings.AUTHOR_NAME, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "audio/ogg"
    author_name = settings.AUTHOR_NAME

    def items(self, obj):
        return Video.objects.filter(encodingDone=True, published=True, channel=obj ).exclude(oggURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.oggURL

    def item_enclosure_length(self, item):
        return item.oggSize

    def item_pubdate(self, item):
        return item.created

class ChannelFeedTorrent(Feed):

    def get_object(self, request, channel_slug):
        return get_object_or_404(Channel, slug=channel_slug)

    def title(self, obj):
        return _(u"LambdaCast: Torrents for Channel %s") % obj.name

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

class CollectionFeedMP4(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"LambdaCast: Videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "video/mp4"

    def items(self, obj):
        return obj.videos.filter(encodingDone=True, published=True).exclude(mp4URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.mp4URL

    def item_enclosure_length(self, item):
        return item.mp4Size

    def item_pubdate(self, item):
        return item.created

class CollectionFeedWEBM(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"LambdaCast: Videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "video/webm"

    def items(self, obj):
        return obj.videos.filter(encodingDone=True, published=True).exclude(webmURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.webmURL

    def item_enclosure_length(self, item):
        return item.webmSize

    def item_pubdate(self, item):
        return item.created

class CollectionFeedMP3(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"LambdaCast: Videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "audio/mp3"

    def items(self, obj):
        return obj.videos.filter(encodingDone=True, published=True).exclude(mp3URL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.mp3URL

    def item_enclosure_length(self, item):
        return item.mp3Size

    def item_pubdate(self, item):
        return item.created

class CollectionFeedOGG(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"LambdaCast: Videos in Collection %s") % obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return  obj.description

    item_enclosure_mime_type = "audio/ogg"

    def items(self, obj):
        return obj.videos.filter(encodingDone=True, published=True).exclude(oggURL='').order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return markdown.markdown(item.description, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_enclosure_url(self, item):
        return item.oggURL

    def item_enclosure_length(self, item):
        return item.oggSize

    def item_pubdate(self, item):
        return item.created

class CollectionFeedTorrent(Feed):

    def get_object(self, request, collection_slug):
        return get_object_or_404(Collection, slug=collection_slug)

    def title(self, obj):
        return _(u"LambdaCast: Videos in Collection %s") % obj.title

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


class CommentsFeed(Feed):
    title = _(u"Latest comments from your podcast portal")
    link = "/"
    description = _(u"The latest comments from your podcast portal")

    def items(self):
        return Comment.objects.filter(moderated=True).order_by('-created')

    def item_title(self, item):
        title = _(u"New comment to %s") % item.video.title
        return title

    def item_description(self, item):
        return markdown.markdown(item.comment, safe_mode='replace', html_replacement_text='[HTML_REMOVED]')

    def item_pubdate(self, item):
        return item.created
