from django import template

register = template.Library()

@register.filter
def absolute_media(request, media_url):
    """
    Convert /media/... to absolute URL for WeasyPrint
    """
    if not media_url:
        return ""
    return request.build_absolute_uri(media_url)
