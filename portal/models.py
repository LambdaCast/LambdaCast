# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_delete
from django.core.exceptions import ValidationError

from autoslug import AutoSlugField
from taggit.managers import TaggableManager

import lambdaproject.settings as settings

from portal.signals import get_remote_filesize, set_mediatype, purge_encoded_files

from pytranscode.ffmpeg import *
from pytranscode.runner import *
from ffmpeg_presets import *

import os
import subprocess
import re
import decimal
import urllib2
import datetime

from types import NoneType

from mutagen import File
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

from threading import Event

import markdown

from BitTornadoABC.btmakemetafile import calcsize, make_meta_file, ignore

LICENSE_CHOICES = (
    ("None", _(u"No License")),
    ("CC0", _(u"Public Domain/CC0")),
    ("CC-BY", _(u"CreativeCommons - Attribution")),
    ("CC-BY-NC", _(u"CreativeCommons - Attribution - NonCommercial")),
    ("CC-BY-NC-ND", _(u"CreativeCommons - Attribution - NonCommercial - NoDerivs")),
    ("CC-BY-ND", _(u"CreativeCommons - Attribution - NoDerivs")),
) 

KIND_CHOICES = (
    (0, _(u'Video-only')),
    (1, _(u'Audio-only')),
    (2, _(u'Audio and Video')),
)

FILE_FORMATS = (
    ("MP3", "mp3"),
    ("MP4", "mp4"),
    ("OGG", "ogg"),
    ("WEBM", "WebM"),
    ("OPUS", "Opus"),
)

FORMATINFO_LIST = (
#   format0     ending1  mediatype2  html_type3
    ("MP3",     ".mp3",  "audio",    "audio/mp3"),
    ("MP4",     ".mp4",  "video",    "video/mp4"),
    ("OGG",     ".ogg",  "audio",    "audio/ogg"),
    ("WEBM",    ".webm", "video",    "video/webm"),
    ("OPUS",    ".opus", "audio",    "application/ogg"),
)

class MediaFile(models.Model):
    ''' The model only for the media files '''
    title = models.CharField(_(u"Title"),max_length=200)
    url = models.URLField(_(u"URL to Transcoded File"),blank=True,verify_exists=False, help_text=_(u"Insert the link to the media file"))
    file_format = models.CharField(_(u"File Format"),max_length=20,choices=FILE_FORMATS,default="MP3",help_text=_(u"File format of the media file"),null=True)
    size = models.BigIntegerField(_(u"File Size in Bytes"),null=True,blank=True)
    media_item = models.ForeignKey('portal.MediaItem',help_text=_(u"Media Item the file is connected to"),null=True, blank=True)
    mediatype = models.CharField(_(u"Media Type"),max_length=20,help_text=_(u"File type of the media file"),null=True,blank=True)

    def file_ending(self):
        for list_row in FORMATINFO_LIST:
            if self.file_format == list_row[0]:
                return list_row[1]
    
    def html_type(self):
        for list_row in FORMATINFO_LIST:
            if self.file_format == list_row[0]:
                return list_row[3]

    def clean(self):
        for tuple in FORMATINFO_LIST:
            if self.file_format == tuple[0]:
                if not self.url.endswith(tuple[1]):
                    raise ValidationError(_(u"URL doesn't end with %s" % (tuple[1])))

