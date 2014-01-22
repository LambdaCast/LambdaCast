from django.db.models.signals import pre_save
from django.core.validators import URLValidator

import urllib

def url_validator(url):
    if url.endswith('.mp3') or url.endswith('.mp4') or url.endswith('.ogg') or url.endswith('.webm'):
        url_val = URLValidator(verify_exists=True)
        try:
            url_val(url)
            return url
        except Exception:
            print "url is not verified"
    else:
        raise Exception

def get_remote_filesize(sender, instance, **kwargs):
    format_list = [instance.mp3URL, instance.mp4URL, instance.webmURL, instance.oggURL]
    size_list = []
    for url in format_list:
        try: 
            url_validator(url)
            site = urllib.urlopen(url)
            meta = site.info()
            size_in_bytes = meta.getheaders("Content-Length")[0]
            size_list.append(size_in_bytes)
        except:
            size_list.append(0)
    
    instance.mp3Size = size_list[0]
    instance.mp4Size = size_list[1]
    instance.webmSize = size_list[2]
    instance.oggSize = size_list[3]
