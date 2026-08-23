from urllib.parse import unquote

from django.conf import settings
from django.views.static import serve


def serve_media(request, path):
    """Serve uploaded files whose names are URL-encoded by the browser."""
    return serve(request, unquote(path), document_root=settings.MEDIA_ROOT)
