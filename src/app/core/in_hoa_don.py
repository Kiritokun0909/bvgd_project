import os
import sys
from datetime import datetime

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors

from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

TARGET_DIR = get_file_path('data/in_hoa_don')

# ----------------- CẤU HÌNH TIẾNG VIỆT -----------------
# 1. Tên font sẽ sử dụng trong ReportLab
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'

TEN_DON_VI = AppConfig.TEN_DON_VI
MA_SO_THUE = AppConfig.MA_SO_THUE
DIA_CHI = AppConfig.DIA_CHI
SDT = AppConfig.SDT
LOGO_FILE_NAME =  AppConfig.LOGO_FILE_NAME

LOGO_PATH = get_file_path(LOGO_FILE_NAME)

HOA_DON_HEADER = 'HOÁ ĐƠN BÁN HÀNG'

# Định nghĩa chiều rộng và chiều dài (chiều dài cần đủ lớn)
THERMAL_WIDTH_MM = 30
THERMAL_HEIGHT_MM = 60 # Chiều dài lớn, sẽ được cắt sau

MARGIN_LEFT = 4
FONT_SIZE = 4

LOGO_WIDTH = THERMAL_WIDTH_MM/4 * mm  # Chiều rộng mong muốn của logo (ví dụ: 12mm)
LOGO_HEIGHT =  LOGO_WIDTH # Chiều cao mong muốn của logo (ví dụ: 12mm)

# Chuyển đổi sang ReportLab units (points)
K_WIDTH = THERMAL_WIDTH_MM * mm
K_HEIGHT = THERMAL_HEIGHT_MM * mm

K80 = (K_WIDTH, K_HEIGHT)

try:
    pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
except Exception as e:
    print(f"!!! CẢNH BÁO: Lỗi đăng ký font: {e}")
    print("Sử dụng font ReportLab mặc định (có thể không hiển thị tiếng Việt).")
    # Giữ các tên font ReportLab mặc định để tránh lỗi, nhưng sẽ mất hỗ trợ tiếng Việt
    VIET_FONT = 'Times-Roman'
    VIET_FONT_BOLD = 'Times-Bold'
    VIET_FONT_ITALIC = 'Times-Italic'

# ----------------- 2. DỮ LIỆU MẪU -----------------
fake_data = {
    'MaYTe': 'BN00001',
    'BHYT': '123',
    'HoTen': 'Nguyen Van A',
    'DiaChi': '123 Nguyen Văn Đậu',
    'TongTienThanhToan:': '200.000,000',
    'SoTienBangChu': 'Hai trăm nghìn đồng',
    'HinhThucThanhToan': 'POST BIDV',
}

# ----------------- 3. HÀM VẼ PHIẾU THUỐC -----------------
def get_paragraph_style(font_name, font_size):
    """Tạo ParagraphStyle cho nội dung dịch vụ và Table."""
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        name='ServiceContent',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 2,
        alignment=TA_LEFT,
        spaceAfter=0,
    )

def draw_table(c, x_start, y_start,
               col_widths, rows_data,
               font, font_size) ->  float:
    styleN = get_paragraph_style(font, font_size)
    table_data = []

    for i in range(len(rows_data)):
        table_row = [Paragraph(rows_data[i], styleN)]
        table_data.append(table_row)

    table = Table(table_data, colWidths=[col_widths])
    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0, colors.white),
        ('BOX', (0, 0), (-1, -1), 0, colors.white),
        ('FONTNAME', (0, 0), (-1, -1), font),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),

        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ])

    table.setStyle(table_style)

    table_width, table_height = table.wrapOn(c, 0, 0)
    x_position = x_start
    y_position = y_start - table_height

    table.drawOn(c, x_position, y_position)

    return y_position

def draw_header(c, data):
    width, height = K_WIDTH, K_HEIGHT
    y_start = height - 5

    table_data = [
        TEN_DON_VI,
        'Mã số thuế: ' + MA_SO_THUE,
        'Địa chỉ: ' + DIA_CHI,
        'Điện thoại: ' + SDT
    ]

    y_position = draw_table(c, MARGIN_LEFT, y_start,
                            K_WIDTH - LOGO_WIDTH - MARGIN_LEFT*mm,
                            table_data, VIET_FONT_BOLD, FONT_SIZE)

    # 4. VẼ LOGO
    try:
        c.drawImage(LOGO_PATH, width - LOGO_WIDTH - 5, height - LOGO_HEIGHT - 5,
                    width=LOGO_WIDTH, height=LOGO_HEIGHT)
    except Exception as e:
        print(f"!!! CẢNH BÁO: Không thể vẽ logo từ đường dẫn {LOGO_PATH}: {e}")

    return y_position

