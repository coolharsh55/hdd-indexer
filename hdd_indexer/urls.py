"""Urls for hdd-indexer

    / home
    /settings settings
"""

from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    # admin urls
    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),

    # homepage
    url(r'^$', 'hdd_indexer.views.homepage', name='home'),
    url(r'^help/$', 'hdd_indexer.views.help', name='help'),
    url(r'^setup/$', 'hdd_indexer.views.setup', name='setup'),
    url(r'^settings/$', 'hdd_indexer.views.settings', name='settings'),
    url(r'^crawler/$', 'hdd_indexer.views.crawler', name='crawler'),
    url(r'^loader/$', 'hdd_indexer.views.loader', name='loader'),
    # TODO: replace urls in index.html and input_alert.js with {{url}}
)
