from django.shortcuts import render_to_response, get_object_or_404, redirect
from django import forms
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic.list_detail import object_list
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from pages.models import Page
from portal.models import MediaItem, Comment, Channel, Collection, User, Submittal
from portal.forms import MediaItemForm, CommentForm, getThumbnails, ThumbnailForm, SubmittalForm

from transloadit.client import Client
from taggit.models import Tag
import lambdaproject.settings as settings

import djangotasks

import simplejson as json
import urllib2
from datetime import datetime
import os
import shutil
import re
from threading import Event
from traceback import print_exc
from sys import argv
from operator import attrgetter
import itertools

def list(request):
    ''' This view is the front page of OwnTube. It just gets the first 15 available media items and
    forwards them to the template. We use Django's Paginator to have pagination '''
    queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True, published=True).order_by('-date','-modified'),Collection.objects.all().order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,15)
    channel_list = Channel.objects.all()
    page = request.GET.get('page')
    try:
        mediaitems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mediaitems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mediaitems = paginator.page(paginator.num_pages)
    return render_to_response('portal/index.html', {'page_list': get_page_list, 'submittal_list':get_submittal_list(request), 'latest_mediaitem_list': mediaitems, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def channel_list(request,slug):
    ''' This view is the view for the channel's list it works almost like the index view'''
    channel = get_object_or_404(Channel, slug=slug)
#    mediaitems_list = MediaItem.objects.filter(encodingDone=True, published=True, channel__slug=slug).order_by('-date','-modified')
    queryset = itertools.chain(MediaItem.objects.filter(encodingDone=True, published=True, channel__slug=slug).order_by('-date','-modified'),Collection.objects.filter(channel__slug=slug).order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,15)
    channel_list = Channel.objects.all()
    page = request.GET.get('page')
    try:
        mediaitems = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        mediaitems = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        mediaitems = paginator.page(paginator.num_pages)
    return render_to_response('portal/channel.html', {'page_list':get_page_list, 'submittal_list':get_submittal_list(request), 'mediaitems_list': mediitems, 'channel': channel, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def detail(request, slug):
    ''' Handles the detail view of a media item (the player so to say) and handles the comments (this should become nicer with AJAX and stuff)'''
    if request.method == 'POST':
        comment = Comment(video=MediaItem.objects.get(slug=slug),ip=request.META["REMOTE_ADDR"])
        mediaitem = get_object_or_404(MediaItem, slug=slug)
        emptyform = CommentForm()
        form = CommentForm(request.POST, instance=comment)
        comments = Comment.objects.filter(moderated=True, video=mediaitem).order_by('-created')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            message = _(u"Your comment will be moderated")
            user_mediaitem = mediaitem.user
            if not user_mediaitem.email == '':
                if not user_mediaitem.first_name == '':
                    mail_message = _(u'Hello %s,\n\nsomeone commented under one of your videos/audios. Please check and moderate it, so others can see the comment.\n\nThank You.') % user_mediaitem.first_name
                else:
                    mail_message = _(u'Hello %s,\n\nsomeone commented under one of your videos/audios. Please check and moderate it, so others can see the comment.\n\nThank You.') % user_mediaitem.username
                user_mediaitem.email_user(_(u'New Comment: ') + mediaitem.title, mail_message)
            return render_to_response('portal/items/detail.html', {'page_list':get_page_list,'mediaitem': mediaitem, 'comment_form': emptyform, 'comments': comments, 'message': message, 'settings': settings}, context_instance=RequestContext(request))
        else:
            return render_to_response('portal/items/detail.html', {'page_list':get_page_list,'mediaitem': mediaitem, 'comment_form': form, 'comments': comments, 'settings': settings}, context_instance=RequestContext(request))
                    
    else:
        mediaitem = get_object_or_404(MediaItem, slug=slug)
        form = CommentForm()
        comments = Comment.objects.filter(moderated=True, video=mediaitem).order_by('-created')
        return render_to_response('portal/items/detail.html', {'mediaitem': mediaitem, 'page_list':get_page_list, 'submittal_list':get_submittal_list(request), 'comment_form': form, 'comments': comments, 'settings': settings},
                            context_instance=RequestContext(request))

def iframe(request, slug):
    ''' Returns an iframe for a item so that media items can be shared easily '''
    mediaitem = get_object_or_404(MediaItem, slug=slug)
    return render_to_response('portal/items/iframe.html', {'mediaitem': mediaitem, 'settings': settings, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list}, context_instance=RequestContext(request))


def tag(request, tag):
    ''' Gets all media items for a specified tag'''
    mediaitemslist = MediaItem.objects.filter(encodingDone=True, published=True, tags__slug__in=[tag]).order_by('-date')
    tag_name = get_object_or_404(Tag, slug=tag)
    return render_to_response('portal/items/list.html', {'mediaitems_list': mediaitemslist, 'tag':tag_name, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list,'settings': settings},
                            context_instance=RequestContext(request))

def collection(request, slug):
    ''' Gets all media items for a channel'''
    collection = get_object_or_404(Collection, slug=slug)
    mediaitemslist = collection.videos.filter(encodingDone=True, published=True)
    return render_to_response('portal/collection.html', {'mediaitems_list': mediaitemslist, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list,'collection':collection, 'settings': settings},
                            context_instance=RequestContext(request))
                            
def search(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and get_query)'''
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['title', 'description', 'tags__name'])
        
        found_entries = MediaItem.objects.filter(entry_query).order_by('-date')

    return render_to_response('portal/search_results.html',
                          { 'query_string': query_string, 'mediaitems_list': found_entries, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list, 'settings': settings},
                          context_instance=RequestContext(request))

def search_json(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and get_query)'''
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'description','tags__name'])

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
            cmodel = form.save()
            cmodel.user = request.user
            cmodel.save()
            return redirect(list)
        else:
            return render_to_response('portal/submittal.html', {'submittal_form': form, 'submittal': submittal, 'settings': settings, 'page_list':get_page_list, 'submittal_list':get_submittal_list(request)}, context_instance=RequestContext(request))
    else:
        form = SubmittalForm(initial={
            'title': submittal.media_title,
            'date': datetime.now(),
            'description': submittal.media_description,
            'channel': submittal.media_channel,
            'license': submittal.media_license,
            'linkURL': submittal.media_linkURL,
            'kind': submittal.media_kind,
            'torrentURL': submittal.media_torrentURL,
            'mp4URL': submittal.media_mp4URL,
            'webmURL': submittal.media_webmURL,
            'mp3URL': submittal.media_mp3URL,
            'oggURL': submittal.media_oggURL,
            'videoThumbURL': submittal.media_videoThumbURL,
            'audioThumbURL': submittal.media_audioThumbURL,
            'published': submittal.media_published,
            'tags': ", ".join(str(x) for x in  submittal.media_tags.all()),
            'torrentDone': submittal.media_torrentDone,
            'encodingDone': True,
        })
        return render_to_response('portal/submittal.html', {'submittal_form': form, 'submittal': submittal, 'settings': settings, 'page_list':get_page_list, 'submittal_list':get_submittal_list(request)}, context_instance=RequestContext(request))

@login_required
def upload_thumbnail(request):
    if request.method == 'POST':
        form = ThumbnailForm(request.POST, request.FILES or None)
        if form.is_valid():
            if (request.FILES['file'].content_type == 'image/png' or request.FILES['file'].content_type == 'image/jpeg') and not form.data['title'] == '':
                handle_uploaded_thumbnail(request.FILES['file'], form.data['title'])
                message = _("The upload of %s was successful") % (form.data['title'])
                form = ThumbnailForm()
                return render_to_response('portal/thumbnail.html', {'thumbnail_form': ThumbnailForm(), 'settings': settings, 'page_list':get_page_list, 'thumbs_list':get_thumbnails_list, 'message': message}, context_instance=RequestContext(request))
            else:
                error = _("Please upload an image file")
                return render_to_response('portal/thumbnail.html', {'thumbnail_form': form, 'settings': settings, 'page_list':get_page_list, 'thumbs_list':get_thumbnails_list, 'error': error}, context_instance=RequestContext(request))

        else:
            return render_to_response('portal/thumbnail.html', {'thumbnail_form': ThumbnailForm(), 'settings': settings, 'page_list':get_page_list, 'thumbs_list':get_thumbnails_list}, context_instance=RequestContext(request))
    else:
        return render_to_response('portal/thumbnail.html', {'thumbnail_form': ThumbnailForm(), 'settings': settings, 'page_list':get_page_list, 'thumbs_list':get_thumbnails_list}, context_instance=RequestContext(request))
    
def handle_uploaded_thumbnail(f, filename):
    suffix = '.png' if (f.content_type == 'image/png') else '.jpg'
    suffix = '' if (filename.endswith(suffix)) else suffix
    destination = open('media/thumbnails/' + filename + suffix, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

@login_required
def submit(request):
    ''' The view for uploading the items. Only authenticated users can upload media items!
    If we use transloadit to encode the items we use the more or less official python
    "API" to ask transloadit to transcode our files otherwise we use django tasks to make
    a new task task for encoding this items. If we use bittorrent to distribute our files
    we also use django tasks to make the .torrent files (this can take a few minutes for
    very large files '''
    if request.method == 'POST':
        form = MediaItemForm(request.POST, request.FILES or None)
        if form.is_valid():
            cmodel = form.save()
            cmodel.audioThumbURL = form.data['thumbURL']
            cmodel.videoThumbURL = form.data['thumbURL']
            if cmodel.originalFile:
                if settings.USE_TRANLOADIT:
                    client = Client(settings.TRANSLOAD_AUTH_KEY, settings.TRANSLOAD_AUTH_SECRET)
                    params = None
                    if (cmodel.kind==0):
                        params = {
                            'steps': {
                                ':original': {
                                    'robot': '/http/import',
                                    'url': cmodel.originalFile.url,
                                }
                            },
                            'template_id': settings.TRANSLOAD_TEMPLATE_VIDEO_ID,
                            'notify_url': settings.TRANSLOAD_NOTIFY_URL
                        }
                    if (cmodel.kind==1):
                        params = {
                            'steps': {
                                ':original': {
                                    'robot': '/http/import',
                                    'url': cmodel.originalFile.url,
                                }
                            },
                            'template_id': settings.TRANSLOAD_TEMPLATE_AUDIO_ID,
                            'notify_url': settings.TRANSLOAD_NOTIFY_URL
                        }
                    if (cmodel.kind==2):
                        params = {
                            'steps': {
                                ':original': {
                                    'robot': '/http/import',
                                    'url': cmodel.originalFile.url,
                                }
                            },
                            'template_id': settings.TRANSLOAD_TEMPLATE_VIDEO_AUDIO_ID,
                            'notify_url': settings.TRANSLOAD_NOTIFY_URL
                        }
                    result = client.request(**params)
                    cmodel.assemblyid = result['assembly_id']
                    cmodel.published = cmodel.autoPublish
                    cmodel.encodingDone = False
                    cmodel.save()
                else:
                    cmodel.save()
                    djangotasks.register_task(cmodel.encode_media, "Encode the files using ffmpeg")
                    encoding_task = djangotasks.task_for_object(cmodel.encode_media)
                    djangotasks.run_task(encoding_task)
            if settings.USE_BITTORRENT:
                djangotasks.register_task(cmodel.create_bittorrent, "Create Bittorrent file for item and serve it")
                torrent_task = djangotasks.task_for_object(cmodel.create_bittorrent)
                djangotasks.run_task(torrent_task)
            cmodel.user = request.user
            cmodel.save()
            return redirect(list)

        return render_to_response('portal/submit.html',
                                {'submit_form': form, 'settings': settings,'submittal_list':get_submittal_list(request), 'page_list':get_page_list},
                                context_instance=RequestContext(request))
    else:
        form = MediaItemForm()
        return render_to_response('portal/submit.html',
                                {'submit_form': form, 'settings': settings,'submittal_list':get_submittal_list(request), 'page_list':get_page_list},
                                context_instance=RequestContext(request))

@login_required
def status(request):
    if settings.USE_BITTORRENT:
        processing_items = MediaItem.objects.filter(Q(encodingDone=False) | Q(torrentDone=False))
    else:
        processing_items = MediaItem.objects.filter(encodingDone=False)
    running_tasks = []
    for mediaitem in processing_items:
        tasks = djangotasks.models.Task.objects.filter(model="portal.mediaitem", object_id=mediaitem.pk)
        running_tasks.append(tasks)
    return render_to_response('portal/status.html',
                                    {'processing_items': processing_items, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list, 'running_tasks': running_tasks, 'settings': settings},
                                    context_instance=RequestContext(request))

@csrf_exempt
def encodingdone(request):
    ''' This is a somewhat special view: It is called by transloadit to tell
    LambdaCast that the encoding process is done. The view then parses the
    JSON data in the POST request send by transloadit and than get this information
    into our media item model. Of course it can be possible for attackers to alter items
    using for example curl but they would need to guess a assembly_id and these are 
    quite long hex strings. To improve the security we could also use the custom header
    option from transloadit but I think this wouldn't really help in a open source project'''
    if request.method == 'POST':
        data = json.loads(request.POST['transloadit'])
        try:
            mediaitem = MediaItem.objects.get(assemblyid=data['assembly_id'])
            if (mediaitem.kind == 0):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP4_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.mp4URL = resultFirst['url']
                mediaitem.mp4Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                mediaitem.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_WEBM_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.webmURL = resultFirst['url']
                mediaitem.webmSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_THUMB_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.videoThumbURL = resultFirst['url']
            elif (mediaitem.kind == 1):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP3_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.mp3URL = resultFirst['url']
                mediaitem.mp3Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                mediaitem.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_OGG_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.oggURL = resultFirst['url']
                mediaitem.oggSize = resultFirst['size']
            elif (mediaitem.kind == 2):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP4_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.mp4URL = resultFirst['url']
                mediaitem.mp4Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                mediaitem.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_WEBM_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.webmURL = resultFirst['url']
                mediaitem.webmSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_MP3_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.mp3URL = resultFirst['url']
                mediaitem.mp3Size = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_OGG_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.oggURL = resultFirst['url']
                mediaitem.oggSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_THUMB_ENCODE]
                resultFirst = resultItem[0]
                mediaitem.videoThumbURL = resultFirst['url']
            mediaitem.encodingDone = True
            mediaitem.save()
        except MediaItem.DoesNotExist:
            raise Http404
        return HttpResponse(_(u"Media was updated"))
    else:
        raise Http404
    

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
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

def get_thumbnails_list():
    thumbnails_list = getThumbnails(settings.THUMBNAILS_DIR)
    del thumbnails_list[0]
    return thumbnails_list

def get_page_list():
	return Page.objects.filter(activated=True).order_by('orderid')

def get_submittal_list(request):
    return Submittal.objects.filter(users=request.user) if request.user.is_authenticated() else []

