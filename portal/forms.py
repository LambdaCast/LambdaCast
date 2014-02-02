from django.forms import ModelForm
from django import forms

from captcha.fields import CaptchaField

from portal.models import MediaItem
from portal.models import Comment
from portal.models import Submittal

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
        exclude = ["slug","mp4URL","mp4Size","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","duration","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone","videoThumbURL","audioThumbURL"]

    def __init__(self, *args, **kwargs):
        super(MediaItemForm, self).__init__(*args, **kwargs)
        THUMBNAILS_LIST = getThumbnails(settings.THUMBNAILS_DIR)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            if field.required:
                field.widget.attrs['class'] = 'required'
        self.fields['thumbURL'] = forms.ChoiceField(choices=THUMBNAILS_LIST, required=False, label=_("Thumbnail")) 


class CommentForm(ModelForm):
    ''' Used for the comments '''
    captcha = CaptchaField()
    class Meta:
        model = Comment
        exclude = ["ip","moderated","item"]

class SubmittalForm(ModelForm):
    ''' Used for creating media instances through submittals '''
    class Meta:
        model = MediaItem
        exclude = ["slug","mp4Size","webmSize","mp3Size","oggSize","assemblyid","user","autoPublish","originalFile"]

    def __init__(self, *args, **kwargs):
        super(SubmittalForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            if field.required:
                field.widget.attrs['class'] = 'required'

class ThumbnailForm(forms.Form):
    ''' Used for uploading thumbnails '''
    title = forms.CharField(max_length=50, help_text=_('The name of the image with file format like "test.png"'), label=_("Title"))
    file = forms.FileField(help_text=_('Only upload image files'),label=_("File"))
