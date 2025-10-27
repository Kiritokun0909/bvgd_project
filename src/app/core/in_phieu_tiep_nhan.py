from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor

# Thư viện để đăng ký font
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import tempfile
import os
import sys

# ----------------- CẤU HÌNH TIẾNG VIỆT -----------------
# 1. Tên font sẽ sử dụng trong code
VIET_FONT = 'TahomaVN'
VIET_FONT_BOLD = 'TahomaVNBold'
VIET_FONT_ITALIC = 'TahomaVNItalic'

try:
    FONT_PATH = 'C:/Windows/Fonts/Arial.ttf'  # Thay bằng đường dẫn thực tế, ví dụ: 'C:/Windows/Fonts/Tahoma.ttf'
    # Đăng ký font
    pdfmetrics.registerFont(TTFont(VIET_FONT, FONT_PATH))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, FONT_PATH))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, FONT_PATH))

except Exception as e:
    print(f"!!! CẢNH BÁO: Lỗi đăng ký font: {e}")
    print("Sử dụng font ReportLab mặc định (có thể không hiển thị tiếng Việt).")
    VIET_FONT = 'Times-Roman'
    VIET_FONT_BOLD = 'Times-Bold'
    VIET_FONT_ITALIC = 'Times-Italic'

# ----------------- DỮ LIỆU CỦA PHIẾU CHỜ KHÁM -----------------
data = {
    'clinic_name': 'BỆNH VIỆN ABC',
    'room_info': 'Lầu X Phòng K',
    'queue_number': '0000',
    'code': 'CODE',
    'patient_name': 'Nguyễn Văn A',
    'patient_dob': '1999',
    'schedule_time': '23/10/2025 13:34',
    'print_time': '23/10/2025 13:34:37',
    'payment_method': 'BHYT'
}

# Kích thước tiêu chuẩn cho phiếu in nhiệt (khoảng 80mm)
TICKET_WIDTH = 80 * mm
TICKET_HEIGHT = 65 * mm

