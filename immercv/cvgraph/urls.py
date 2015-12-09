# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    url(
        regex=r'^person/me/$',
        view=views.CvgraphMeView.as_view(),
        name='me'
    ),
    url(
        regex=r'^person/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphPersonDetailView.as_view(),
        name='person_detail',
    ),
    url(
        regex=r'^change/$',
        view=views.CvgraphChangeView.as_view(),
        name='change',
    ),
]
