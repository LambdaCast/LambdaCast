from django.forms import ModelForm
from django import forms

from captcha.fields import CaptchaField

from portal.models import MediaItem
from portal.models import Comment
from portal.models import Submittal
from portal.models import MediaFile
import models

from django.utils.translation import ugettext_lazy as _

from taggit.forms import *

import lambdaproject.settings as settings
import os
import os.path

def getThumbnails(thumbssettings):
    ''' Lists all thumbnails from the /media/thumbnails-directory and sends them to the videoThumbURL and audioThumbURL '''
    thumbsdir = thumbssettings
    if not os.path.exists(thumbsdir):
        os.makedirs(thumbsdir)
    thumbsdir = thumbsdir + '/'
    thumb_list = [("", _(u"Automaticly"))]
    for thumbfile in os.listdir(thumbsdir):
        if os.path.isfile(os.path.join(thumbsdir, thumbfile)):
            thumb_list.append(((settings.DOMAIN + "/media/thumbnails/" + thumbfile),(thumbfile)))
    return thumb_list


class MediaItemForm(ModelForm):
    ''' Used for the uploading form '''

    class Meta:
        model = MediaItem
        exclude = ["slug","mp4URL","mp4Size","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","duration","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone","videoThumbURL","audioThumbURL", "kind"]

    def __init__(self, *args, **kwargs):
        super(MediaItemForm, self).__init__(*args, **kwargs)
        THUMBNAILS_LIST = getThumbnails(settings.THUMBNAILS_DIR)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            if field.required:
                field.widget.attrs['class'] = 'required'
        self.fields['thumbURL'] = forms.ChoiceField(choices=THUMBNAILS_LIST, required=False, label=_("Thumbnail"))
        self.fields['fileFormats'] = forms.MultipleChoiceField(choices=models.FILE_FORMATS, required=True, label=_("File Formats"))

class CommentForm(ModelForm):
    ''' Used for the comments '''
    captcha = CaptchaField()
    class Meta:
        model = Comment
        exclude = ["ip","moderated","item"]

class SubmittalForm(ModelForm):
    ''' Used for creating media instances through submittals '''
    media_mp4URL = forms.URLField(help_text=_('Enter the URL to the mp4 file'), label=_("MP4-URL"),required=False)
    media_webmURL = forms.URLField(help_text=_('Enter the URL to the webm file'), label=_("WEBM-URL"),required=False)
    media_mp3URL = forms.URLField(help_text=_('Enter the URL to the mp3 file'), label=_("MP3-URL"),required=False)
    media_oggURL = forms.URLField(help_text=_('Enter the URL to the ogg file'), label=_("OGG-URL"),required=False)
    media_opusURL = forms.URLField(help_text=_('Enter the URL to the opus file'), label=_("OPUS-URL"),required=False)

    class Meta:
        model = MediaItem
        exclude = ["kind","slug","assemblyid","user","autoPublish","originalFile"]

    def __init__(self, *args, **kwargs):
        super(SubmittalForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            if field.required:
                field.widget.attrs['class'] = 'required'

    def create_mediafiles(self, mediaitem):
        if not self.data['media_webmURL'] == "":
            mediafile_webm = MediaFile.objects.create(title=mediaitem.slug+' WEBM',url=self.data['media_webmURL'],file_format="WEBM",media_item=mediaitem, mediatype='video')
        if not self.data['media_mp4URL'] == "":
            mediafile_mp4 = MediaFile.objects.create(title=mediaitem.slug+' MP4',url=self.data['media_mp4URL'],file_format="MP4",media_item=mediaitem, mediatype='video')
        if not self.data['media_mp3URL'] == "":
            mediafile_mp3 = MediaFile.objects.create(title=mediaitem.slug+' MP3',url=self.data['media_mp3URL'],file_format="MP3",media_item=mediaitem, mediatype='audio')
        if not self.data['media_oggURL'] == "":
            mediafile_ogg = MediaFile.objects.create(title=mediaitem.slug+' OGG',url=self.data['media_oggURL'],file_format="OGG",media_item=mediaitem, mediatype='audio')
        if not self.data['media_opusURL'] == "":
            mediafile_opus = MediaFile.objects.create(title=mediaitem.slug+' OPUS',url=self.data['media_opusURL'],file_format="OPUS",media_item=mediaitem, mediatype='audio')
 

class ThumbnailForm(forms.Form):
    ''' Used for uploading thumbnails '''
    title = forms.CharField(max_length=50, help_text=_('The name of the image with file format like "test.png"'), label=_("Title"))
    file = forms.FileField(help_text=_('Only upload image files'),label=_("File"))