def draw_bill_form(c, data):
    width, height = K_WIDTH, K_HEIGHT
    line_y_offset = -6

    y_current = draw_header(c, data)

    y_current += line_y_offset -4
    c.setFont(VIET_FONT, FONT_SIZE * 1.5)
    c.drawCentredString(width/2.0, y_current, HOA_DON_HEADER)

    y_current += line_y_offset -2
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(width / 2.0, y_current, data['NgayThang'])

    # 1. Tạo chuỗi cho tên người mua với markup <font name="VIET_FONT_BOLD">
    nguoi_mua = f"Người mua: <font name='{VIET_FONT_BOLD}'>{data.get('HoTen', '')}</font>"
    ten_don_vi = f"Tên đơn vị: <font name='{VIET_FONT_BOLD}'>{data.get('TenDonVi', '')}</font>"
    ma_so_thue = f"Mã số thuế: <font name='{VIET_FONT_BOLD}'>{data.get('MST', '')}</font>"
    dia_chi = f"Địa chỉ: <font name='{VIET_FONT_BOLD}'>{data.get('DiaChi', '')}</font>"
    tong_tien = f" <font name='{VIET_FONT_BOLD}'>Tổng tiền thanh toán: {data.get('TongTienThanhToan', '')}</font>"
    so_tien_bang_chu = f"<font name='{VIET_FONT_BOLD}'>Số tiền viết bằng chữ: </font>{data.get('SoTienBangChu', '')}"

    y_current += line_y_offset / 2
    table_data = [
        nguoi_mua,
        ten_don_vi,
        ma_so_thue,
        dia_chi,
        tong_tien,
        so_tien_bang_chu
    ]
    y_position = draw_table(c, MARGIN_LEFT, y_current,
                            K_WIDTH - MARGIN_LEFT * mm,
                            table_data, VIET_FONT, FONT_SIZE)

    y_current = y_position + line_y_offset
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(K_WIDTH/4, y_current, f'Người mua')
    c.drawCentredString(K_WIDTH/4 + K_WIDTH/2, y_current, f'Người bán')

    y_current += line_y_offset
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(K_WIDTH / 4, y_current, f'(Ký, ghi rõ họ tên)')
    c.drawCentredString(K_WIDTH / 4 + K_WIDTH / 2, y_current, f'(Ký, ghi rõ họ tên)')

    y_current += line_y_offset
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(K_WIDTH / 4 + K_WIDTH / 2, y_current, f'(Họ tên nguời bán)')

    y_current += line_y_offset * 1.5
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y_current, f'Mã tra cứu (Mã số bệnh nhân): {data.get('MaYTe', '')}')

    y_current += line_y_offset
    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawString(MARGIN_LEFT, y_current, f'Hình thức thanh toán: {data.get('HinhThucThanhToan', '')}')

# ----------------- 4. HÀM TẠO TÊN FILE -----------------
def create_file_name(data):
    # 1. Tạo tên file
    ma_bhyt = data.get('BHYT', 'NO_BHYT')

    current_datetime = datetime.now()

    chuoi_ngay_thang_nam = current_datetime.strftime("Ngày %d tháng %m năm %Y")

    data['NgayThang'] = chuoi_ngay_thang_nam

    # Format ngày giờ thành chuỗi an toàn cho tên file (không chứa ký tự / và :)
    # Ví dụ: 12_11_2025__14_25_48
    safe_date_string = current_datetime.strftime("%d_%m_%Y__%H_%M_%S")

    # Tên file PDF
    file_name = f"HoaDon_{ma_bhyt}_{safe_date_string}.pdf"

    return file_name

# ----------------- 5. HÀM TẠO FILE PDF TOA THUỐC -----------------
def create_and_open_pdf_for_printing(data):
    """Tạo file PDF với tên file là mã BHYT và ngày tiếp nhận, sau đó mở file."""
    try:
        # 1. Tạo thư mục nếu chưa có. exist_ok=True tránh báo lỗi nếu thư mục đã tồn tại
        os.makedirs(TARGET_DIR, exist_ok=True)
        pdf_path = os.path.join(TARGET_DIR, create_file_name(data))

        # 2. Tạo PDF
        c = canvas.Canvas(pdf_path, pagesize=K80)
        draw_bill_form(c, data)
        c.showPage()
        c.save()

        # 3. Mở file PDF
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi khi tạo hoặc mở PDF: {e}")

if __name__ == "__main__":
    create_and_open_pdf_for_printing(fake_data)