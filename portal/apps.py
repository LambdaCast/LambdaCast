from django.apps import AppConfig
import django.core.exceptions as exceptions

import os

import lambdaproject.settings as settings

class Portal(AppConfig):
    name = 'portal'
    verbose_name = 'Portal'
    
    def ready(self):
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT)
        elif not os.path.isdir(settings.FILE_UPLOAD_TEMP_DIR):
            os.makedirs(settings.FILE_UPLOAD_TEMP_DIR)
        elif not os.path.isdir(settings.ENCODING_OUTPUT_DIR):
            os.makedirs(settings.ENCODING_OUTPUT_DIR)
