from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

def home_redirect(request):
    return redirect("/auth/dashboard/") if request.user.is_authenticated else redirect("/auth/login/")

urlpatterns = [
    path('', home_redirect),   # Auto redirect
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('reports/', include('reports.urls')),
    path('projects/', include('projects.urls')),
    path('finance/', include('finance.urls')),
    path('setup/', include('setup.urls')),
    path('sitemanage/', include('sitemanage.urls')),
    path('compliance/', include('compliance.urls')),
    path('progress/', include('progress.urls')),
    path('quality/', include('quality.urls')),
    path('resources/', include('resources.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)