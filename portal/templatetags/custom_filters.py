from django import template
import datetime
import urllib

from django.utils.text import normalize_newlines

register = template.Library()

@register.filter(name='secondstohms')
def secondstohms(value):
    ''' This is used to have a nicer format for the video duration in the template'''
    if (value):
        return str(datetime.timedelta(seconds=int(value)))

@register.filter(name='remove_newlines')
def remove_newlines(text):
    ''' Removes all newline characters from a block of text.'''
    normalized_text = normalize_newlines(text)
    return normalized_text.replace('\n', ' ')

@register.filter(name="get_remote_size")
def get_remote_size(url):
    site = urllib.urlopen(url)
    meta = site.info()
    size_in_mb = float(meta.getheaders("Content-Length")[0]) / 1024 / 1024 
    return round(size_in_mb, 2)
