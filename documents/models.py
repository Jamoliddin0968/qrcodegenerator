from random import randint
import uuid
from django.db import models
def generate_code():
    return str(randint(1000, 9999))

class UploadedFile(models.Model):
    uuid_name = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=4, default=generate_code)  # 4 xonali kod
    def __str__(self):
        return f"{self.original_name} ({self.uuid_name})"
