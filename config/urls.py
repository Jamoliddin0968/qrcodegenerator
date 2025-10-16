from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from documents.views import verify_file, create_pdf_view, create_work_experience_pdf_view
from django.contrib import admin
# from django.conf
urlpatterns = [
    path('verify/<uuid:uuid>/', verify_file, name='verify_file'),
    path('income-statement', create_pdf_view, name='create_pdf'), 
    path('create-work-experience', create_work_experience_pdf_view, name='create_work_experience'),
   
path('admin/', admin.site.urls),
]

# if settings.DEBUG:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)