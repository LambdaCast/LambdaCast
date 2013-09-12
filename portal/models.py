from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User

from autoslug import AutoSlugField
from taggit.managers import TaggableManager

import lambdaproject.settings as settings

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

from threading import Event

import markdown

from BitTornadoABC.btmakemetafile import calcsize, make_meta_file, ignore

KIND_CHOICES = (
    (0, _(u'Video-only')),
    (1, _(u'Audio-only')),
    (2, _(u'Audio and Video')),
)

class Video(models.Model):
    ''' The model for our videos. It uses slugs (with DjangoAutoSlug) and tags (with Taggit)
    everything else is quite standard. The sizes fields are used in the feeds to make enclosures
    possible. The videoThumbURL is the URL for Projekktor's "poster" and assemblyid is just a storage
    for the result we get back from transloadit so that we know which video just triggered the "encoding_done"
    view. Why are there URL fields and not file fields? Because you maybe want to use external storage
    (like Amazon S3) to store your files '''
    title = models.CharField(_(u"Title"),max_length=200)
    slug = AutoSlugField(populate_from='title',unique=True,verbose_name=_(u"Slug"),help_text=_(u"Slugs are parts of an URL that you can define"))
    date = models.DateField(_(u"Date"),help_text=_(u"Upload or record date"))
    description = models.TextField(_(u"Description"),blank=True,help_text=_(u"Insert a description to the media. You can use Markdown to add formatting"))
    user = models.ForeignKey(User,verbose_name=_(u"User"), blank=True, null=True, help_text=_(u"Shows which user made or uploaded the video"))
    channel = models.ForeignKey('portal.Channel',blank=True,null=True,verbose_name=_(u"Channel"),help_text=_(u"Channels are used to order your media"))
    linkURL = models.URLField(_(u"Link"),blank=True,verify_exists=False, help_text=_(u"Insert a link to a blog or website that relates to the media"))
    kind = models.IntegerField(_(u"Type"),max_length=1, choices=KIND_CHOICES,help_text=_(u"The type of the media could be video or audio or both"))
    torrentURL = models.URLField(_(u"Torrent-URL"),blank=True,verify_exists=False,help_text=_(u"The URL to the torrent-file"))
    mp4URL = models.URLField(_(u"MP4-URL"),blank=True,verify_exists=False,help_text=_(u"Add the link of the media folder or any other one with .mp4 ending"))
    mp4Size = models.BigIntegerField(_(u"MP4 Size in Bytes"),null=True,blank=True)
    webmURL = models.URLField(_(u"WEBM-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .webm ending"))
    webmSize = models.BigIntegerField(_(u"WEBM Size in Bytes"),null=True,blank=True)
    mp3URL = models.URLField(_(u"MP3-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .mp3 ending"))
    mp3Size = models.BigIntegerField(_(u"MP3 Size in Bytes"),null=True,blank=True)
    oggURL = models.URLField(_(u"OGG-URL"),blank=True,verify_exists=False, help_text=_(u"Add the link of the media folder or any other one with .ogg ending"))
    oggSize = models.BigIntegerField(_(u"OGG Size in Bytes"),null=True,blank=True)
    videoThumbURL = models.URLField(_(u"Video Thumb-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as thumbnail for the media list"))
    audioThumbURL = models.URLField(_(u"Audio Cover-URL"),blank=True,verify_exists=False, help_text=_(u"Use a picture as cover for the media list"))
    duration = models.DecimalField(verbose_name=_(u"Duration"),null=True, max_digits=10, decimal_places=2, blank=True, help_text=_(u"The length of the media"))
    autoPublish = models.BooleanField(verbose_name=_(u"Auto-Publish"),default=True)
    published = models.BooleanField(verbose_name=_(u"Published"))
    encodingDone = models.BooleanField(verbose_name=_(u"Encoding done"))
    torrentDone = models.BooleanField(verbose_name=_(u"Torrent done"))
    assemblyid = models.CharField(_(u"Transloadit Result"),max_length=100,blank=True)
    tags = TaggableManager(_(u"Tags"),blank=True,help_text=_(u"Insert what the video is about in short terms divided by commas"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    originalFile = models.FileField(_(u"File"),upload_to="raw/%Y/%m/%d/",max_length=2048)
    
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/videos/%s/" % self.slug
    def getClassName(self):
        return self.__class__.__name__
  
    def oggSize_mb(self):
        size = float(self.oggSize) / 1024 / 1024
        return round(size, 3)
    
    def mp3Size_mb(self):
        size = float(self.mp3Size) / 1024 / 1024
        return round(size, 3)

    def mp4Size_mb(self):
        size = float(self.mp4Size) / 1024 / 1024
        return round(size, 3)

    def webmSize_mb(self):
        size = float(self.webmSize) / 1024 / 1024
        return round(size, 3)

    def markdown_free(self):
        md_free_desc = markdown.markdown(self.description)
        html_free_desc = re.sub('<[^<]+?>', '', md_free_desc)
        return unicode(html_free_desc)

    def encode_media(self):
        ''' This is used to tell ffmpeg what to do '''
        kind = self.kind
        path = self.originalFile.path
        outputdir = settings.ENCODING_OUTPUT_DIR + self.slug
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        outputdir = outputdir + '/'
        if ((kind == 0) or (kind == 2)):
            logfile = outputdir + 'encoding_mp4_log.txt'
            outfile_mp4 = outputdir + self.slug + '.mp4'
            # Create the command line
            cl_mp4 = ffmpeg(path, outfile_mp4, logfile, MP4_VIDEO, MP4_AUDIO).build_command_line()
            
            logfile = outputdir + 'encoding_webm_log.txt'
            outfile_webm = outputdir + self.slug + '.webm'
    
            cl_webm = ffmpeg(path, outfile_webm, logfile, WEBM_VIDEO, WEBM_AUDIO).build_command_line()
            
            self.mp4URL = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + self.slug + '.mp4'
            self.webmURL = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + self.slug + '.webm' 
            self.videoThumbURL = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + self.slug + '.jpg'
            outcode = subprocess.Popen(cl_mp4, shell=True)
            
            while outcode.poll() == None:
                pass
    
            if outcode.poll() == 0:
                self.mp4Size = os.path.getsize(outfile_mp4)
                self.duration = getLength(outfile_mp4)
            else:
                raise StandardError(_(u"Encoding MP4 Failed"))
            
            print(cl_mp4)
            print(cl_webm)    
            outcode = subprocess.Popen(cl_webm, shell=True)
            
            while outcode.poll() == None:
                pass
    
            if outcode.poll() == 0:
                self.wembSize = os.path.getsize(outfile_webm)
            else:
                raise StandardError(_(u"Encoding WEBM Failed"))
    
            outcode = subprocess.Popen(['ffmpeg -i '+ self.originalFile.path + ' -ss 5.0 -vframes 1 -f image2 ' + outputdir + self.slug + '.jpg'],shell = True)
            
            while outcode.poll() == None:
                pass
    
            if outcode.poll() == 0:
                pass 
            else:
                raise StandardError(_(u"Making Thumb Failed"))
            
            
        if((kind == 1) or (kind == 2)):
            logfile = outputdir + 'encoding_mp3_log.txt'
            outfile_mp3 = outputdir + self.slug + '.mp3'
            # Create the command line
            cl_mp3 = ffmpeg(path, outfile_mp3, logfile, NULL_VIDEO , MP3_AUDIO).build_command_line()
            
            logfile = outputdir + 'encoding_ogg_log.txt'
            outfile_ogg = outputdir + self.slug + '.ogg'

            cl_ogg = ffmpeg(path, outfile_ogg, logfile, NULL_VIDEO, OGG_AUDIO).build_command_line()
            
            self.mp3URL = settings.ENCODING_VIDEO_BASE_URL + self.slug +  '/' + self.slug + '.mp3'
            self.oggURL = settings.ENCODING_VIDEO_BASE_URL + self.slug +  '/' + self.slug + '.ogg'
            
            outcode = subprocess.Popen(cl_mp3, shell=True)
            
            while outcode.poll() == None:
                pass
    
            if outcode.poll() == 0:
                self.mp3Size = os.path.getsize(outfile_mp3)
                self.duration = getLength(outfile_mp3)
            else:
                raise StandardError(_(u"Encoding MP3 Failed"))
                
            outcode = subprocess.Popen(cl_ogg, shell=True)
            
            while outcode.poll() == None:
                pass
    
            if outcode.poll() == 0:
                self.oggSize = os.path.getsize(outfile_ogg)
            else:
                raise StandardError(_(u"Encoding OGG Failed"))
                
#        if (kind == 1):
#            file = File(self.originalFile.path) # mutagen can automatically detect format and type of tags
#            if not isinstance(file, NoneType) and file.tags and 'APIC:' in file.tags and file.tags['APIC:']:
#                artwork = file.tags['APIC:'].data # access APIC frame and grab the image
#                with open(outputdir + self.slug + '_cover.jpg', 'wb') as img:
#                    img.write(artwork)

#                self.audioThumbURL = settings.ENCODING_VIDEO_BASE_URL + self.slug + '/' + self.slug + '_cover.jpg'

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
        
class Comment(models.Model):
    ''' The model for our comments, please note that (right now) LambdaCast comments are moderated only'''
    name = models.CharField(_(u"Name"),max_length=30)
    ip = models.IPAddressField("IP",blank=True,null=True,help_text=_(u"The IP of the one who posted the comment"))
    moderated = models.BooleanField(verbose_name=_(u"Moderated"))
    timecode = models.DecimalField(null=True,max_digits=10, decimal_places=2,blank=True,verbose_name=_(u"Timecode"))
    comment = models.TextField(_(u"Comment"),max_length=1000)
    video = models.ForeignKey(Video,verbose_name=_(u"Video"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    
    def __unicode__(self):
        return self.comment

class Channel(models.Model):
    ''' The model for our channels, all channels can hold videos but videos can only be part of one channel'''
    name = models.CharField(_(u"Name"),max_length=30)
    slug = AutoSlugField(verbose_name=_(u"Slug"),populate_from='name',unique=True,help_text=_(u"Slugs are parts of an URL that you can define"))
    description = models.TextField(_(u"Description"), max_length=1000, null=True, blank=True,help_text=_(u"Describe the topic or content of the channel"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    featured = models.BooleanField(verbose_name=_(u"Featured"))

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/videos/channel/%s/" % self.slug

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
    videos = models.ManyToManyField('portal.Video',verbose_name=_(u"Videos"),help_text=_(u"Media you want to add to your collection"))
    channel = models.ForeignKey('portal.Channel',blank=True,null=True,help_text=_(u"Channels you want to add to your collection"))
    created = models.DateTimeField(verbose_name=_(u"Created"),auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_(u"Modified"),auto_now=True)
    def __unicode__(self):
        return self.title
    def getClassName(self):
        return self.__class__.__name__
    def get_absolute_url(self):
        return "/collection/%s/" % self.slug

def getLength(filename):
    ''' Just a little helper to get the duration (in seconds) from a video file using ffmpeg '''
    process = subprocess.Popen(['ffmpeg',  '-i', filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
    duration = decimal.Decimal(matches['hours'])*3600 + decimal.Decimal(matches['minutes'])*60 + decimal.Decimal(matches['seconds'])
    return duration
