from django.conf.urls import patterns, include, url
from portal.feeds import LatestMedia, TorrentFeed, ChannelFeed, ChannelFeedTorrent, CollectionFeed, CollectionFeedTorrent, CommentsFeed
from livestream.feeds import UpcomingEvents

import lambdaproject.settings as settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'portal.views.index'),
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/favicon.ico'}),
    url(r'^item/(?P<slug>[-\w]+)/$', 'portal.views.detail'),
    url(r'^tags/(?P<tag>[\w|\W]+)/$', 'portal.views.tag'),
    url(r'^collection/(?P<slug>[-\w]+)/$', 'portal.views.collection'),
    url(r'^json_tags/(?P<tag>[\w|\W]+)/$', 'portal.views.tag_json'),
    url(r'^channel/(?P<slug>[-\w]+)/$', 'portal.views.channel_list'),
    url(r'^item/iframe/(?P<slug>[-\w]+)/$', 'portal.views.iframe'),
    url(r'^submittal/(?P<subm_id>\d+)/$', 'portal.views.submittal'),
    url(r'^search/', 'portal.views.search'),
    url(r'^json_search/', 'portal.views.search_json'),
    url(r'^submit/', 'portal.views.submit'),
    url(r'^thumbnail/', 'portal.views.upload_thumbnail'),
    url(r'^status/', 'portal.views.status'),
    url(r'^p/(?P<slug>[-\w]+)/$', 'pages.views.page'),
    url(r'^stream/$', 'livestream.views.current'),
    url(r'^stream/list/$', 'livestream.views.list_streams'),
    url(r'^stream/(?P<slug>[-\w]+)/$', 'livestream.views.detail'),
    url(r'^login/', 'django.contrib.auth.views.login'),
    url(r'^logout/', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^feeds/latest/(?P<fileformat>[-\w]+)/$', LatestMedia()),
    url(r'^feeds/stream/upcoming', UpcomingEvents()),
    url(r'^feeds/latest/torrent', TorrentFeed()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/(?P<fileformat>[-\w]+)/$', ChannelFeed()),
    url(r'^feeds/(?P<channel_slug>[-\w]+)/torrent/$', ChannelFeedTorrent()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/(?P<fileformat>[-\w]+)/$', CollectionFeed()),
    url(r'^feeds/collection/(?P<collection_slug>[-\w]+)/torrent/$', CollectionFeedTorrent()),
    url(r'^feeds/comments/$', CommentsFeed()),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

if "django.contrib.admindocs" in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        url(r'^admindocs/', include('django.contrib.admindocs.urls')),
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
