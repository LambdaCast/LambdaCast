from django.forms import ModelForm
from django import forms

from captcha.fields import CaptchaField

from portal.models import Video
from portal.models import Comment

class VideoForm(ModelForm):
    ''' Used for the uploading form '''

    class Meta:
        model = Video
        exclude = ["slug","mp4URL","mp4Size","flashURL","flashSize","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","ogvURL","ogvSize","duration","videoThumbURL","audioThumbURL","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone"]

    def __init__(self, *args, **kwargs):
        super(VideoForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            field = self.fields[fieldName]
            if field.required:
        	    field.widget.attrs['class'] = 'required'

class CommentForm(ModelForm):
    ''' Used for the comments '''
    captcha = CaptchaField()
    class Meta:
        model = Comment
        exclude = ["ip","moderated","video"]
