import uuid
from django.db import models

class UploadedFile(models.Model):
    uuid_name = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_name} ({self.uuid_name})"
