import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from docx import Document
from docx.shared import Inches,Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from .models import UploadedFile


def upload_docx(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        temp_name = fs.save(uploaded_file.name, uploaded_file)
        temp_path = fs.path(temp_name)

        db_file = UploadedFile.objects.create(
            original_name=uploaded_file.name,
            file=f'uploads/temp_{uploaded_file.name}'
        )

        new_filename = f"{db_file.uuid_name}.docx"
        new_path = os.path.join(settings.MEDIA_ROOT, 'uploads', new_filename)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        with open(temp_path, 'rb') as src, open(new_path, 'wb') as dst:
            dst.write(src.read())

        domain = request.build_absolute_uri('/')[:-1]
        verify_url = f"{domain}/verify/{db_file.uuid_name}/"

        # QR code yaratamiz (fayl emas, verify sahifasiga)
        qr_img = qrcode.make(verify_url)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        buf.seek(0)

        # DOCX ga QR va kod yozamiz
        doc = Document(new_path)
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False

        # chap ustunda kod
        cell_code = table.rows[0].cells[0]
        p_code = cell_code.paragraphs[0]
        run_code = p_code.add_run(f"Kod: {db_file.code}")
        run_code.bold = True
        run_code.font.size = Pt(20)  # shrift kattaligi
        p_code.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell_code.width = Inches(2)

        # o'ng ustunda QR rasm
        cell_qr = table.rows[0].cells[1]
        p_qr = cell_qr.paragraphs[0]
        run_qr = p_qr.add_run()
        run_qr.add_picture(buf, width=Inches(1.3))
        p_qr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        cell_qr.width = Inches(3)

        # Jadvalni o'ng tomonga suramiz
        table.alignment = WD_TABLE_ALIGNMENT.RIGHT
        doc.save(new_path)

        db_file.file.name = f"uploads/{new_filename}"
        db_file.save()

        os.remove(temp_path)

        return render(request, 'result.html', {
            'file_url': f"{settings.MEDIA_URL}uploads/{new_filename}",
            'uuid': db_file.uuid_name,
            'code': db_file.code,
            'verify_url': verify_url
        })

    return render(request, 'upload.html')



from django.shortcuts import get_object_or_404, render
from django.http import FileResponse

def verify_file(request, uuid):
    file_obj = get_object_or_404(UploadedFile, uuid_name=uuid)

    if request.method == 'POST':
        code = request.POST.get('code')
        if code == file_obj.code:
            file_path = file_obj.file.path
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_obj.original_name)
        else:
            return render(request, 'verify.html', {
                'error': 'Kod noto‘g‘ri!',
                'uuid': uuid
            })

    return render(request, 'verify.html', {'uuid': uuid})
