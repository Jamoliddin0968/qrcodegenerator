from django.contrib import admin

# Register your models here.
from .models import UploadedFile

@admin.register(UploadedFile)
class myadmin(admin.ModelAdmin):
    list_display = ['id','uuid_name','created_at']