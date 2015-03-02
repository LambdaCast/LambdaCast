from django.db import models
from django.utils.safestring import mark_safe 
from django.utils.translation import ugettext_lazy as _

from autoslug import AutoSlugField

# Create your models here.

class Stream(models.Model):
    ''' This is the model for each live stream event nothing really special
    except for the iframe field maybe. It contains the loaded iframe for 
    each stream event and is marked as safe. Maybe we change this or add
    support for streams directly loaded into Projekktor'''
    title = models.CharField(_(u"Stream title"),max_length=200)
    slug = AutoSlugField(populate_from='title',unique=True,verbose_name=_(u"Slug"),help_text=_(u"Slugs are parts of an URL that you can define"))
    startDate = models.DateTimeField(_(u"Beginning of the event"))
    endDate = models.DateTimeField(_(u"End of the event"))
    description = models.TextField(_(u"Description"))
    link = models.URLField(_(u"Link"),blank=True)
    rtmpLink = models.URLField(_(u"RTMP Link"),blank=True,help_text=_(u"RTMP is a protocol to stream video. If you have a server as host, you can insert a link of the output"))
    audioOnlyLink = models.URLField(_(u"Audio-only Link"),blank=True)
    iframe = models.TextField(_(u"iFrame of the Stream"))
    published = models.BooleanField(verbose_name=_(u"Published"),default=False)
    created = models.DateTimeField(auto_now_add=True,verbose_name=_(u"Created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_(u"Modified"))
    def __unicode__(self):
        return self.title
    def get_absolute_url(self):
        return "/stream/%s/" % self.slug
    def display_iFrameSafeField(self): 
        return mark_safe(self.iframe)
