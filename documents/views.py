import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .models import UploadedFile


def upload_docx(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()

        # Faylni vaqtincha saqlaymiz
        temp_name = fs.save(uploaded_file.name, uploaded_file)
        temp_path = fs.path(temp_name)

        # Bazaga yozamiz
        db_file = UploadedFile.objects.create(
            original_name=uploaded_file.name,
            file=f'uploads/temp_{uploaded_file.name}'  # keyinchalik yangilanadi
        )

        # Yangi nom yaratamiz (uuid)
        new_filename = f"{db_file.uuid_name}.docx"
        new_path = os.path.join(settings.MEDIA_ROOT, 'uploads', new_filename)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        # Faylni nusxalab yangi nomda saqlaymiz
        with open(temp_path, 'rb') as src, open(new_path, 'wb') as dst:
            dst.write(src.read())

        # To‘liq URL (domain kerak)
        domain = request.build_absolute_uri('/')[:-1]
        file_url = f"{domain}{settings.MEDIA_URL}uploads/{new_filename}"

        # QR code yaratamiz (fayl URL bilan)
        qr_img = qrcode.make(file_url)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        buf.seek(0)

        # DOCX ochamiz va pastki o‘ng burchakka qo‘shamiz
        doc = Document(new_path)
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        run.add_picture(buf, width=Inches(1.3))
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        # Saqlaymiz
        doc.save(new_path)

        # Bazada fayl yo‘lini yangilaymiz
        db_file.file.name = f"uploads/{new_filename}"
        db_file.save()

        # Vaqtincha faylni o‘chirib tashlaymiz
        try:
            os.remove(temp_path)
        except FileNotFoundError:
            pass

        return render(request, 'result.html', {
            'file_url': f"{settings.MEDIA_URL}uploads/{new_filename}",
            'uuid': db_file.uuid_name,
            'link': file_url
        })

    return render(request, 'upload.html')
