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
        regex=r'^company/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphCompanyDetailView.as_view(),
        name='company_detail',
    ),
    url(
        regex=r'^experience/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphExperienceDetailView.as_view(),
        name='experience_detail',
    ),
    url(
        regex=r'^person/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphPersonDetailView.as_view(),
        name='person_detail',
    ),
    url(
        regex=r'^project/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphProjectDetailView.as_view(),
        name='project_detail',
    ),
    url(
        regex=r'^role/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphRoleDetailView.as_view(),
        name='role_detail',
    ),
    url(
        regex=r'^topic/(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view=views.CvgraphTopicDetailView.as_view(),
        name='topic_detail',
    ),
    url(
        regex=r'^change/$',
        view=views.CvgraphChangeView.as_view(),
        name='change',
    ),
]
