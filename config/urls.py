# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views import defaults as default_views

from immercv.cvblog.views import CvblogPersonOfFirstUserView
from immercv.cvgraph.views import CvgraphPersonOfFirstUserView
from immercv.cvgraph.sitemaps import CvsSitemap


sitemaps = {
    'cvs': CvsSitemap(),
}


urlpatterns = [
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots-txt'),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include("immercv.users.urls", namespace="users")),
    url(r'^accounts/', include('allauth.urls')),

    # Your stuff: custom urls includes go here
    url(r'^$', RedirectView.as_view(url='/person/first/'), name="home"),
    url(r'^blog/first/$', CvblogPersonOfFirstUserView.as_view(), name="blog"),
    url(r'^blog/', include('immercv.cvblog.urls', namespace='cvblog')),
    url(r'^person/first/$', CvgraphPersonOfFirstUserView.as_view(), name="cv"),
    url(r'', include('immercv.cvgraph.urls', namespace='cvgraph')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request),
        url(r'^403/$', default_views.permission_denied),
        url(r'^404/$', default_views.page_not_found),
        url(r'^500/$', default_views.server_error),
    ]
