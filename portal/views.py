# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.response import TemplateResponse

from portal.models import MediaItem, Comment, Channel, Collection, Submittal, MediaFile
from portal.forms import MediaItemForm, CommentForm, getThumbnails, ThumbnailForm, SubmittalForm
from portal.media_formats import MEDIA_FORMATS

from taggit.models import Tag
import lambdaproject.settings as settings

import djangotasks

import os
import re
from operator import attrgetter
import itertools
from sets import Set

def index(request):
    ''' This view is the front page of OwnTube. It just gets the first 15 available media items and
    forwards them to the template. We use Django's Paginator to have pagination '''
    if request.user.is_authenticated():
        queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True).order_by('-date','-modified'),Collection.objects.all().order_by('-created'))
    else:
        queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True, published=True).order_by('-date','-modified'),Collection.objects.all().order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,16)
    channel_list = Channel.objects.all()
    page = request.GET.get('page')
    rss_list = []
    for file_type in MEDIA_FORMATS:
        rss_list.append((MEDIA_FORMATS[file_type].format_key,MEDIA_FORMATS[file_type].mediatype,"/feeds/latest/"+file_type))
    rss_list.append(('torrent','torrent','/feeds/latest/torrent'))
    try:
        mediaitems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mediaitems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mediaitems = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'portal/index.html', {'latest_mediaitems_list': mediaitems, 'channel_list': channel_list, 'rss_list': rss_list})

def channel_list(request,slug):
    ''' This view is the view for the channel's list it works almost like the index view'''
    channel = get_object_or_404(Channel, slug=slug)
    if request.user.is_authenticated():
        queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True, channel__slug=slug).order_by('-date','-modified'),Collection.objects.filter(channel__slug=slug).order_by('-created'))
    else:
        queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True, published=True, channel__slug=slug).order_by('-date','-modified'),Collection.objects.filter(channel__slug=slug).order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,15)
    channel_list = Channel.objects.all()
    page = request.GET.get('page')
    rss_list = []
    for file_type in MEDIA_FORMATS:
        rss_list.append((MEDIA_FORMATS[file_type].format_key,MEDIA_FORMATS[file_type].mediatype,"/feeds/"+channel.slug+"/"+file_type))
    rss_list.append(('torrent','torrent','/feeds/'+channel.slug+'/torrent'))
    try:
        mediaitems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mediaitems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mediaitems = paginator.page(paginator.num_pages)
    return TemplateResponse(request, 'portal/channel.html', {'mediaitems_list': mediaitems, 'channel': channel, 'channel_list': channel_list, 'rss_list': rss_list})

def detail(request, slug):
    ''' Handles the detail view of a media item (the player so to say) and handles the comments (this should become nicer with AJAX and stuff)'''
    mediaitem = get_object_or_404(MediaItem, slug=slug)
    if request.user.is_authenticated(): 
        comment_list = Comment.objects.filter(item=mediaitem).order_by('-created')
    else:
        comment_list = Comment.objects.filter(item=mediaitem,moderated=True).order_by('-created')

    if request.method == 'POST':
        comment = Comment(item=mediaitem,ip=request.META["REMOTE_ADDR"])
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            message = _(u"Your comment will be moderated")
            comment.send_notification_mail()
            return TemplateResponse(request, 'portal/items/detail.html', {'comment_list': comment_list, 'mediaitem': mediaitem, 'comment_form': CommentForm(), 'message': message})
        else:
            return TemplateResponse(request, 'portal/items/detail.html', {'comment_list': comment_list, 'mediaitem': mediaitem, 'comment_form': form})
    else:
        form = CommentForm()
        return TemplateResponse(request, 'portal/items/detail.html', {'mediaitem': mediaitem, 'comment_list': comment_list, 'comment_form': form})

def iframe(request, slug):
    ''' Returns an iframe for a item so that media items can be shared easily '''
    mediaitem = get_object_or_404(MediaItem, slug=slug)
    return TemplateResponse(request, 'portal/items/iframe.html', {'mediaitem': mediaitem})

