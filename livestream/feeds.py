from django.contrib.syndication.views import Feed
from livestream.models import Stream
from django.utils.translation import ugettext_lazy as _

from django.utils import timezone

class UpcomingEvents(Feed):
    ''' This sub class of Django's Feed class handles the feed URL from urls.py
    in the LambdaCast directory, it gets all upcoming
    streaming events and returns the data as required
    for the django feed class
    TO DO: 
    Making it possible to change the title and so on in a better way,
    maybe in the admin app?
    '''
    title = _(u"The next streamings")
    link = "/stream/"
    description = _(u"Here you will see the streams")

    def items(self):
        return Stream.objects.filter(published=True,endDate__gt=timezone.now).order_by('-startDate')

    def item_title(self, item):
        return str(item.startDate) + ' ' + item.title

    def item_description(self, item):
        return item.description

    def item_pubdate(self, item):
        return item.created
