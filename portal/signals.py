from django.db.models.signals import pre_save
import urllib2

def get_remote_filesize(sender, instance, **kwargs):
    format_list = [instance.mp3URL, instance.mp4URL, instance.webmURL, instance.oggURL]
    size_list = []
    for url in format_list: 
        try:
            request = urllib2.Request(url)
            request.get_method = lambda: 'HEAD'

            response = urllib2.urlopen(request)
            size_in_bytes = response.info().getheader('content-length')
            size_list.append(size_in_bytes)
        except:
            size_list.append(0)
    
    instance.mp3Size = size_list[0]
    instance.mp4Size = size_list[1]
    instance.webmSize = size_list[2]
    instance.oggSize = size_list[3]