def tag(request, tag):
    ''' Gets all media items for a specified tag'''
    if request.user.is_authenticated():
        mediaitemslist = MediaItem.objects.filter(encodingDone=True, tags__slug__in=[tag]).order_by('-date')
    else:
        mediaitemslist = MediaItem.objects.filter(encodingDone=True, published=True, tags__slug__in=[tag]).order_by('-date')
    tag_name = get_object_or_404(Tag, slug=tag)
    return TemplateResponse(request, 'portal/items/list.html', {'mediaitems_list': mediaitemslist, 'tag': tag_name})

def collection(request, slug):
    ''' Gets all media items for a channel'''
    collection = get_object_or_404(Collection, slug=slug)
    rss_list = []
    for file_type in MEDIA_FORMATS:
        rss_list.append((MEDIA_FORMATS[file_type].format_key,MEDIA_FORMATS[file_type].mediatype,"/feeds/collection/"+collection.slug+"/"+file_type))
    if request.user.is_authenticated():
        mediaitemslist = collection.items.filter(encodingDone=True)
    else:
        mediaitemslist = collection.items.filter(encodingDone=True, published=True)
    return TemplateResponse(request, 'portal/collection.html', {'mediaitems_list': mediaitemslist, 'collection': collection, 'rss_list': rss_list })

def search(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and _get_query)'''
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = _get_query(query_string, ['title', 'description', 'tags__name'])

        if request.user.is_authenticated():
            found_entries = MediaItem.objects.filter(entry_query).order_by('-date')
        else:
            found_entries = MediaItem.objects.filter(entry_query, published=True).order_by('-date')

    return TemplateResponse(request, 'portal/search_results.html', { 'query_string': query_string, 'mediaitems_list': found_entries})

def search_json(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and _get_query)'''
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = _get_query(query_string, ['title', 'description','tags__name'])

        found_entries = MediaItem.objects.filter(entry_query).order_by('-date')

    data = serializers.serialize('json', found_entries)
    return HttpResponse(data, content_type = 'application/javascript; charset=utf8')
           
def tag_json(request, tag):
    mediaitemslist = MediaItem.objects.filter(encodingDone=True, published=True, tags__name__in=[tag]).order_by('-date')
    data = serializers.serialize('json', mediaitemslist)
    return HttpResponse(data, content_type = 'application/javascript; charset=utf8')

@login_required
def submittal(request, subm_id):
    submittal = get_object_or_404(Submittal, pk = subm_id)
    if request.method == 'POST':
        form = SubmittalForm(request.POST)
        if form.is_valid():
            mediaitem = form.save()
            mediaitem.user = request.user
            mediaitem.save()
            form.create_mediafiles(mediaitem)
            mediaitem.get_and_save_duration()
            return redirect(index)
        else:
            return TemplateResponse(request, 'portal/submittal.html', {'submittal_form': form, 'submittal': submittal})
    else:
        form = SubmittalForm(initial={
            'title': submittal.media_title,
            'description': submittal.media_description,
            'channel': submittal.media_channel,
            'license': submittal.media_license,
            'linkURL': submittal.media_linkURL,
            'torrentURL': submittal.media_torrentURL,
            'media_mp3URL': submittal.media_mp3URL,
            'media_oggURL': submittal.media_oggURL,
            'media_opusURL':  submittal.media_opusURL,
            'videoThumbURL': submittal.media_videoThumbURL,
            'audioThumbURL': submittal.media_audioThumbURL,
            'published': submittal.media_published,
            'tags': ", ".join(str(x) for x in  submittal.media_tags.all()),
            'torrentDone': submittal.media_torrentDone,
            'encodingDone': True,
        })
        return TemplateResponse(request, 'portal/submittal.html', {'submittal_form': form, 'submittal': submittal})

