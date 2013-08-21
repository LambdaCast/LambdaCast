from django.forms import ModelForm
from django import forms

from portal.models import Video
from portal.models import Comment

import lambdaproject.settings as settings
import os
import os.path

class VideoForm(ModelForm):
    ''' Used for the uploading form '''

    class Meta:
        model = Video
        exclude = ["slug","mp4URL","mp4Size","flashURL","flashSize","webmURL","webmSize","mp3URL","mp3Size","oggURL","oggSize","ogvURL","ogvSize","duration","published","encodingDone","assemblyid","torrentURL","user","autoPublish", "torrentDone"]

    def __init__(self, *args, **kwargs):
	THUMBNAILS_LIST = self.getThumbnails(settings.THUMBNAILS_DIR)
        super(VideoForm, self).__init__(*args, **kwargs)
        for fieldName in self.fields:
            if fieldName == 'audioThumbURL':
                self.fields['audioThumbURL'] = forms.ChoiceField(choices=THUMBNAILS_LIST) 
            else:
                field = self.fields[fieldName]
                if field.required:
                    field.widget.attrs['class'] = 'required'

    def getThumbnails(self,thumbssettings):
        ''' Lists all thumbnails from the /media/thumbnails-directory and sends them to the videoThumbURL and audioThumbURL '''
        thumbsdir = thumbssettings
        if not os.path.exists(thumbsdir):
            os.makedirs(thumbsdir)
        thumbsdir = thumbsdir + '/'
        thumb_list = []
        for thumbfile in os.listdir(thumbsdir):
            if os.path.isfile(os.path.join(thumbsdir, thumbfile)):
                thumb_list.append((("http://" + thumbfile),("http://" + thumbfile)))
            print thumb_list
        return thumb_list

class CommentForm(ModelForm):
    ''' Used for the comments '''
    class Meta:
        model = Comment
        exclude = ["ip","moderated","video"]
