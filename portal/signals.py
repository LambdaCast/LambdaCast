from django.db.models.signals import pre_save
import urllib2

def get_remote_filesize(sender, instance, **kwargs):
    instance.mp3Size = _get_remote_filesize_for_url(instance.mp3URL)
    instance.oggSize = _get_remote_filesize_for_url(instance.oggURL)
    instance.mp4Size = _get_remote_filesize_for_url(instance.mp4URL)
    instance.webmSize = _get_remote_filesize_for_url(instance.webmURL)

def _get_remote_filesize_for_url(url):
    try:
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'

        response = urllib2.urlopen(request)
        return response.info().getheader('content-length')
    except:
        return 0
