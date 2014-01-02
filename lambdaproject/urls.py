from django.conf.urls import patterns, include, url
from portal.feeds import *
from livestream.feeds import UpcomingEvents
from django.conf import settings

from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'portal.views.list'),
    url(r'^videos/(?P<slug>[-\w]+)/$', 'portal.views.detail'),
    url(r'^tags/(?P<tag>[\w|\W]+)/$', 'portal.views.tag'),
    url(r'^collection/(?P<slug>[-\w]+)/$', 'portal.views.collection'),
    url(r'^json_tags/(?P<tag>[\w|\W]+)/$', 'portal.views.tag_json'),
    url(r'^videos/channel/(?P<slug>[-\w]+)/$', 'portal.views.channel_list'),
    url(r'^videos/iframe/(?P<slug>[-\w]+)/$', 'portal.views.iframe'),
    url(r'^submittal/(?P<subm_id>\d+)/$', 'portal.views.submittal'),
    url(r'^search/', 'portal.views.search'),
    url(r'^json_search/', 'portal.views.search_json'),
    url(r'^submit/', 'portal.views.submit'),
    url(r'^thumbnail/', 'portal.views.upload_thumbnail'),
    url(r'^encodingdone/', 'portal.views.encodingdone'),
    url(r'^status/', 'portal.views.status'),
    url(r'^p/(?P<slug>[-\w]+)/$', 'pages.views.page'),
    url(r'^stream/$', 'livestream.views.current'),
    url(r'^stream/list/$', 'livestream.views.list'),
    url(r'^stream/(?P<slug>[-\w]+)/$', 'livestream.views.detail'),
    url(r'^login/', 'django.contrib.auth.views.login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^feeds/latest/mp4', LatestMP4Videos()),
    url(r'^feeds/latest/webm', LatestWEBMVideos()),
    url(r'^feeds/latest/mp3', LatestMP3Audio()),
    url(r'^feeds/latest/ogg', LatestOGGAudio()),
    url(r'^feeds/stream/upcoming', UpcomingEvents()),
    url(r'^feeds/latest/torrent', TorrentFeed()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/mp4/$', ChannelFeedMP4()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/webm/$', ChannelFeedWEBM()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/ogg/$', ChannelFeedOGG()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/mp3/$', ChannelFeedMP3()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/torrent/$', ChannelFeedTorrent()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/mp4/$', CollectionFeedMP4()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/webm/$', CollectionFeedWEBM()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/ogg/$', CollectionFeedOGG()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/mp3/$', CollectionFeedMP3()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/torrent/$', CollectionFeedTorrent()),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    
)

urlpatterns += patterns('',
    url(r'^captcha/', include('captcha.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
