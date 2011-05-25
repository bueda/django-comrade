from django.conf import settings


def ssl_media(request):
    if request.is_secure():
        ssl_media_url = settings.MEDIA_URL.replace('http://','https://')
    else:
        ssl_media_url = settings.MEDIA_URL
    return {'MEDIA_URL': ssl_media_url}
