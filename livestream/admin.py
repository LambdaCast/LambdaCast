from livestream.models import Stream
from django.contrib import admin
from lambdaproject import settings

if (settings.ENABLE_LIVESTREAMS):
    admin.site.register(Stream)
