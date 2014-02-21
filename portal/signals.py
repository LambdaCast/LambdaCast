from django.db.models.signals import pre_save
import urllib2
import models

def get_remote_filesize(sender, instance, **kwargs):
    instance.size = _get_remote_filesize_for_url(instance.url)

def _get_remote_filesize_for_url(url):
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'

        response = urllib2.urlopen(request)
        return response.info().getheader('content-length')
    except:
        pass

def set_mediatype(sender, instance, **kwargs):
    for mediatype in models.FORMATINFO_LIST:
        if instance.file_format == mediatype[0]:
            instance.mediatype = mediatype[2]
