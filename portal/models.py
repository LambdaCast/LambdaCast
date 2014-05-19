# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import pre_save, post_delete
from django.contrib.auth.models import User

import djangotasks

from autoslug import AutoSlugField
from taggit.managers import TaggableManager

import lambdaproject.settings as settings

from pytranscode.ffmpeg import ffmpeg

from portal.signals import get_remote_filesize, purge_files, get_mediatype
from portal.licenses import LICENSE_CHOICES, LICENSE_URLS
from portal.media_formats import FILE_FORMATS, MEDIA_TYPES, MEDIA_FORMATS
from portal.model_helpers import *

import subprocess
import decimal
import re
import time

from mutagen.mp3 import MP3
from mutagen.id3 import ID3

from threading import Event

import markdown

from BitTornadoABC.btmakemetafile import make_meta_file

class MediaFile(models.Model):
    ''' The model only for the media files '''
    title = models.CharField(_(u"Title"),max_length=200)
    url = models.URLField(_(u"URL to Transcoded File"), verify_exists=False, max_length=512, help_text=_(u"Insert the link to the media file"))
    file_format = models.CharField(_(u"File Format"), max_length=20, choices=FILE_FORMATS,default="MP3", help_text=_(u"File format of the media file"))
    size = models.BigIntegerField(_(u"File Size in Bytes"), null=True, blank=True)
    media_item = models.ForeignKey('portal.MediaItem', help_text=_(u"Media Item the file is connected to"))
    mediatype = models.CharField(_(u"Media Type"), max_length=20, choices=MEDIA_TYPES, default="audio", help_text=_(u"File type of the media file (audio or video)"))

    class Meta:
        verbose_name = _('Media File')
        verbose_name_plural = _('Media Files')

    def mime_type(self):
        return MEDIA_FORMATS[self.file_format].mime_type

    def encode_media(self):
        ''' This is used to tell ffmpeg what to do '''
        media_format = MEDIA_FORMATS[self.file_format]

        path = self.media_item.originalFile.path
        outputdir = settings.ENCODING_OUTPUT_DIR + self.media_item.slug + '/'

        # Create the command line (MP3)
        logfile = outputdir + 'encoding_' + media_format.format_key + '_log.txt'
        outfile = outputdir + self.media_item.slug + media_format.extension
        cl = ffmpeg(path, outfile, logfile, media_format.video_options , media_format.audio_options).build_command_line()

        outcode = subprocess.Popen(cl, shell=True)

        while outcode.poll() == None:
            time.sleep(1)

        if outcode.poll() != 0:
            raise StandardError("Encoding " + media_format.text + " Failed")

        self.save()
        self.media_item.finish_encoding()

    def get_tasks(self):
        return djangotasks.Task.objects.filter(object_id=self.pk, model="portal.mediafile")

