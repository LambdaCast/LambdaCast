# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import autoslug.fields
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Stream title')),
                ('slug', autoslug.fields.AutoSlugField(editable=False, help_text='Slugs are parts of an URL that you can define', unique=True, verbose_name='Slug')),
                ('startDate', models.DateTimeField(verbose_name='Beginning of the event')),
                ('endDate', models.DateTimeField(verbose_name='End of the event')),
                ('description', models.TextField(verbose_name='Description')),
                ('link', models.URLField(verbose_name='Link', blank=True)),
                ('rtmpLink', models.URLField(help_text='RTMP is a protocol to stream video. If you have a server as host, you can insert a link of the output', verbose_name='RTMP Link', blank=True)),
                ('audioOnlyLink', models.URLField(verbose_name='Audio-only Link', blank=True)),
                ('iframe', models.TextField(verbose_name='iFrame of the Stream')),
                ('published', models.BooleanField(default=False, verbose_name='Published')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modified')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
