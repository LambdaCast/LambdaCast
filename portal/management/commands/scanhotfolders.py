from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from portal.models import *
import portal.appsettings as settings
import djangotasks
import datetime
import shutil
import os
import time

class Command(BaseCommand):
    args = ''
    help = _(u'Gets new media out of hotfolders')
    def handle(self, *args, **options):
        now = time.time()
        five_minutes_ago = now - 60*2
        hotfolders = Hotfolder.objects.filter(activated=True)
        for folder in hotfolders:
            self.stdout.write(_(u'This is folder "%s"\n') % folder.folderName)
            os.chdir(settings.HOTFOLDER_BASE_DIR + folder.folderName)
            for file in os.listdir("."):
                st=os.stat(file)
                mtime=st.st_mtime
                if mtime < five_minutes_ago:
                    if file.endswith(".mov") or file.endswith(".mp4") or file.endswith(".avi") or file.endswith(".ogv") or file.endswith(".m4v") or file.endswith(".mp3") or file.endswith(".ogg"):
                        self.stdout.write(_(u'Using file %s\n') % file) 
                        mediaitem = MediaItem(title=folder.defaultName,date=datetime.date.today(),description=folder.description,kind=folder.kind,channel=folder.channel,autoPublish=folder.autoPublish)
                        mediaitem.save()
                        shutil.copy(settings.HOTFOLDER_BASE_DIR + folder.folderName + '/' + file, settings.HOTFOLDER_MOVE_TO_DIR)
                        mediaitem.originalFile = settings.HOTFOLDER_MOVE_TO_DIR + file
                        mediaitem.save()
                        os.remove(settings.HOTFOLDER_BASE_DIR + folder.folderName + '/' + file)
                        djangotasks.register_task(mediaitem.encode_media, _(u"Encode the files using ffmpeg"))
                        encoding_task = djangotasks.task_for_object(mediaitem.encode_media)
                        djangotasks.run_task(encoding_task)
                        if settings.USE_BITTORRENT:
                            djangotasks.register_task(mediaitem.create_bittorrent, _(u"Create Bittorrent file for media and serve via Bittorrent"))
                            torrent_task = djangotasks.task_for_object(mediaitem.create_bittorrent)
                            djangotasks.run_task(torrent_task)
