from django.shortcuts import render_to_response, get_object_or_404, redirect
from django import forms
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic.list_detail import object_list
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from pages.models import Page
from portal.models import Video, Comment, Channel, Collection, Submittal
from portal.forms import VideoForm, CommentForm, getThumbnails, ThumbnailForm, SubmittalForm
from transloadit.client import Client
from taggit.models import Tag
import lambdaproject.settings as settings

import djangotasks

import simplejson as json
import urllib2
import datetime
import os
import shutil
import re
from threading import Event
from traceback import print_exc
from sys import argv
from operator import attrgetter
import itertools

page_list = Page.objects.filter(activated=True).order_by('orderid')

def list(request):
    ''' This view is the front page of OwnTube. It just gets the first 15 available video and
    forwards them to the template. We use Django's Paginator to have pagination '''
    queryset = itertools.chain(Video.objects.filter(encodingDone=True, published=True).order_by('-date','-modified'),Collection.objects.all().order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,15)
    channel_list = Channel.objects.all()
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        videos = paginator.page(paginator.num_pages)
    return render_to_response('videos/index.html', {'page_list': page_list, 'submittal_list':submittal_list, 'latest_videos_list': videos, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def channel_list(request,slug):
    ''' This view is the view for the channels video list it works almost like the index view'''
    channel = get_object_or_404(Channel, slug=slug)
#    videos_list = Video.objects.filter(encodingDone=True, published=True, channel__slug=slug).order_by('-date','-modified')
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    queryset = itertools.chain(Video.objects.filter(encodingDone=True, published=True, channel__slug=slug).order_by('-date','-modified'),Collection.objects.filter(channel__slug=slug).order_by('-created'))
    queryset_sorted = sorted(queryset, key=attrgetter('date', 'created'), reverse=True)
    paginator = Paginator(queryset_sorted,15)
    channel_list = Channel.objects.all()
    page = request.GET.get('page')
    try:
        videos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        videos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        videos = paginator.page(paginator.num_pages)
    return render_to_response('videos/channel.html', {'page_list':page_list, 'submittal_list':submittal_list, 'videos_list': videos, 'channel': channel, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def detail(request, slug):
    ''' Handles the detail view of a video (the player so to say) and handles the comments (this should become nicer with AJAX and stuff)'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    if request.method == 'POST':
            comment = Comment(video=Video.objects.get(slug=slug),ip=request.META["REMOTE_ADDR"])
            video = get_object_or_404(Video, slug=slug)
            emptyform = CommentForm()
            form = CommentForm(request.POST, instance=comment)
            comments = Comment.objects.filter(moderated=True, video=video).order_by('-created')

            if form.is_valid():
                    human = True
                    comment = form.save(commit=False)
                    comment.save()
                    message = _(u"Your comment will be moderated")
                    return render_to_response('videos/detail.html', {'page_list':page_list, 'submittal_list':submittal_list, 'video': video, 'comment_form': emptyform, 'comments': comments, 'message': message, 'settings': settings}, context_instance=RequestContext(request))
            else:
                    return render_to_response('videos/detail.html', {'page_list':page_list, 'submittal_list':submittal_list, 'video': video, 'comment_form': form, 'comments': comments, 'settings': settings}, context_instance=RequestContext(request))
                    
    else:
        video = get_object_or_404(Video, slug=slug)
        form = CommentForm()
        comments = Comment.objects.filter(moderated=True, video=video).order_by('-created')
        return render_to_response('videos/detail.html', {'video': video, 'page_list':page_list, 'submittal_list':submittal_list, 'comment_form': form, 'comments': comments, 'settings': settings},
                            context_instance=RequestContext(request))

def iframe(request, slug):
    ''' Returns an iframe for a video so that videos can be shared easily '''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    video = get_object_or_404(Video, slug=slug)
    return render_to_response('videos/iframe.html', {'video': video, 'settings': settings, 'submittal_list':submittal_list, 'page_list':page_list}, context_instance=RequestContext(request))


def tag(request, tag):
    ''' Gets all videos for a specified tag'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    videolist = Video.objects.filter(encodingDone=True, published=True, tags__slug__in=[tag]).order_by('-date')
    tag_name = get_object_or_404(Tag, slug=tag)
    return render_to_response('videos/list.html', {'videos_list': videolist, 'tag':tag_name, 'submittal_list':submittal_list, 'page_list':page_list,'settings': settings},
                            context_instance=RequestContext(request))

def collection(request, slug):
    ''' Gets all videos for a channel'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    collection = get_object_or_404(Collection, slug=slug)
    videolist = collection.videos.filter(encodingDone=True, published=True)
    return render_to_response('videos/collection.html', {'videos_list': videolist, 'submittal_list':submittal_list, 'page_list':page_list,'collection':collection, 'settings': settings},
                            context_instance=RequestContext(request))
                            
def search(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and get_query)'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['title', 'description', 'tags__name'])
        
        found_entries = Video.objects.filter(entry_query).order_by('-date')

    return render_to_response('videos/search_results.html',
                          { 'query_string': query_string, 'videos_list': found_entries, 'submittal_list':submittal_list, 'page_list':page_list, 'settings': settings},
                          context_instance=RequestContext(request))

def search_json(request):
    ''' The search view for handling the search using Django's "Q"-class (see normlize_query and get_query)'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, ['title', 'description','tags__name'])

        found_entries = Video.objects.filter(entry_query).order_by('-date')

    data = serializers.serialize('json', found_entries)
    return HttpResponse(data, content_type = 'application/javascript; charset=utf8')
           
def tag_json(request, tag):
    videolist = Video.objects.filter(encodingDone=True, published=True, tags__name__in=[tag]).order_by('-date')
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    data = serializers.serialize('json', videolist)
    return HttpResponse(data, content_type = 'application/javascript; charset=utf8')

@login_required(login_url='/login/')
def submittal(request, subm_id):
    if request.user.is_authenticated():
        submittal = get_object_or_404(Submittal, pk = subm_id)
        submittal_list = Submittal.objects.filter(users=request.user)
        if request.method == 'POST':
            form = SubmittalForm(request.POST)
            if form.is_valid():
                model = Video(
                              title=form.data['media_title'],
                              slug=form.data['media_title'],
                              date=datetime.date.today(),
                              description=form.data['media_description'],
                              user=request.user,
                              license=form.data['media_license'],
                              linkURL=form.data['media_linkURL'],
                              kind=form.data['media_kind'],
                              torrentURL=form.data['media_torrentURL'],
                              mp4URL=form.data['media_mp4URL'],
                              webmURL=form.data['media_webmURL'],
                              mp3URL=form.data['media_mp3URL'],
                              oggURL=form.data['media_oggURL'],
                              videoThumbURL=form.data['media_videoThumbURL'],
                              audioThumbURL=form.data['media_audioThumbURL'],
                              originalFile="None",
                              encodingDone=True,
                              published=form.cleaned_data['media_published'],
                              channel=form.cleaned_data['media_channel'],
                              torrentDone=form.cleaned_data['media_torrentDone'],
                             )
                media_tags=form.cleaned_data['media_tags']
                model.full_clean()
                model.save()
                for media_tag in media_tags:
                    model.tags.add(media_tag)
                return redirect(list)
        else:
	    tag_string = ""
            for tag in submittal.media_tags.all():
                tag_string += (str(tag) + ", ")

            form = SubmittalForm(initial={
                'media_title': submittal.media_title,
                'media_description': submittal.media_description,
                'media_channel': submittal.media_channel,
                'media_license': submittal.media_license,
                'media_linkURL': submittal.media_linkURL,
                'media_kind': submittal.media_kind,
                'media_torrentURL': submittal.media_torrentURL,
                'media_mp4URL': submittal.media_mp4URL,
                'media_webmURL': submittal.media_webmURL,
                'media_mp3URL': submittal.media_mp3URL,
                'media_oggURL': submittal.media_oggURL,
                'media_videoThumbURL': submittal.media_videoThumbURL,
                'media_audioThumbURL': submittal.media_audioThumbURL,
                'media_published': submittal.media_published,
                'media_tags': tag_string,
                'media_torrentDone': submittal.media_torrentDone,
            })
            return render_to_response('videos/submittal.html', {'submittal_form': form, 'submittal': submittal, 'settings': settings, 'page_list':page_list, 'submittal_list':submittal_list}, context_instance=RequestContext(request))
    else:
        return render_to_response('videos/submittal.html', {'submittal_form': form, 'submittal': submittal, 'settings': settings, 'page_list':page_list, 'submittal_list':submittal_list}, context_instance=RequestContext(request)) 

@login_required(login_url='/login/')
def upload_thumbnail(request):
    submittal_list = Submittal.objects.filter(users=request.user)
    thumbnails_list = getThumbnails(settings.THUMBNAILS_DIR)
    del thumbnails_list[0]
    if request.method == 'POST':
        form = ThumbnailForm(request.POST, request.FILES or None)
        if form.is_valid():
            if (request.FILES['file'].content_type == 'image/png' or request.FILES['file'].content_type == 'image/jpeg') and not form.data['title'] == '':
                handle_uploaded_thumbnail(request.FILES['file'], form.data['title'])
                message = _("The upload of %s was successful") % (form.data['title'])
                return render_to_response('videos/thumbnail.html', {'thumbnail_form': form, 'settings': settings, 'page_list':page_list, 'submittal_list':submittal_list, 'thumbs_list':thumbnails_list, 'message': message}, context_instance=RequestContext(request))
            else:
                error = _("Please upload an image file")
                form = ThumbnailForm()
                return render_to_response('videos/thumbnail.html', {'thumbnail_form': form, 'settings': settings, 'submittal_list':submittal_list, 'page_list':page_list, 'thumbs_list':thumbnails_list, 'error': error}, context_instance=RequestContext(request))

        else:
            form = ThumbnailForm()
            return render_to_response('videos/thumbnail.html', {'thumbnail_form': form, 'settings': settings, 'submittal_list':submittal_list, 'page_list':page_list, 'thumbs_list':thumbnails_list}, context_instance=RequestContext(request))
    else:
        form = ThumbnailForm()
        return render_to_response('videos/thumbnail.html', {'thumbnail_form': form, 'settings': settings, 'submittal_list':submittal_list, 'page_list':page_list, 'thumbs_list':thumbnails_list}, context_instance=RequestContext(request))
    
def handle_uploaded_thumbnail(f, filename):
    destination = open('media/thumbnails/' + filename, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

@login_required(login_url='/login/')
def submit(request):
    ''' The view for uploading the videos. Only authenticated users can upload videos!
    If we use transloadit to encode the videos we use the more or less official python
    "API" to ask transloadit to transcode our files otherwise we use django tasks to make
    a new task task for encoding this video. If we use bittorrent to distribute our files
    we also use django tasks to make the .torrent files (this can take a few minutes for
    very large files '''
    submittal_list = Submittal.objects.filter(users=request.user)
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = VideoForm(request.POST, request.FILES or None)
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
                        djangotasks.register_task(cmodel.create_bittorrent, "Create Bittorrent file for video and serve it")
                        torrent_task = djangotasks.task_for_object(cmodel.create_bittorrent)
                        djangotasks.run_task(torrent_task)
                    cmodel.user = request.user
                    cmodel.save()
                    return redirect(list)
    
            return render_to_response('videos/submit.html',
                                    {'submit_form': form, 'settings': settings,'submittal_list':submittal_list, 'page_list':page_list},
                                    context_instance=RequestContext(request))
        else:
            form = VideoForm()
            return render_to_response('videos/submit.html',
                                    {'submit_form': form, 'settings': settings,'submittal_list':submittal_list, 'page_list':page_list},
                                    context_instance=RequestContext(request))
    else:
        return render_to_response('videos/nothing.html', {'page_list':page_list, 'submittal_list':submittal_list, 'settings': settings},
                            context_instance=RequestContext(request))

@login_required(login_url='/login/')
def status(request):
    submittal_list = Submittal.objects.filter(users=request.user)
    if settings.USE_BITTORRENT:
        processing_videos = Video.objects.filter(Q(encodingDone=False) | Q(torrentDone=False))
    else:
        processing_videos = Video.objects.filter(encodingDone=False)
    running_tasks = []
    for video in processing_videos:
        tasks = djangotasks.models.Task.objects.filter(model="portal.video", object_id=video.pk)
        running_tasks.append(tasks)
    return render_to_response('videos/status.html',
                                    {'processing_videos': processing_videos, 'submittal_list':submittal_list, 'page_list':page_list, 'running_tasks': running_tasks, 'settings': settings},
                                    context_instance=RequestContext(request))

@csrf_exempt
def encodingdone(request):
    ''' This is a somewhat special view: It is called by transloadit to tell
    OwnTube that the encoding process is done. The view then parses the
    JSON data in the POST request send by transloadit and than get this information
    into our video model. Of course it can be possible for attackers to alter videos
    using for example curl but they would need to guess a assembly_id and these are 
    quite long hex strings. To improve the security we could also use the custom header
    option from transloadit but I think this wouldn't really help in a open source project'''
    if request.user.is_authenticated():
        submittal_list = Submittal.objects.filter(users=request.user)
    else:
        submittal_list = Submittal.objects.filter()
    if request.method == 'POST':
        data = json.loads(request.POST['transloadit'])
        try:
            video = Video.objects.get(assemblyid=data['assembly_id'])
            if (video.kind == 0):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP4_ENCODE]
                resultFirst = resultItem[0]
                video.mp4URL = resultFirst['url']
                video.mp4Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                video.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_WEBM_ENCODE]
                resultFirst = resultItem[0]
                video.webmURL = resultFirst['url']
                video.webmSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_THUMB_ENCODE]
                resultFirst = resultItem[0]
                video.videoThumbURL = resultFirst['url']
            elif (video.kind == 1):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP3_ENCODE]
                resultFirst = resultItem[0]
                video.mp3URL = resultFirst['url']
                video.mp3Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                video.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_OGG_ENCODE]
                resultFirst = resultItem[0]
                video.oggURL = resultFirst['url']
                video.oggSize = resultFirst['size']
            elif (video.kind == 2):
                results = data['results']
                resultItem = results[settings.TRANSLOAD_MP4_ENCODE]
                resultFirst = resultItem[0]
                video.mp4URL = resultFirst['url']
                video.mp4Size = resultFirst['size']
                resultMeta = resultFirst['meta']
                video.duration = str(resultMeta['duration'])
                resultItem = results[settings.TRANSLOAD_WEBM_ENCODE]
                resultFirst = resultItem[0]
                video.webmURL = resultFirst['url']
                video.webmSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_MP3_ENCODE]
                resultFirst = resultItem[0]
                video.mp3URL = resultFirst['url']
                video.mp3Size = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_OGG_ENCODE]
                resultFirst = resultItem[0]
                video.oggURL = resultFirst['url']
                video.oggSize = resultFirst['size']
                resultItem = results[settings.TRANSLOAD_THUMB_ENCODE]
                resultFirst = resultItem[0]
                video.videoThumbURL = resultFirst['url']
            video.encodingDone = True
            video.save()
        except Video.DoesNotExist:
            raise Http404
        return HttpResponse(_(u"Video was updated"))

    else:
        return render_to_response('videos/nothing.html', {'settings': settings, 'page_list':page_list},
                            context_instance=RequestContext(request))
    

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
