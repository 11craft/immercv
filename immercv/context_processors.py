from django.conf import settings


def analytics(request):
    return {
        'PIWIK_SERVER': settings.PIWIK_SERVER,
        'PIWIK_SITE_ID': settings.PIWIK_SITE_ID,
    }


def caching(request):
    return {
        'cache_timeout': 0 if request.user.is_authenticated() else 300,
    }


def disqus(request):
    return {
        'DISQUS_SITE_ID': settings.DISQUS_SITE_ID,
    }
