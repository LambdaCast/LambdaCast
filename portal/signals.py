from django.db.models.signals import pre_save
import urllib2

FILEFORMAT_LIST = (
    ("MP3", ".mp3", "audio"),
    ("MP4", ".mp4", "video"),
    ("VORBIS", ".ogg", "audio"),
    ("THEORA", ".ogg", "audio"),
    ("WEBM", ".webm", "video"),
    ("OPUS", ".opus", "audio"),
)

def get_remote_filesize(sender, instance, **kwargs):
    instance.size = _get_remote_filesize_for_url(instance.url)

def _get_remote_filesize_for_url(url):
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'

        response = urllib2.urlopen(request)
        return response.info().getheader('content-length')
    except:
        return 0

def define_mediatype(sender, instance, **kwargs):
    for tuple in FILEFORMAT_LIST:
        if instance.file_format == tuple[0]:
            instance.mediatype = tuple[2]

def validate_url(sender, instance, **kwargs):
    for tuple in FILEFORMAT_LIST:
        if instance.file_format == tuple[0]:
            if not instance.url.endswith(tuple[1]):
                raise ValidationError(_(u"URL doesn't end with %s" % tuple[1]))

