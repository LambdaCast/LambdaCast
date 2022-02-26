# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
import taggit.managers
from django.conf import settings
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, help_text='Slugs are parts of an URL that you can define', unique=True, verbose_name='Slug')),
                ('description', models.TextField(help_text='Describe the topic or content of the channel', max_length=1000, null=True, verbose_name='Description', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('featured', models.BooleanField(default=False, verbose_name='Featured')),
                ('channelThumbURL', models.URLField(help_text='Use a picture as thumbnail for the RSS-Feed', verbose_name='Channel Thumb URL', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40, verbose_name='Title')),
                ('description', models.TextField(max_length=1000, verbose_name='Description')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, help_text='Slugs are parts of an URL that you can define', unique=True, verbose_name='Slug')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('channel', models.ForeignKey(blank=True, to='portal.Channel', help_text='Channels you want to add to your collection', null=True)),
            ],
            options={
                'verbose_name': 'Collection',
                'verbose_name_plural': 'Collections',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('ip', models.GenericIPAddressField(help_text='The IP of the one who posted the comment', null=True, verbose_name=b'IP', blank=True)),
                ('moderated', models.BooleanField(default=False, verbose_name='Moderated')),
                ('timecode', models.DecimalField(null=True, verbose_name='Timecode', max_digits=10, decimal_places=2, blank=True)),
                ('comment', models.TextField(max_length=1000, verbose_name='Comment')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Hotfolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activated', models.BooleanField(default=False, verbose_name='Activated')),
                ('folderName', models.CharField(help_text='Set a folder you can add media in and then get it automatically listed in LambdaCast', max_length=30, verbose_name='Name of the folder')),
                ('defaultName', models.CharField(max_length=30, verbose_name='Title', blank=True)),
                ('description', models.TextField(max_length=1000, null=True, verbose_name='Description', blank=True)),
                ('autoPublish', models.BooleanField(default=False, verbose_name='Auto-Publish')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('channel', models.ForeignKey(verbose_name='Channel', to='portal.Channel', help_text='The media in the folder will be added to the channel automatically')),
            ],
            options={
                'verbose_name': 'Hotfolder',
                'verbose_name_plural': 'Hotfolder',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('url', models.URLField(help_text='Insert the link to the media file', max_length=512, verbose_name='URL to Transcoded File')),
                ('file_format', models.CharField(default=b'MP3', help_text='File format of the media file', max_length=20, verbose_name='File Format', choices=[(b'MP3', b'mp3'), (b'OGG', b'ogg'), (b'OPUS', b'Opus'), (b'MP4', b'mp4'), (b'WEBM', b'WebM')])),
                ('size', models.BigIntegerField(null=True, verbose_name='File Size in Bytes', blank=True)),
                ('mediatype', models.CharField(default=b'audio', help_text='File type of the media file (audio or video)', max_length=20, verbose_name='Media Type', choices=[(b'audio', b'audio'), (b'video', b'video')])),
            ],
            options={
                'verbose_name': 'Media File',
                'verbose_name_plural': 'Media Files',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MediaItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, help_text='Slugs are parts of an URL that you can define', unique=True, verbose_name='Slug')),
                ('date', models.DateField(help_text='Upload or record date', verbose_name='Date', auto_now=True)),
                ('description', models.TextField(help_text='Insert a description to the media. You can use Markdown to add formatting', verbose_name='Description', blank=True)),
                ('license', models.CharField(default=b'CC-BY', help_text='Rights the viewer/listener has', max_length=200, verbose_name='License', choices=[(b'None', 'No License'), (b'CC0', 'Public Domain/CC0'), (b'CC-BY', 'CreativeCommons - Attribution'), (b'CC-BY-NC', 'CreativeCommons - Attribution - NonCommercial'), (b'CC-BY-NC-ND', 'CreativeCommons - Attribution - NonCommercial - NoDerivs'), (b'CC-BY-ND', 'CreativeCommons - Attribution - NoDerivs')])),
                ('linkURL', models.URLField(help_text='Insert a link to a blog or website that relates to the media', verbose_name='Link', blank=True)),
                ('torrentURL', models.URLField(help_text='The URL to the torrent-file', verbose_name='Torrent-URL', blank=True)),
                ('videoThumbURL', models.URLField(help_text='Use a picture as thumbnail for the media list', verbose_name='Video Thumb-URL', blank=True)),
                ('audioThumbURL', models.URLField(help_text='Use a picture as cover for the media list', verbose_name='Audio Cover-URL', blank=True)),
                ('duration', models.DecimalField(decimal_places=2, max_digits=10, blank=True, help_text='The length of the media', null=True, verbose_name='Duration')),
                ('autoPublish', models.BooleanField(default=True, verbose_name='Auto-Publish')),
                ('published', models.BooleanField(default=False, verbose_name='Published')),
                ('encodingDone', models.BooleanField(default=False, verbose_name='Encoding done')),
                ('torrentDone', models.BooleanField(default=False, verbose_name='Torrent done')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
                ('originalFile', models.FileField(upload_to=b'raw/%Y/%m/%d/', max_length=2048, verbose_name='File')),
                ('channel', models.ForeignKey(blank=True, to='portal.Channel', help_text='Channels are used to order your media', null=True, verbose_name='Channel')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='Insert what the media item is about in short terms divided by commas', verbose_name='Tags')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Shows which user made or uploaded the media item', null=True, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Media Item',
                'verbose_name_plural': 'Media Items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Submittal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title of the submittal')),
                ('description', models.TextField(help_text='Insert a sample description to the media. You can use Markdown to add formatting', verbose_name='Description of the submittal', blank=True)),
                ('media_title', models.CharField(max_length=200, verbose_name='Title')),
                ('media_description', models.TextField(help_text='Insert a sample description to the media. You can use Markdown to add formatting', verbose_name='Description', blank=True)),
                ('media_license', models.CharField(default=b'CC-BY', help_text='Rights the viewer/listener has', max_length=200, verbose_name='License', choices=[(b'None', 'No License'), (b'CC0', 'Public Domain/CC0'), (b'CC-BY', 'CreativeCommons - Attribution'), (b'CC-BY-NC', 'CreativeCommons - Attribution - NonCommercial'), (b'CC-BY-NC-ND', 'CreativeCommons - Attribution - NonCommercial - NoDerivs'), (b'CC-BY-ND', 'CreativeCommons - Attribution - NoDerivs')])),
                ('media_linkURL', models.URLField(help_text='Insert a link to a blog or website that relates to the media', verbose_name='Link', blank=True)),
                ('media_torrentURL', models.URLField(help_text='The URL to the torrent-file', verbose_name='Torrent-URL', blank=True)),
                ('media_mp4URL', models.URLField(help_text='Add the link of the media folder or any other one with .mp4 ending', verbose_name='MP4-URL', blank=True)),
                ('media_webmURL', models.URLField(help_text='Add the link of the media folder or any other one with .webm ending', verbose_name='WEBM-URL', blank=True)),
                ('media_mp3URL', models.URLField(help_text='Add the link of the media folder or any other one with .mp3 ending', verbose_name='MP3-URL', blank=True)),
                ('media_oggURL', models.URLField(help_text='Add the link of the media folder or any other one with .ogg ending', verbose_name='OGG-URL', blank=True)),
                ('media_opusURL', models.URLField(help_text='Add the link of the media folder or any other one with .opus ending', verbose_name='OPUS-URL', blank=True)),
                ('media_videoThumbURL', models.URLField(help_text='Use a picture as thumbnail', verbose_name='Video Thumb-URL', blank=True)),
                ('media_audioThumbURL', models.URLField(help_text='Use a picture as cover', verbose_name='Audio Cover-URL', blank=True)),
                ('media_published', models.BooleanField(default=False, verbose_name='Published')),
                ('media_torrentDone', models.BooleanField(default=False, verbose_name='Torrent done')),
                ('media_channel', models.ForeignKey(blank=True, to='portal.Channel', help_text='Channels are used to order your media', null=True, verbose_name='Channel')),
                ('media_tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='Insert what the media item is about in short terms divided by commas', verbose_name='Tags')),
                ('users', models.ManyToManyField(help_text='User who use the submittal and get it shown on frontpage', to=settings.AUTH_USER_MODEL, null=True, verbose_name='Users of the submittal', blank=True)),
            ],
            options={
                'verbose_name': 'Submittal',
                'verbose_name_plural': 'Submittals',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='mediafile',
            name='media_item',
            field=models.ForeignKey(help_text='Media Item the file is connected to', to='portal.MediaItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='item',
            field=models.ForeignKey(verbose_name='Media Item', to='portal.MediaItem'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='collection',
            name='items',
            field=models.ManyToManyField(help_text='Media you want to add to your collection', to='portal.MediaItem', verbose_name='Media Item'),
            preserve_default=True,
        ),
    ]
