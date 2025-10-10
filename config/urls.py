from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from documents.views import upload_docx
from django.contrib import admin
# from django.conf
urlpatterns = [
    path('document', upload_docx, name='upload_docx'),
   
path('admin/', admin.site.urls),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)