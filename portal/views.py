from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.translation import ugettext_lazy as _

from pages.models import Page
from portal.models import MediaItem, Comment, Channel, Collection, Submittal, MediaFile
from portal.forms import MediaItemForm, CommentForm, getThumbnails, ThumbnailForm, SubmittalForm
from portal.media_formats import MEDIA_FORMATS

from taggit.models import Tag
import lambdaproject.settings as settings

import djangotasks

from datetime import datetime
import os
import re
from operator import attrgetter
import itertools
from sets import Set

def index(request):
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
    return render_to_response('portal/index.html', {'page_list': get_page_list, 'submittal_list':get_submittal_list(request), 'latest_mediaitems_list': mediaitems, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def channel_list(request,slug):
    ''' This view is the view for the channel's list it works almost like the index view'''
    channel = get_object_or_404(Channel, slug=slug)
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
    return render_to_response('portal/channel.html', {'page_list':get_page_list, 'submittal_list':get_submittal_list(request), 'mediaitems_list': mediaitems, 'channel': channel, 'channel_list': channel_list, 'settings': settings},
                            context_instance=RequestContext(request))

def detail(request, slug):
    ''' Handles the detail view of a media item (the player so to say) and handles the comments (this should become nicer with AJAX and stuff)'''
    mediaitem = get_object_or_404(MediaItem, slug=slug)

    if request.method == 'POST':
        comment = Comment(item=mediaitem,ip=request.META["REMOTE_ADDR"])
        emptyform = CommentForm()
        form = CommentForm(request.POST, instance=comment)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.save()
            message = _(u"Your comment will be moderated")
            user_mediaitem = mediaitem.user
            if not user_mediaitem.email == '':
                if not user_mediaitem.first_name == '':
                    mail_message = _(u'Hello %s,\n\nSomeone commented under one of your content. Please check and moderate it, so others can see the comment.\n\nThank You.') % user_mediaitem.first_name
                else:
                    mail_message = _(u'Hello %s,\n\nSomeone commented under one of your content. Please check and moderate it, so others can see the comment.\n\nThank You.') % user_mediaitem.username
                try:
                    user_mediaitem.email_user(_(u'New Comment: ') + mediaitem.title, mail_message)
                except:
                    pass
            return render_to_response('portal/items/detail.html', {'page_list':get_page_list,
                                                                   'mediaitem': mediaitem,
                                                                   'comment_form': emptyform,
                                                                   'message': message,
                                                                   'settings': settings,
                                                                  }, context_instance=RequestContext(request))
        else:
            return render_to_response('portal/items/detail.html', {'page_list':get_page_list,
                                                                   'mediaitem': mediaitem,
                                                                   'comment_form': form,
                                                                   'settings': settings,
                                                                  }, context_instance=RequestContext(request))
    else:
        form = CommentForm()
        return render_to_response('portal/items/detail.html', {'mediaitem': mediaitem,
                                                               'page_list':get_page_list,
                                                               'submittal_list':get_submittal_list(request),
                                                               'comment_form': form,
                                                               'settings': settings,
                                                              },context_instance=RequestContext(request))

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
    mediaitemslist = collection.items.filter(encodingDone=True, published=True)
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
            mediaitem = form.save()
            mediaitem.user = request.user
            mediaitem.save()
            form.create_mediafiles(mediaitem)
            mediaitem.get_and_save_duration()
            return redirect(index)
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
    tasks_mediaitem = djangotasks.models.Task.objects.filter(model="portal.mediaitem").exclude(status="successful")
    tasks_mediafile = djangotasks.models.Task.objects.filter(model="portal.mediafile").exclude(status="successful")

    mediaitem_ids = Set(map((lambda mediaitem: mediaitem.object_id), tasks_mediaitem))
    for mediafile in tasks_mediafile:
        try:
            mediaitem_ids.add(MediaFile.objects.get(pk=mediafile.object_id).media_item.pk)
        except MediaFile.DoesNotExist:
            pass

    mediaitems = MediaItem.objects.filter(pk__in=mediaitem_ids)
    return render_to_response('portal/status.html',
                                    {'mediaitems': mediaitems, 'submittal_list':get_submittal_list(request), 'page_list':get_page_list, 'settings': settings},
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

def get_thumbnails_list():
    thumbnails_list = getThumbnails(settings.THUMBNAILS_DIR)
    del thumbnails_list[0]
    return thumbnails_list

def get_page_list():
    return Page.objects.filter(activated=True).order_by('orderid')

def get_submittal_list(request):
    return Submittal.objects.filter(users=request.user) if request.user.is_authenticated() else []

