from django.db.models.signals import pre_save
import urllib2

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

def validate_url(sender, instance, **kwargs):
    fileformat_list = (
        ("MP3", ".mp3"),
        ("MP4", ".mp4"),
        ("VORBIS", ".ogg"),
        ("THEORA", ".ogg"),
        ("WEBM", ".webm"),
        ("OPUS", ".opus"),
    )
    for tuple in fileformat_list:
        if instance.file_format == tuple[0]:
            if not instance.url.endswith(tuple[1]):
                raise ValidationError(_(u"URL doesn't end with %s" % tuple[1]))

