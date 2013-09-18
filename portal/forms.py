from django.forms import ModelForm
from django import forms

from captcha.fields import CaptchaField

from portal.models import Video
from portal.models import Comment

from django.utils.translation import ugettext_lazy as _

import lambdaproject.settings as settings
import os
import os.path

def getThumbnails(thumbssettings):
    ''' Lists all thumbnails from the /media/thumbnails-directory and sends them to the videoThumbURL and audioThumbURL '''
    thumbsdir = thumbssettings
    if not os.path.exists(thumbsdir):
        os.makedirs(thumbsdir)
    thumbsdir = thumbsdir + '/'
    thumb_list = [("", "---")]
    for thumbfile in os.listdir(thumbsdir):
        if os.path.isfile(os.path.join(thumbsdir, thumbfile)):
            thumb_list.append(((settings.DOMAIN + "/media/thumbnails/" + thumbfile),(settings.DOMAIN + "/media/thumbnails/" + thumbfile)))
    return thumb_list


class VideoForm(ModelForm):
    ''' Used for the uploading form '''

    class Meta:
        model = Video
        exclude = ["slug","mp4URL","mp4Size","flashURL","flashSize","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","ogvURL","ogvSize","duration","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone", "videoThumbURL", "audioThumbURL"]

    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
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
        exclude = ["ip","moderated","video"]
