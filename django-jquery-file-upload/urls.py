from django.urls import include, path
from django.http import HttpResponseRedirect
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('', lambda x: HttpResponseRedirect('/batmusic/new/')),
    path('batmusic/', include('fileupload.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
