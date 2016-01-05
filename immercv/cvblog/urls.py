# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.PersonPostsView.as_view(),
        name='person_posts',
    ),
    url(
        regex=r'^(?P<id>\d+)/(?P<slug>[\w-]+)/rss/$',
        view=views.PersonPostsFeed(),
        name='person_posts_feed',
    ),
]