@login_required
def upload_thumbnail(request):
    if request.method == 'POST':
        form = ThumbnailForm(request.POST, request.FILES or None)
        if form.is_valid():
            if (request.FILES['file'].content_type == 'image/png' or request.FILES['file'].content_type == 'image/jpeg') and not form.data['title'] == '':
                _handle_uploaded_thumbnail(request.FILES['file'], form.data['title'])
                message = _("The upload of %s was successful") % (form.data['title'])
                form = ThumbnailForm()
                return TemplateResponse(request, 'portal/thumbnail.html', {'thumbnail_form': ThumbnailForm(), 'thumbs_list':_get_thumbnails_list, 'message': message})
            else:
                error = _("Please upload an image file")
                return TemplateResponse(request, 'portal/thumbnail.html', {'thumbnail_form': form, 'thumbs_list':_get_thumbnails_list, 'error': error})

        else:
            return TemplateResponse(request, 'portal/thumbnail.html', {'thumbnail_form': form, 'thumbs_list':_get_thumbnails_list})
    else:
        return TemplateResponse(request, 'portal/thumbnail.html', {'thumbnail_form': ThumbnailForm(), 'thumbs_list':_get_thumbnails_list})

def _handle_uploaded_thumbnail(f, filename):
    suffix = '.png' if (f.content_type == 'image/png') else '.jpg'
    suffix = '' if (filename.endswith(suffix)) else suffix
    destination = open(settings.THUMBNAILS_DIR + filename + suffix, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

@login_required
def submit(request):
    ''' The view for uploading the items. Only authenticated users can upload media items!
    We use django tasks to make a new task task for encoding this items. If we use 
    bittorrent to distribute our files we also use django tasks to make the .torrent 
    files (this can take a few minutes for very large files '''
    if request.method == 'POST':
        form = MediaItemForm(request.POST, request.FILES or None)
        if form.is_valid():
            media_item = form.save()
            if form.cleaned_data['thumbURL']:
                media_item.audioThumbURL = form.cleaned_data['thumbURL']
                media_item.videoThumbURL = form.cleaned_data['thumbURL']
            media_item.user = request.user
            media_item.save()
            media_item.get_and_save_duration()

            outputdir = settings.ENCODING_OUTPUT_DIR + media_item.slug
            if not os.path.exists(outputdir):
                os.makedirs(outputdir)

            cover_task = djangotasks.task_for_object(media_item.get_and_save_cover)
            djangotasks.run_task(cover_task)

            for target_format in form.cleaned_data['fileFormats']:
                media_format = MEDIA_FORMATS[target_format]
                url = settings.ENCODED_BASE_URL + media_item.slug + '/' + media_item.slug + media_format.extension
                media_file = MediaFile.objects.create(title=media_item.title + " " + media_format.text,
                                                      url=url, file_format=media_format.format_key,
                                                      media_item=media_item, mediatype=media_format.mediatype)
                encoding_task = djangotasks.task_for_object(media_file.encode_media)
                djangotasks.run_task(encoding_task)

            if settings.USE_BITTORRENT:
                torrent_task = djangotasks.task_for_object(media_item.create_bittorrent)
                djangotasks.run_task(torrent_task)
            return redirect(index)

        return TemplateResponse(request, 'portal/submit.html', {'submit_form': form})
    else:
        form = MediaItemForm()
        return TemplateResponse(request, 'portal/submit.html', {'submit_form': form})

@login_required
def status(request):
    tasks_mediaitem = djangotasks.models.Task.objects.filter(model="portal.mediaitem").exclude(status="successful")
    tasks_mediafile = djangotasks.models.Task.objects.filter(model="portal.mediafile").exclude(status="successful")

    mediaitem_ids = Set(map((lambda mediaitem: mediaitem.object_id), tasks_mediaitem))
    for mediafile in tasks_mediafile:
        try:
            mediaitem_ids.add(MediaFile.objects.get(pk=mediafile.object_id).media_item.pk)
        except MediaFile.DoesNotExist:
            pass

    mediaitems = MediaItem.objects.filter(pk__in=mediaitem_ids)
    return TemplateResponse(request, 'portal/status.html', {'mediaitems': mediaitems})

def _normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> _normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def _get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    '''
    query = None # Query to search for every search term        
    terms = _normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def _get_thumbnails_list():
    thumbnails_list = getThumbnails(settings.THUMBNAILS_DIR)
    del thumbnails_list[0]
    return thumbnails_list
