'''
Created on Apr 5, 2014

@author: benjamin
'''

from portal.ffmpeg_presets import *

FILE_FORMATS = (
    ("MP3", "mp3"),
    ("OGG", "ogg"),
    ("OPUS", "Opus"),
    ("MP4", "mp4"),
    ("WEBM", "WebM")
)

MEDIA_TYPES = (
    ("audio", "audio"),
    ("video", "video")
)

MEDIA_FORMATS = {}

class MediaFormat(object):

    def __init__(self, format_key, text, mediatype, mime_type, extension, video_options, audio_options):
        self.format_key = format_key
        self.text = text
        self.mediatype = mediatype
        self.mime_type = mime_type
        self.extension = extension
        self.video_options = video_options
        self.audio_options = audio_options
        MEDIA_FORMATS[format_key] = self

MediaFormat("MP3", "mp3", "audio", "audio/mp3", ".mp3", NULL_VIDEO, MP3_AUDIO)
MediaFormat("OGG", "ogg", "audio", "audio/ogg", ".ogg", NULL_VIDEO, OGG_AUDIO)
MediaFormat("OPUS", "Opus", "audio", "audio/ogg", ".opus", NULL_VIDEO, OPUS_AUDIO)
MediaFormat("MP4", "mp4", "video", "video/mp4", ".mp4", MP4_VIDEO, MP4_AUDIO)
MediaFormat("WEBM", "WebM", "video", "video/webm", ".webm", WEBM_VIDEO, WEBM_AUDIO)
