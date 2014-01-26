from django import template
import datetime

import markdown
from django.utils.safestring import mark_safe


from django.utils.text import normalize_newlines

register = template.Library()

@register.filter(name='secondstohms')
def secondstohms(value):
    ''' This is used to have a nicer format for the media duration in the template'''
    if (value):
        return str(datetime.timedelta(seconds=int(value)))

@register.filter(name='remove_newlines')
def remove_newlines(text):
    ''' Removes all newline characters from a block of text.'''
    normalized_text = normalize_newlines(text)
    return normalized_text.replace('\n', ' ')

@register.filter(name="in_mb")
def in_mb(number_bytes):
    return round(float(number_bytes) / 1024 / 1024, 2) if number_bytes is not None else 0

@register.filter(name="render_markdown")
def render_markdown(text):
    rendered_md = markdown.markdown(text)
    return mark_safe(rendered_md)

