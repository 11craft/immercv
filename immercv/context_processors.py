def caching(request):
    return {
        'cache_timeout': 0 if request.user.is_authenticated() else 300,
    }
