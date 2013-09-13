from django.forms import ModelForm
from django import forms

from captcha.fields import CaptchaField

from portal.models import Video
from portal.models import Comment

import lambdaproject.settings as settings
import os
import os.path

def getThumbnails(thumbssettings):
    ''' Lists all thumbnails from the /media/thumbnails-directory and sends them to the videoThumbURL and audioThumbURL '''
    thumbsdir = thumbssettings
    if not os.path.exists(thumbsdir):
        os.makedirs(thumbsdir)
    thumbsdir = thumbsdir + '/'
    thumb_list = []
    for thumbfile in os.listdir(thumbsdir):
        if os.path.isfile(os.path.join(thumbsdir, thumbfile)):
            thumb_list.append((("http://" + thumbfile),("http://" + thumbfile)))
    return thumb_list

THUMBNAILS_LIST = getThumbnails(settings.THUMBNAILS_DIR)

class VideoForm(ModelForm):
    ''' Used for the uploading form '''

    class Meta:
        model = Video
        exclude = ["slug","mp4URL","mp4Size","flashURL","flashSize","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","ogvURL","ogvSize","duration","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone", "audioThumbURL", "videoThumbURL"]

    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
#            if fieldName == 'audioThumbURL':
#                self.fields['audioThumbURL'] = forms.MultipleChoiceField(choices=THUMBNAILS_LIST) 
#            else:
            field = self.fields[fieldName]
            if field.required:
                field.widget.attrs['class'] = 'required'
        Thumb = self.fields['Thumb'] = forms.ChoiceField(choices=THUMBNAILS_LIST)

class CommentForm(ModelForm):
    ''' Used for the comments '''
    captcha = CaptchaField()
    class Meta:
        model = Comment
        exclude = ["ip","moderated","video"]
