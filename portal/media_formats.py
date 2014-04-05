'''
Created on Apr 5, 2014

@author: benjamin
'''

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

    def __init__(self, format_key, mediatype, mime_type):
        self.format_key = format_key
        self.mediatype = mediatype
        self.mime_type = mime_type
        MEDIA_FORMATS[format_key] = self

MediaFormat("MP3", "audio", "audio/mp3")
MediaFormat("OGG", "audio", "audio/ogg")
MediaFormat("OPUS", "audio", "audio/ogg")
MediaFormat("MP4", "video", "video/mp4")
MediaFormat("WEBM", "video", "video/webm")