def draw_ticket(canvas, data):
    """Vẽ nội dung phiếu chờ khám lên canvas của ReportLab."""

    # 1. Khởi tạo Styles và Canvas
    styles = getSampleStyleSheet()

    # Thêm style cho tiêu đề và nội dung (Lưu ý: Bạn có thể thêm 'leading' để điều chỉnh khoảng cách dòng trong Paragraph)
    styles.add(ParagraphStyle(name='Header', fontName=VIET_FONT_BOLD, fontSize=11, alignment=1, leading=14))
    styles.add(ParagraphStyle(name='RoomInfo', fontName=VIET_FONT_BOLD, fontSize=16, alignment=0, leading=20))
    styles.add(ParagraphStyle(name='QueueNumber', fontName=VIET_FONT_BOLD, fontSize=30, textColor=HexColor('#d9534f')))
    styles.add(ParagraphStyle(name='NormalLeft', fontName=VIET_FONT, fontSize=10, alignment=0, leading=12))
    styles.add(ParagraphStyle(name='SmallItalic', fontName=VIET_FONT_ITALIC, fontSize=9, alignment=1, leading=10))

    # 2. Định vị bắt đầu vẽ (Bắt đầu từ trên xuống)
    y_cursor = TICKET_HEIGHT - 5 * mm  # Bắt đầu cách lề trên 5mm

    # KHOẢNG CÁCH MỚI
    SPACE_SMALL = 4 * mm
    SPACE_MEDIUM = 6 * mm
    SPACE_LARGE = 12 * mm

    # 3. Vẽ BỆNH VIỆN ABC
    p = Paragraph(data['clinic_name'], styles['Header'])
    p.wrapOn(canvas, TICKET_WIDTH - 10 * mm, 15 * mm)
    p.drawOn(canvas, 5 * mm, y_cursor - SPACE_SMALL)
    y_cursor -= SPACE_MEDIUM  # Giảm từ 15mm

    # 4. Vẽ Lầu X Phòng K
    p = Paragraph(data['room_info'], styles['RoomInfo'])
    p.wrapOn(canvas, TICKET_WIDTH - 10 * mm, 15 * mm)
    p.drawOn(canvas, 5 * mm, y_cursor - SPACE_MEDIUM)
    y_cursor -= SPACE_MEDIUM  # Giảm từ 15mm

    # 5. Vẽ SỐ THỨ TỰ (0000 và CODE)
    # Vị trí cho 0000
    canvas.setFont(VIET_FONT_BOLD, 30)
    # canvas.setFillColor(HexColor('#d9534f'))
    canvas.drawString(5 * mm, y_cursor - 10 * mm, data['queue_number'])  # Giữ nguyên vị trí vẽ số lớn

    # Vị trí cho CODE
    canvas.setFont(VIET_FONT, 10)
    canvas.setFillColor('black')
    canvas.drawString(TICKET_WIDTH - 25 * mm, y_cursor - 5 * mm, '')
    y_cursor -= SPACE_LARGE  # Giảm từ 15mm

    # Kẻ một đường ngang
    canvas.line(5 * mm, y_cursor, TICKET_WIDTH - 5 * mm, y_cursor)
    y_cursor -= SPACE_SMALL  # Giảm từ 5mm

    # 6. Vẽ Tên Bệnh Nhân
    patient_text = f"{data['patient_name']} - {data['patient_dob']}"
    canvas.setFont(VIET_FONT_BOLD, 12)
    canvas.drawString(5 * mm, y_cursor - SPACE_SMALL, patient_text)
    y_cursor -= SPACE_MEDIUM  # Giảm từ 10mm

    # 7. Vẽ Thời gian Dự kiến
    time_text = f"Dự kiến: {data['schedule_time']} --> {data['schedule_time']}"
    canvas.setFont(VIET_FONT, 8)
    canvas.drawString(5 * mm, y_cursor - SPACE_SMALL, time_text)
    y_cursor -= SPACE_MEDIUM  # Giảm từ 10mm

    # 8. Vui lòng chờ
    canvas.setFont(VIET_FONT, 10)
    canvas.drawCentredString(TICKET_WIDTH / 2, y_cursor - SPACE_SMALL, "Vui lòng chờ đến số thứ tự")
    y_cursor -= SPACE_SMALL  # Giảm từ 15mm

    # 9. Phiếu chỉ có giá trị trong ngày
    canvas.setFont(VIET_FONT_ITALIC, 9)
    canvas.drawCentredString(TICKET_WIDTH / 2, y_cursor - SPACE_SMALL, "Phiếu chỉ có giá trị trong ngày!")
    y_cursor -= SPACE_MEDIUM  # Giảm từ 10mm

    # 10. Phương thức thanh toán và giờ in
    canvas.setFont(VIET_FONT, 9)
    canvas.drawString(5 * mm, y_cursor - SPACE_SMALL, data['payment_method'])
    canvas.drawRightString(TICKET_WIDTH - 5 * mm, y_cursor - SPACE_SMALL, data['print_time'])
    y_cursor -= SPACE_MEDIUM  # Giảm từ 10mm


def create_and_open_pdf_for_printing(data):
    """Tạo file PDF tạm thời bằng ReportLab và mở file."""

    try:
        # 1. Tạo tệp PDF tạm thời
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            pdf_path = tmp_file.name

        # 2. Khởi tạo canvas với kích thước A4 (hoặc kích thước tùy chỉnh)
        c = canvas.Canvas(pdf_path, pagesize=A4)
        c.translate(0, A4[1] - TICKET_HEIGHT)

        # 3. Vẽ border để mô phỏng phiếu chờ
        c.rect(0, 0, TICKET_WIDTH, TICKET_HEIGHT, stroke=0, fill=0)

        # 4. Gọi hàm vẽ nội dung phiếu
        draw_ticket(c, data)

        # Kết thúc và lưu file PDF
        c.showPage()
        c.save()

        print(f"Đã tạo file PDF tạm tại: {pdf_path}")

        # 5. Mở file PDF để in
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')

    except Exception as e:
        print(f"Đã xảy ra lỗi khi tạo PDF với ReportLab: {e}")
