from django import template
import datetime

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

@register.filter(name="in_mb")
def in_mb(number_bytes):
    size_in_mb = float(number_bytes) / 1024 / 1024 
    return round(size_in_mb, 2)
