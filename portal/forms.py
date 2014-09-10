from django.utils.translation import ugettext_lazy as _
from django.forms import Form, ModelForm
from django import forms
from django.core.validators import RegexValidator

from captcha.fields import CaptchaField

from portal.models import MediaItem, MediaFile, Comment
from portal.media_formats import FILE_FORMATS

import lambdaproject.settings as settings
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
            thumb_list.append(((settings.THUMBNAILS_BASE_URL + thumbfile),(thumbfile)))
    return thumb_list

class MediaItemForm(ModelForm):
    ''' Used for the uploading form '''
    thumbURL = forms.ChoiceField(choices=getThumbnails(settings.THUMBNAILS_DIR), required=False, label=_("Thumbnail"))
    fileFormats = forms.MultipleChoiceField(choices=FILE_FORMATS, required=True, label=_("File Formats"))

    class Meta:
        model = MediaItem
        exclude = ["slug","duration","published","encodingDone","torrentURL","user","autoPublish", "torrentDone","videoThumbURL","audioThumbURL"]
        name = forms.CharField(widget=forms.FileInput(attrs={'class':''}))

    def __init__(self, *args, **kwargs):
        super(MediaItemForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['class'] = 'required form-control'

class CommentForm(ModelForm):
    ''' Used for the comments '''
    captcha = CaptchaField()

    class Meta:
        model = Comment
        exclude = ["ip","moderated","item"]

class SubmittalForm(ModelForm):
    ''' Used for creating media instances through submittals '''
    media_mp4URL = forms.URLField(help_text=_('Enter the URL to the mp4 file'), label=_("MP4-URL"),required=False)
    media_webmURL = forms.URLField(help_text=_('Enter the URL to the WebM file'), label=_("WEBM-URL"),required=False)
    media_mp3URL = forms.URLField(help_text=_('Enter the URL to the mp3 file'), label=_("MP3-URL"),required=False)
    media_oggURL = forms.URLField(help_text=_('Enter the URL to the ogg file'), label=_("OGG-URL"),required=False)
    media_opusURL = forms.URLField(help_text=_('Enter the URL to the Opus file'), label=_("OPUS-URL"),required=False)

    class Meta:
        model = MediaItem
        exclude = ["slug","user","autoPublish","originalFile", "duration"]

    def __init__(self, *args, **kwargs):
        super(SubmittalForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['class'] = 'required form-control'


    def create_mediafiles(self, mediaitem):
        if not self.data['media_webmURL'] == "":
            MediaFile.objects.create(title=mediaitem.title+' WebM',url=self.data['media_webmURL'],file_format="WEBM",media_item=mediaitem, mediatype='video')
        if not self.data['media_mp4URL'] == "":
            MediaFile.objects.create(title=mediaitem.title+' mp4',url=self.data['media_mp4URL'],file_format="MP4",media_item=mediaitem, mediatype='video')
        if not self.data['media_mp3URL'] == "":
            MediaFile.objects.create(title=mediaitem.title+' mp3',url=self.data['media_mp3URL'],file_format="MP3",media_item=mediaitem, mediatype='audio')
        if not self.data['media_oggURL'] == "":
            MediaFile.objects.create(title=mediaitem.title+' ogg',url=self.data['media_oggURL'],file_format="OGG",media_item=mediaitem, mediatype='audio')
        if not self.data['media_opusURL'] == "":
            MediaFile.objects.create(title=mediaitem.title+' Opus',url=self.data['media_opusURL'],file_format="OPUS",media_item=mediaitem, mediatype='audio')
 

class ThumbnailForm(Form):
    ''' Used for uploading thumbnails '''
    title = forms.CharField(max_length=50, help_text=_('The name of the image with file format like "test.png"'), label=_("Title"), validators=[RegexValidator(regex="^((?!/).)*$", message=_("Title must not contain a slash"), code='invalid_title')])
    file = forms.FileField(help_text=_('Only upload image files'),label=_("File"))