class MediaItem(models.Model):
    ''' The model for our items. It uses slugs (with DjangoAutoSlug) and tags (with Taggit)
    everything else is quite standard. The sizes fields are used in the feeds to make enclosures
    possible. The videoThumbURL is the URL for Projekktor's "poster". Why are there URL fields
    and not file fields? Because you maybe want to use external storage (like Amazon S3) to
    store your files '''
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
    tags = TaggableManager(_(u"Tags"),blank=True,help_text=_(u"Insert what the media item is about in short terms divided by commas"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    originalFile = models.FileField(_(u"File"),upload_to="raw/%Y/%m/%d/",max_length=2048)

    class Meta:
        verbose_name = _('Media Item')
        verbose_name_plural = _('Media Items')

    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/item/%s/" % self.slug
    def getClassName(self):
        return self.__class__.__name__

    def mediafiles(self):
        return self.mediafile_set.exclude(size__isnull=True)
    
    def comments_count(self):
        return self.comment_set.filter(moderated=True).count()

    def comments_count_all(self):
        return self.comment_set.all().count()

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
            wp_code = wp_code + '<a title="%s %s" href="%s" target="_blank">%s</a>, ' % (self.title,mediafile.get_file_format_display(),mediafile.url,mediafile.get_file_format_display())
        for mediafile in downloads_audio:
            wp_code = wp_code + '<a title="%s %s" href="%s" target="_blank">%s</a>, ' % (self.title,mediafile.get_file_format_display(),mediafile.url,mediafile.get_file_format_display())
        if self.description:
            wp_code = wp_code + '\n\n<!--more-->\n%s' % ((markdown.markdown(self.description)))
        return unicode(wp_code)

    def get_and_save_cover(self):
        ''' get the covers from the original file '''
        original_path = self.originalFile.path

        outputdir = settings.ENCODING_OUTPUT_DIR + self.slug + '/'

        # try to get a video thumbnail
        outcode = subprocess.Popen(['ffmpeg -i '+ original_path + ' -ss 5.0 -vframes 1 -f image2 ' + outputdir + self.slug + '.jpg'],shell = True)

        # Get cover of mp3-file
        if original_path.endswith('.mp3') and not self.audioThumbURL:
            audio_mp3 = MP3(original_path, ID3=ID3)
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
                    self.audioThumbURL = settings.ENCODED_BASE_URL + self.slug + '/' + filename
            except:
                pass

        while outcode.poll() == None:
            time.sleep(0.1);

        if outcode.poll() == 0:
            # safe if successful, else ignore it
            self.videoThumbURL = settings.ENCODED_BASE_URL + self.slug + '/' + self.slug + '.jpg'

        # TODO: use update_fields after update to django 1.5
        update(self, audioThumbURL=self.audioThumbURL, videoThumbURL=self.videoThumbURL).save()

    def finish_encoding(self):
        mediaitem = refresh(self)
        if not mediaitem.published:
            mediaitem.encodingDone = bool(mediaitem.mediafiles())
            mediaitem.published = mediaitem.autoPublish and mediaitem.encodingDone
            # TODO: use update_fields after update to django 1.5
            mediaitem.save()

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

    def get_and_save_duration(self):
        ''' Just a little helper to get the duration (in seconds) from a file using ffmpeg '''
        filepath = self.originalFile.path if self.originalFile else (self.mediafiles()[0].url if self.mediafiles() else None)
        if filepath:
            process = subprocess.Popen(['ffmpeg',  '-i', filepath], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, _ = process.communicate()
            matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
            self.duration = decimal.Decimal(matches['hours'])*3600 + decimal.Decimal(matches['minutes'])*60 + decimal.Decimal(matches['seconds'])
            self.save()

    def get_license_link(self):
        return LICENSE_URLS[self.license]

    audio_files = None
    def get_audio_files(self):
        if not self.audio_files: self.audio_files = self.mediafiles().filter(mediatype='audio')
        return self.audio_files

    video_files = None
    def get_video_files(self):
        if not self.video_files: self.video_files = self.mediafiles().filter(mediatype='video')
        return self.video_files

    def get_tasks(self):
        return djangotasks.Task.objects.filter(object_id=self.pk, model="portal.mediaitem")

class Comment(models.Model):
    ''' The model for our comments, please note that (right now) LambdaCast comments are moderated only'''
    name = models.CharField(_(u"Name"),max_length=30)
    ip = models.GenericIPAddressField("IP",blank=True,null=True,help_text=_(u"The IP of the one who posted the comment"))
    moderated = models.BooleanField(verbose_name=_(u"Moderated"))
    timecode = models.DecimalField(null=True,max_digits=10, decimal_places=2,blank=True,verbose_name=_(u"Timecode"))
    comment = models.TextField(_(u"Comment"),max_length=1000)
    item = models.ForeignKey(MediaItem,verbose_name=_(u"Media Item"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

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
    channelThumbURL = models.URLField(_(u"Channel Thumb URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as thumbnail for the RSS-Feed"))

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
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)

    class Meta:
        verbose_name = _('Hotfolder')
        verbose_name_plural = _('Hotfolder')

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

    class Meta:
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

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

    class Meta:
        verbose_name = _('Submittal')
        verbose_name_plural = _('Submittals')

    def __unicode__(self):
        return self.title

pre_save.connect(get_remote_filesize, sender=MediaFile)
pre_save.connect(get_mediatype, sender=MediaFile)
post_delete.connect(purge_files, sender=MediaItem)

djangotasks.register_task(MediaFile.encode_media, "Encode the file using ffmpeg")
djangotasks.register_task(MediaItem.get_and_save_cover, "Get the cover from the original file")
djangotasks.register_task(MediaItem.create_bittorrent, "Create Bittorrent file for item and serve it")
