"""

    Presets for the ffmpeg manager

"""

# video

MP4_VIDEO =      {'format':'mp4',
                  'vcodec':'mpeg4',
                  'qmin':'3',
                  'qmax':'5',
                  'g':'300',
                  'bitrate':'700k',
                  'vf':'"scale=-1:360"',
}
MP4_AUDIO =      {'acodec':'libfaac',
                  'rate':'128k'}

WEBM_VIDEO =     {'format':'webm',
                  'vcodec':'libvpx',
                  'vf':'"scale=-1:360"',
                  'bitrate':'700k'}
WEBM_AUDIO =     {'acodec':'libvorbis',
                  'rate':'128k'}

# audio

MP3_AUDIO =      {'format':'mp3',
                  'rate':'128k',
                  'freq':'44100',
                  'channels':'2',
                  'disablevideo':'',}

OGG_AUDIO =      {'format':'ogg',
                  'acodec':'libvorbis',
                  'rate':'128k',
                  'freq':'44100',
                  'channels':'2',
                  'disablevideo':'',}

OPUS_AUDIO =     {'format':'ogg',
                  'acodec':'libopus',
                  'rate':'96k',
                  'freq':'48000',
                  'channels':'2',
                  'disablevideo':'',}

NULL_VIDEO = {}
