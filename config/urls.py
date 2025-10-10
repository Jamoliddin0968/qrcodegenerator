from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from documents.views import upload_docx

urlpatterns = [
    path('', upload_docx, name='upload_docx'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