class MediaItem(models.Model):
    ''' The model for our items. It uses slugs (with DjangoAutoSlug) and tags (with Taggit)
    everything else is quite standard. The sizes fields are used in the feeds to make enclosures
    possible. The videoThumbURL is the URL for Projekktor's "poster" and assemblyid is just a storage
    for the result we get back from transloadit so that we know which item just triggered the "encoding_done"
    view. Why are there URL fields and not file fields? Because you maybe want to use external storage
    (like Amazon S3) to store your files '''
    title = models.CharField(_(u"Title"),max_length=200)
    slug = AutoSlugField(populate_from='title',unique=True,verbose_name=_(u"Slug"),help_text=_(u"Slugs are parts of an URL that you can define"))
    date = models.DateField(_(u"Date"),help_text=_(u"Upload or record date"))
    description = models.TextField(_(u"Description"),blank=True,help_text=_(u"Insert a description to the media. You can use Markdown to add formatting"))
    user = models.ForeignKey(User,verbose_name=_(u"User"), blank=True, null=True, help_text=_(u"Shows which user made or uploaded the media item"))
    channel = models.ForeignKey('portal.Channel',blank=True,null=True,verbose_name=_(u"Channel"),help_text=_(u"Channels are used to order your media"))
    license = models.CharField(_(u"License"),max_length=200,choices=LICENSE_CHOICES,default="CC-BY",help_text=_(u"Rights the viewer/listener has"))
    linkURL = models.URLField(_(u"Link"),blank=True,verify_exists=False, help_text=_(u"Insert a link to a blog or website that relates to the media"))
    torrentURL = models.URLField(_(u"Torrent-URL"),blank=True,verify_exists=False,help_text=_(u"The URL to the torrent-file"))
    videoThumbURL = models.URLField(_(u"Video Thumb-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as thumbnail for the media list"))
    audioThumbURL = models.URLField(_(u"Audio Cover-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as cover for the media list"))
    duration = models.DecimalField(verbose_name=_(u"Duration"),null=True, max_digits=10, decimal_places=2, blank=True, help_text=_(u"The length of the media"))
    autoPublish = models.BooleanField(verbose_name=_(u"Auto-Publish"),default=True)
    published = models.BooleanField(verbose_name=_(u"Published"))
    encodingDone = models.BooleanField(verbose_name=_(u"Encoding done"))
    torrentDone = models.BooleanField(verbose_name=_(u"Torrent done"))
    assemblyid = models.CharField(_(u"Transloadit Result"),max_length=100,blank=True)
    tags = TaggableManager(_(u"Tags"),blank=True,help_text=_(u"Insert what the media item is about in short terms divided by commas"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    originalFile = models.FileField(_(u"File"),upload_to="raw/%Y/%m/%d/",max_length=2048)

    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/item/%s/" % self.slug
    def getClassName(self):
        return self.__class__.__name__

    def mediafiles(self):
        return MediaFile.objects.filter(media_item=self)
    
    def comments_number(self):
        return Comment.objects.filter(moderated=True, item=self.pk).count()  

    def markdown_free(self):
        md_free_desc = markdown.markdown(self.description)
        md_free_desc = md_free_desc.replace('</p>', ' | ').replace('</li>', ' | ').replace('<ul>', ' | ')
        md_free_desc = re.sub('</h\\d>', ' | ', md_free_desc)
        md_free_desc = re.sub('<[^<]+?>', '', md_free_desc)
        md_free_desc = re.sub('\\|(\\s+\\|)+', '|', md_free_desc)
        return md_free_desc

    def get_wp_code(self):
        downloads_audio = MediaFile.objects.filter(media_item=self,mediatype='audio')
        downloads_video = MediaFile.objects.filter(media_item=self, mediatype='video')

        wp_code = ""
        if downloads_video:
            wp_code = wp_code + '[video src="%s"]\n' % (downloads_video[0].url)
        if downloads_audio:
            wp_code = wp_code + '[audio src="%s"]\n' % (downloads_audio[0].url)
        wp_code = wp_code + '\nDownload: '
        for mediafile in downloads_video:
            wp_code = wp_code + '<a title="%s %s" href="%s" target="_blank">%s</a>, ' % (self.title,mediafile.file_ending(),mediafile.url,mediafile.file_ending())
        for mediafile in downloads_audio:
            wp_code = wp_code + '<a title="%s %s" href="%s" target="_blank">%s</a>, ' % (self.title,mediafile.file_ending(),mediafile.url,mediafile.file_ending())
        if self.description:
            wp_code = wp_code + '\n\n<!--more-->\n%s' % ((markdown.markdown(self.description)))
        return unicode(wp_code)

    def encode_media(self):
        ''' This is used to tell ffmpeg what to do '''
        path = self.originalFile.path
        outputdir = settings.ENCODING_OUTPUT_DIR + self.slug
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        outputdir = outputdir + '/'

        # Create the command line (MP3)
        logfile = outputdir + 'encoding_mp3_log.txt'
        outfile_mp3 = outputdir + self.slug + '.mp3'
        cl_mp3 = ffmpeg(path, outfile_mp3, logfile, NULL_VIDEO , MP3_AUDIO).build_command_line()

        # Create the command line (OGG)
        logfile = outputdir + 'encoding_ogg_log.txt'
        outfile_ogg = outputdir + self.slug + '.ogg'
        cl_ogg = ffmpeg(path, outfile_ogg, logfile, NULL_VIDEO, OGG_AUDIO).build_command_line()

        # Create the command line (OPUS)
        logfile = outputdir + 'encoding_opus_log.txt'
        outfile_opus = outputdir + self.slug + '.opus'

        mp3_url = settings.ENCODING_VIDEO_BASE_URL + self.slug +  '/' + self.slug + '.mp3'
        ogg_url = settings.ENCODING_VIDEO_BASE_URL + self.slug +  '/' + self.slug + '.ogg'
        opus_url = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + self.slug + '.opus'

        mediafile_mp3 = MediaFile.objects.create(title=self.slug+" mp3",url=mp3_url,file_format="MP3",media_item=self)
        mediafile_ogg = MediaFile.objects.create(title=self.slug+" ogg",url=ogg_url,file_format="OGG",media_item=self)
        mediafile_opus = MediaFile.objects.create(title=self.slug+" opus",url=opus_url,file_format="OPUS",media_item=self)

        outcode = subprocess.Popen(cl_mp3, shell=True)

        while outcode.poll() == None:
            pass

        if outcode.poll() == 0:
            mediafile_mp3.size = os.path.getsize(outfile_mp3)
            mediafile_mp3.save()
            self.duration = getLength(outfile_mp3)
        else:
            raise StandardError(_(u"Encoding MP3 Failed"))

        outcode = subprocess.Popen(cl_ogg, shell=True)

        while outcode.poll() == None:
            pass

        if outcode.poll() == 0:
            mediafile_ogg.size = os.path.getsize(outfile_ogg)
            mediafile_ogg.save()
        else:
            raise StandardError(_(u"Encoding OGG Failed"))

        outcode = subprocess.Popen(['ffmpeg -i "'+ path + '" -acodec libopus -ab 128k -ar 48000 -ac 2 ' + outfile_opus + ' 2> ' + logfile],shell=True)

        while outcode.poll() == None:
            pass

        if outcode.poll() == 0:
            mediafile_opus.size = os.path.getsize(outfile_opus)
            mediafile_opus.save()
        else:
            raise StandardError(_(u"Encoding OPUS Failed %s") % outcode.poll())

        # Get cover of mp3-file
        if path.endswith('.mp3') and self.audioThumbURL == "":
            audio_mp3 = MP3(path, ID3=ID3)
            try: 
                apic = audio_mp3.tags.getall('APIC')
                if apic:
                    cover_data = apic[0].data
                    cover_mimetype = apic[0].mime
                    filename = ''
                    if cover_mimetype == 'image/png':
                        filename = self.slug + '_cover.png'
                    elif cover_mimetype == 'image/jpg':
                        filename = self.slug + '_cover.jpg'
                    art_mp3 = open(outputdir + filename, 'w')
                    art_mp3.write(cover_data)
                    art_mp3.close()
                    self.audioThumbURL = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + filename
            except:
                pass

        self.encodingDone = True
        self.torrentDone = settings.USE_BITTORRENT
        if settings.USE_BITTORRENT:
            self.torrentURL = settings.BITTORRENT_FILES_BASE_URL + self.slug + '.torrent'
            
        self.published = self.autoPublish
        self.save()
        
    def create_bittorrent(self):
        ''' This is where the bittorrent files are created and transmission is controlled'''
        flag = Event()
        make_meta_file(str(self.originalFile.path),
            settings.BITTORRENT_TRACKER_ANNOUNCE_URL,
            params = {'target' : settings.BITTORRENT_FILES_DIR
                                            + self.slug + '.torrent',
             'piece_size_pow2' : 18,
             'announce_list': settings.BITTORRENT_TRACKER_BACKUP,
             'url_list' : str(self.originalFile.url)},
             flag = flag,
             progress_percent=0)
        self.torrentURL = settings.BITTORRENT_FILES_BASE_URL + self.slug + '.torrent'
        self.torrentDone = True
        self.published = self.autoPublish
        self.save()

    def get_license_link(self):
        if self.license == "CC0":
            return _(u"https://creativecommons.org/publicdomain/zero/1.0/")
        elif self.license == "CC-BY":
            return _(u"http://creativecommons.org/licenses/by/3.0/")
        elif self.license == "CC-BY-NC":
            return _(u"http://creativecommons.org/licenses/by-nc/3.0/")
        elif self.license == "CC-BY-NC-ND":
            return _(u"http://creativecommons.org/licenses/by-nc-nd/3.0/")
        elif self.license == "CC-BY-ND":
            return _(u"http://creativecommons.org/licenses/by-nd/3.0/")
        elif self.license == "None":
            return ""

class Comment(models.Model):
    ''' The model for our comments, please note that (right now) LambdaCast comments are moderated only'''
    name = models.CharField(_(u"Name"),max_length=30)
    ip = models.IPAddressField("IP",blank=True,null=True,help_text=_(u"The IP of the one who posted the comment"))
    moderated = models.BooleanField(verbose_name=_(u"Moderated"))
    timecode = models.DecimalField(null=True,max_digits=10, decimal_places=2,blank=True,verbose_name=_(u"Timecode"))
    comment = models.TextField(_(u"Comment"),max_length=1000)
    item = models.ForeignKey(MediaItem,verbose_name=_(u"Media Item"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    
    def __unicode__(self):
        return self.comment

    def get_absolute_url(self):
        return "/item/%s/" % self.item.slug

class Channel(models.Model):
    ''' The model for our channels, all channels can hold items but items can only be part of one channel'''
    name = models.CharField(_(u"Name"),max_length=30)
    slug = AutoSlugField(verbose_name=_(u"Slug"),populate_from='name',unique=True,help_text=_(u"Slugs are parts of an URL that you can define"))
    description = models.TextField(_(u"Description"), max_length=1000, null=True, blank=True,help_text=_(u"Describe the topic or content of the channel"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    featured = models.BooleanField(verbose_name=_(u"Featured"))
    channelThumbURL = models.URLField(_(u"Video Thumb-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as thumbnail for the RSS-Feed"))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/channel/%s/" % self.slug

class Hotfolder(models.Model):
    ''' This is used for hotfolder support. Files in one of these will be added to LambdaCast automagicly using a cron job and a manage task '''
    activated = models.BooleanField(_(u"Activated"))
    channel = models.ForeignKey(Channel,verbose_name=_(u"Channel"),help_text=_(u"The media in the folder will be added to the channel automatically"))
    folderName = models.CharField(u"Name of the folder",max_length=30,help_text=_(u"Set a folder you can add media in and then get it automatically listed in LambdaCast"))
    defaultName = models.CharField(_(u"Title"),max_length=30, blank=True)
    description = models.TextField(_(u"Description"), max_length=1000, null=True, blank=True)
    autoPublish = models.BooleanField(_(u"Auto-Publish"))
    kind = models.IntegerField(_(u"Type"),max_length=1, choices=KIND_CHOICES)
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)

    def __unicode__(self):
        return self.folderName

class Collection(models.Model):
    title = models.CharField(_(u"Title"), max_length=40)
    description = models.TextField(_(u"Description"), max_length=1000)
    slug = AutoSlugField(populate_from='title',unique=True,verbose_name=_(u"Slug"),help_text=_(u"Slugs are parts of an URL that you can define"))
    date = models.DateField(_("Date"),null=True)
    items = models.ManyToManyField(MediaItem,verbose_name=_(u"Media Item"),help_text=_(u"Media you want to add to your collection"))
    channel = models.ForeignKey('portal.Channel',blank=True,null=True,help_text=_(u"Channels you want to add to your collection"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    def __unicode__(self):
        return self.title
    def getClassName(self):
        return self.__class__.__name__
    def get_absolute_url(self):
        return "/collection/%s/" % self.slug

class Submittal(models.Model):
    title = models.CharField(_(u"Title of the submittal"),max_length=200)
    description = models.TextField(_(u"Description of the submittal"),blank=True,help_text=_(u"Insert a sample description to the media. You can use Markdown to add formatting"))
    media_title = models.CharField(_(u"Title"),max_length=200)
    media_description = models.TextField(_(u"Description"),blank=True,help_text=_(u"Insert a sample description to the media. You can use Markdown to add formatting"))
    users = models.ManyToManyField(User,verbose_name=_(u"Users of the submittal"), blank=True, null=True, help_text=_(u"User who use the submittal and get it shown on frontpage"))
    media_channel = models.ForeignKey('portal.Channel',blank=True,null=True,verbose_name=_(u"Channel"),help_text=_(u"Channels are used to order your media"))
    media_license = models.CharField(_(u"License"),max_length=200,choices=LICENSE_CHOICES,default="CC-BY",help_text=_(u"Rights the viewer/listener has"))
    media_linkURL = models.URLField(_(u"Link"),blank=True,verify_exists=False, help_text=_(u"Insert a link to a blog or website that relates to the media"))
    media_kind = models.IntegerField(_(u"Type"),max_length=1, choices=KIND_CHOICES,help_text=_(u"The type of the media could be video or audio or both"))
    media_torrentURL = models.URLField(_(u"Torrent-URL"),blank=True,verify_exists=False,help_text=_(u"The URL to the torrent-file"))
    media_mp4URL = models.URLField(_(u"MP4-URL"),blank=True,verify_exists=False,help_text=_(u"Add the link of the media folder or any other one with .mp4 ending"))
    media_webmURL = models.URLField(_(u"WEBM-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .webm ending"))
    media_mp3URL = models.URLField(_(u"MP3-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .mp3 ending"))
    media_oggURL = models.URLField(_(u"OGG-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .ogg ending"))
    media_opusURL = models.URLField(_(u"OPUS-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .opus ending"))
    media_videoThumbURL = models.URLField(_(u"Video Thumb-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as thumbnail"))
    media_audioThumbURL = models.URLField(_(u"Audio Cover-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as cover"))
    media_published = models.BooleanField(verbose_name=_(u"Published"))
    media_tags = TaggableManager(_(u"Tags"),blank=True,help_text=_(u"Insert what the media item is about in short terms divided by commas"))
    media_torrentDone = models.BooleanField(verbose_name=_(u"Torrent done"))
    def __unicode__(self):
        return self.title

def getLength(filename):
    ''' Just a little helper to get the duration (in seconds) from a file using ffmpeg '''
    process = subprocess.Popen(['ffmpeg',  '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
    duration = decimal.Decimal(matches['hours'])*3600 + decimal.Decimal(matches['minutes'])*60 + decimal.Decimal(matches['seconds'])
    return duration
pre_save.connect(set_mediatype, sender=MediaFile)
pre_save.connect(get_remote_filesize, sender=MediaFile)
post_delete.connect(purge_encoded_files, sender=MediaItem)
