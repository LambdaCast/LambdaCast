from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from livestream.models import Stream

from django.utils import timezone

def current(request):
    ''' This view gets all streams that are scheduled to be live right now
    if there are no streams it redirects to the liste view. The upcoming_streams_list
    is used to show upcoming events in a side bar (see the template)'''
    stream_list = Stream.objects.filter(published=True,startDate__lt=timezone.now, endDate__gt=timezone.now).order_by('-startDate')
    upcoming_streams_list = Stream.objects.filter(published=True,endDate__gt=timezone.now).order_by('-startDate')[:5]
    if not stream_list:
        return redirect(list_streams)
    else:
        return TemplateResponse(request, 'livestream/current.html', {'stream_list': stream_list, 'upcoming_streams_list': upcoming_streams_list})

def list_streams(request):
    ''' This view shows gets all upcoming streaming events
    and forwards them to our template '''
    stream_list = Stream.objects.filter(published=True,endDate__gt=timezone.now).order_by('-startDate')
    return TemplateResponse(request, 'livestream/list.html', {'stream_list': stream_list})

def detail(request, slug):
    ''' This view shows the detail of a stream, it is used to
    show the user more information on one event but not
    for showing the player'''
    stream = get_object_or_404(Stream, slug=slug)
    upcoming_streams_list = Stream.objects.filter(published=True,endDate__gt=timezone.now).order_by('-startDate')[:5]
    return TemplateResponse(request, 'livestream/detail.html', {'stream': stream, 'upcoming_streams_list': upcoming_streams_list})
