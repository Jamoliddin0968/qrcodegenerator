import os
import pdfkit
import qrcode
import base64
import uuid
import random
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from .models import UploadedFile
from django.shortcuts import get_object_or_404, render
from django.http import FileResponse


def verify_file(request, uuid):
    file_obj = get_object_or_404(UploadedFile, uuid_name=uuid)

    if request.method == 'POST':
        # print(request.POST)
        code = request.POST.get('code')
        if code == file_obj.code:
            file_path = file_obj.file.path
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_obj.original_name)
        else:
            return render(request, 'index.html', {
                'error': 'Kod noto‘g‘ri!',
                'uuid': uuid
            })

    return render(request, 'index.html', {'uuid': uuid})

def create_pdf_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        pinfl = request.POST.get("pinfl")
       
        years = request.POST.getlist("year[]")
        months = request.POST.getlist("month[]")
        companies = request.POST.getlist("company[]")
        salaries = request.POST.getlist("salary[]")
        taxes = request.POST.getlist("tax[]")

        incomes = []
        for i in range(len(months)):
            if (years[i] or months[i] or companies[i] or salaries[i] or taxes[i]):
                incomes.append({
                "year": (years[i] or "").strip(),
                "month": (months[i] or "").strip(),
                "company": (companies[i] or "").strip(),
                "salary": (salaries[i] or "").strip(),
                "tax": (taxes[i] or "").strip(),
        })


        # создаём запись
        db_file = UploadedFile.objects.create(
            original_name=f"{full_name}.pdf",
            file="",
        )

        # генерим 4-значный код
        code4 = f"{random.randint(0, 9999):04d}"
        try:
            db_file.code = code4
            db_file.save(update_fields=["code"])
        except Exception:
            code4 = db_file.code

        # verify URL + QR
        domain = request.build_absolute_uri('/')[:-1]
        verify_url = f"{domain}/verify/{db_file.uuid_name}/"

        qr_img = qrcode.make(verify_url)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        qr_data = f"data:image/png;base64,{qr_base64}"

        # рендерим HTML
        html_string = render_to_string("pdf_template.html", {
            "full_name": full_name,
            "pinfl": pinfl,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "doc_number": '-'.join([uuid.uuid4().hex[i:i+4] for i in range(0, 28, 4)]),
            "incomes": incomes,
            "verify_url": verify_url,
            "code": code4,
            "qr_data": qr_data,
        })

        # путь для сохранения PDF
        pdf_path = os.path.join(settings.MEDIA_ROOT, "uploads", f"{db_file.uuid_name}.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # === wkhtmltopdf через pdfkit ===
        config = pdfkit.configuration(
            wkhtmltopdf="/usr/bin/wkhtmltopdf"  # путь к бинарнику wkhtmltopdf
        )

        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'enable-local-file-access': None,  # чтобы разрешить загрузку CSS/изображений
            'encoding': 'UTF-8',
            'quiet': '',
        }

        pdfkit.from_string(
            html_string,
            pdf_path,
            configuration=config,
            options=options
        )

        db_file.file.name = f"uploads/{db_file.uuid_name}.pdf"
        db_file.save(update_fields=["file"])

        return HttpResponse(
            f"<h3>PDF готов:</h3><a href='{settings.MEDIA_URL}uploads/{db_file.uuid_name}.pdf'>Скачать</a>"
        )

    return render(request, "pdf_form.html")

def create_work_experience_pdf_view(request):
    """
    Создание документа о трудовом стаже
    """
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        pinfl = request.POST.get("pinfl")
        application_number = request.POST.get("application_number")

        # Получаем массивы данных о работе
        start_dates = request.POST.getlist("start_date[]")
        end_dates = request.POST.getlist("end_date[]")
        organizations = request.POST.getlist("organization[]")
        tins = request.POST.getlist("tin[]")
        positions = request.POST.getlist("position[]")
        departments = request.POST.getlist("department[]")

        work_experiences = []
        for i in range(len(start_dates)):
            if start_dates[i] or organizations[i]:
                work_experiences.append({
                    "start_date": (start_dates[i] or "").strip(),
                    "end_date": (end_dates[i] or "Present").strip(),
                    "organization": (organizations[i] or "").strip(),
                    "tin": (tins[i] or "").strip(),
                    "position": (positions[i] or "").strip(),
                    "department": (departments[i] or "Does not exist").strip(),
                })

        # создаём запись
        db_file = UploadedFile.objects.create(
            original_name=f"{full_name}_work_experience.pdf",
            file="",
        )

        # генерим 4-значный код
        code4 = f"{random.randint(0, 9999):04d}"
        try:
            db_file.code = code4
            db_file.save(update_fields=["code"])
        except Exception:
            code4 = db_file.code

        # verify URL + QR
        domain = request.build_absolute_uri('/')[:-1]
        verify_url = f"{domain}/verify/{db_file.uuid_name}/"

        qr_img = qrcode.make(verify_url)
        buf = BytesIO()
        qr_img.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        qr_data = f"data:image/png;base64,{qr_base64}"

        # рендерим HTML
        html_string = render_to_string("work_experience_template.html", {
            "full_name": full_name,
            "pinfl": pinfl,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "doc_number": '-'.join([uuid.uuid4().hex[i:i+4] for i in range(0, 28, 4)]),
            "application_number": application_number,
            "work_experiences": work_experiences,
            "verify_url": verify_url,
            "code": code4,
            "qr_data": qr_data,
        })

        # путь для сохранения PDF
        pdf_path = os.path.join(settings.MEDIA_ROOT, "uploads", f"{db_file.uuid_name}.pdf")
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

        # wkhtmltopdf через pdfkit
        config = pdfkit.configuration(
            wkhtmltopdf="/usr/bin/wkhtmltopdf"
        )

        options = {
            'page-size': 'A4',
            'margin-top': '1cm',
            'margin-right': '1cm',
            'margin-bottom': '1cm',
            'margin-left': '1cm',
            'enable-local-file-access': None,
            'encoding': 'UTF-8',
            'quiet': '',
        }

        pdfkit.from_string(
            html_string,
            pdf_path,
            configuration=config,
            options=options
        )

        db_file.file.name = f"uploads/{db_file.uuid_name}.pdf"
        db_file.save(update_fields=["file"])

        return HttpResponse(
            f"<h3>PDF готов:</h3><a href='{settings.MEDIA_URL}uploads/{db_file.uuid_name}.pdf'>Скачать</a>"
        )

    return render(request, "work_experience_form.html")