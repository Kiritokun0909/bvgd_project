import os
import sys
from datetime import datetime

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors

from app.core.print_file import print_file_win32
from app.core.utils import draw_multi_column_table

from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

TARGET_DIR = get_file_path('data/in_hoa_don')

# ----------------- 1. CẤU HÌNH CHUNG -----------------
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'

TEN_DON_VI = AppConfig.TEN_DON_VI
MA_SO_THUE = AppConfig.MA_SO_THUE
DIA_CHI = AppConfig.DIA_CHI
SDT = AppConfig.SDT
LOGO_FILE_NAME = AppConfig.LOGO_FILE_NAME
LOGO_PATH = get_file_path(LOGO_FILE_NAME)

HOA_DON_HEADER = 'HOÁ ĐƠN BÁN HÀNG'

# Kích thước giấy in nhiệt (K80 = 80mm, K57 = 57mm)
THERMAL_WIDTH_MM = 57
MARGIN_LEFT = 2
MARGIN_RIGHT = 2
FONT_SIZE = 6

# Quy đổi ra point (1mm = 2.83 point)
K_WIDTH = THERMAL_WIDTH_MM * mm
LOGO_WIDTH = 15 * mm
LOGO_HEIGHT = 15 * mm

# Đăng ký Font
try:
    pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
except Exception as e:
    # print(f"!!! CẢNH BÁO Font: {e}")
    VIET_FONT = 'Helvetica'
    VIET_FONT_BOLD = 'Helvetica-Bold'
    VIET_FONT_ITALIC = 'Helvetica-Oblique'

# ----------------- 2. DỮ LIỆU MẪU -----------------
fake_data = {
    'MaYTe': 'BN00001',
    'BHYT': 'DN4790000000000',
    'HoTen': 'Nguyễn Văn A',
    'DiaChi': '123 Nguyễn Văn Đậu, Bình Thạnh, TP.HCM',
    'TenDonVi': 'Công ty TNHH ABC',  # Đã mở comment để test
    'MST': '031000000',  # Đã mở comment để test
    'TongTienThanhToan': '365.000',
    'SoTienBangChu': 'Ba trăm sáu mươi lăm nghìn đồng chẵn',
    'HinhThucThanhToan': 'Tiền mặt',
    'NgayThang': datetime.now().strftime("Ngày %d tháng %m năm %Y")  # Tạo sẵn để đo độ dài
}


# ----------------- 3. CÁC HÀM HỖ TRỢ TÍNH TOÁN CHIỀU CAO -----------------

def measure_table_height(data, col_widths, font, font_size, padding=0):
    """
    Hàm giả lập tạo bảng để đo chiều cao thực tế
    """
    style = ParagraphStyle('Test', fontName=font, fontSize=font_size, leading=font_size + 2)
    processed_data = []
    for row in data:
        p_row = [Paragraph(str(cell), style) for cell in row]
        processed_data.append(p_row)

    table = Table(processed_data, colWidths=col_widths)

    style_cmds = [
        ('LEFTPADDING', (0, 0), (-1, -1), padding),
        ('RIGHTPADDING', (0, 0), (-1, -1), padding),
        ('TOPPADDING', (0, 0), (-1, -1), padding),
        ('BOTTOMPADDING', (0, 0), (-1, -1), padding),
    ]
    table.setStyle(TableStyle(style_cmds))

    w, h = table.wrap(K_WIDTH, 0)
    return h


def calculate_needed_height(data):
    """
    Tính tổng chiều dài cần thiết dựa trên hàm draw_bill_form mới
    """
    total_h = 0
    w_full = K_WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * mm

    # 1. Header (Logo + Thông tin đơn vị)
    # Trong draw: Text bên trái logo, Logo bên phải.
    # Chiều cao sẽ là cái nào lớn hơn giữa Logo và Text + Margin sau đó

    header_rows = [[TEN_DON_VI], ['Mã số thuế: ' + MA_SO_THUE], ['Địa chỉ: ' + DIA_CHI], ['Điện thoại: ' + SDT]]
    text_h = measure_table_height(header_rows, [w_full - LOGO_WIDTH - 2 * mm], VIET_FONT_BOLD, FONT_SIZE, padding=0)

    # Trong draw có dòng: y_current -= 5 * mm (Sau header)
    # Và y_start bắt đầu từ -3mm
    section1_h = max(LOGO_HEIGHT, text_h) + 5 * mm + 3 * mm
    total_h += section1_h

    # 2. Tiêu đề "HOÁ ĐƠN" + Ngày tháng
    # Font Title 1.3x + Spacing 3pt
    title_h = (FONT_SIZE * 1.3) + 3
    # Font Date 1x + Spacing 2mm
    date_h = FONT_SIZE + 2 * mm

    total_h += title_h + date_h

    # 3. Bảng thông tin khách hàng
    info_rows = [
        [f"Người mua: {data.get('HoTen', '')}"],
        [f"Đơn vị: {data.get('TenDonVi', '')}"],
        [f"Mã số thuế: {data.get('MST', '')}"],
        [f"Địa chỉ: {data.get('DiaChi', '')}"]
    ]
    # Padding = 0 như trong draw
    info_h = measure_table_height(info_rows, [w_full], VIET_FONT, FONT_SIZE, padding=0)

    # Trong draw: y_current -= 1 * mm (Sau bảng khách hàng)
    total_h += info_h + 1 * mm

    # 4. Tổng tiền (Nối tiếp ngay sau khách hàng theo code mới)
    total_rows = [
        [f"Tổng tiền: {data.get('TongTienThanhToan', '')}"],
        [f"Bằng chữ: {data.get('SoTienBangChu', '')}"]
    ]
    money_h = measure_table_height(total_rows, [w_full], VIET_FONT, FONT_SIZE, padding=0)

    # Trong draw: y_current -= 2 * mm (Sau bảng tiền)
    total_h += money_h + 2 * mm

    # 5. Footer (Chữ ký)
    footer_data = [['Người mua', 'Người bán'], ['(Ký, ghi rõ họ tên)', '(Ký, ghi rõ họ tên)']]
    footer_table_h = measure_table_height(footer_data, [w_full / 2, w_full / 2], VIET_FONT, FONT_SIZE, padding=0)

    # Khoảng trống ký: 5mm
    gap_sign = 5 * mm
    # Dòng (Admin): Font size
    admin_h = FONT_SIZE

    # Trong draw: y_current -= 5 * mm (Sau phần Admin)
    total_h += footer_table_h + gap_sign + admin_h + 5 * mm

    # 6. Mã tra cứu cuối cùng
    # 2 dòng text italic: Mã BN và Thanh toán
    bottom_h = (FONT_SIZE - 1) * 2  # +10 point khoảng cách dòng phụ
    total_h += bottom_h

    return total_h


# ----------------- 4. LOGIC VẼ HOÁ ĐƠN -----------------

def draw_bill_form(c, data, total_height):
    y_current = total_height - 3 * mm
    x_left = MARGIN_LEFT * mm
    w_full = K_WIDTH - (MARGIN_LEFT + MARGIN_RIGHT) * mm

    # --- 1. HEADER ---
    try:
        c.drawImage(LOGO_PATH, K_WIDTH - LOGO_WIDTH - x_left, y_current - LOGO_HEIGHT,
                    width=LOGO_WIDTH, height=LOGO_HEIGHT, mask='auto')
    except:
        pass

    header_data = [
        [TEN_DON_VI],
        ['Mã số thuế: ' + MA_SO_THUE],
        ['Địa chỉ: ' + DIA_CHI],
        ['Điện thoại: ' + SDT]
    ]

    # Cột text bên trái logo
    y_current = draw_multi_column_table(
        c, x_left, y_current,
        header_data, [w_full - LOGO_WIDTH - 2 * mm], ['L'],
        VIET_FONT_BOLD, FONT_SIZE,
        border_width=0, padding=0
    )

    # Đảm bảo xuống dòng đủ khoảng cách kể cả khi Text ngắn hơn Logo
    # Logic: Tính điểm đáy của Header (dựa trên cái nào thấp hơn giữa Logo và Text)
    header_bottom_limit = (total_height - 3 * mm) - max(LOGO_HEIGHT, (total_height - 3 * mm - y_current))

    # Reset y_current về điểm đáy an toàn nhất
    y_current = min(y_current, (total_height - 3 * mm) - LOGO_HEIGHT)

    y_current -= 5 * mm

    # --- 2. TIÊU ĐỀ ---
    c.setFont(VIET_FONT_BOLD, FONT_SIZE * 1.3)
    c.drawCentredString(K_WIDTH / 2, y_current, HOA_DON_HEADER)
    y_current -= (FONT_SIZE + 3)

    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(K_WIDTH / 2, y_current, data.get('NgayThang', ''))
    y_current -= 2 * mm

    # --- 3. THÔNG TIN KHÁCH HÀNG ---
    customer_rows = [
        [f"Người mua: <font name='{VIET_FONT_BOLD}'>{data.get('HoTen', '')}</font>"],
        [f"Đơn vị: <font name='{VIET_FONT_BOLD}'>{data.get('TenDonVi', '')}</font>"],
        [f"Mã số thuế: <font name='{VIET_FONT_BOLD}'>{data.get('MST', '')}</font>"],
        [f"Địa chỉ: <font name='{VIET_FONT_BOLD}'>{data.get('DiaChi', '')}</font>"],
    ]

    y_current = draw_multi_column_table(
        c, x_left, y_current,
        customer_rows, [w_full], ['L'],
        VIET_FONT, FONT_SIZE,
        border_width=0, padding=0
    )
    y_current -= 1 * mm

    # --- 5. TỔNG TIỀN (Đã bỏ qua bảng sản phẩm theo yêu cầu) ---
    total_rows = [
        [f"Tổng tiền thanh toán: <font name='{VIET_FONT_BOLD}'>{data.get('TongTienThanhToan', '')}</font>"],
        [f"Số tiền viết bằng chữ: <font name='{VIET_FONT_ITALIC}'>{data.get('SoTienBangChu', '')}</font>"]
    ]
    y_current = draw_multi_column_table(
        c, x_left, y_current,
        total_rows, [w_full], ['L'],
        VIET_FONT, FONT_SIZE,
        border_width=0, padding=0
    )
    y_current -= 2 * mm

    # --- 6. FOOTER ---
    footer_data = [
        ['Người mua', 'Người bán'],
        ['(Ký, ghi rõ họ tên)', '(Ký, ghi rõ họ tên)']
    ]
    y_current = draw_multi_column_table(
        c, x_left, y_current,
        footer_data, [w_full / 2, w_full / 2], ['C', 'C'],
        VIET_FONT, FONT_SIZE,
        border_width=0, padding=0
    )

    y_current -= 5 * mm

    c.setFont(VIET_FONT, FONT_SIZE)
    c.drawCentredString(x_left + w_full * 0.75, y_current, f"{data.get('NguoiThuTien', 'Nguoi thu tien')}")

    # --- 7. MÃ TRA CỨU ---
    y_current -= 5 * mm
    c.setFont(VIET_FONT_ITALIC, FONT_SIZE - 1)
    c.drawString(x_left, y_current, f"Mã tra cứu (Mã bệnh nhân): {data.get('MaYTe', '')}")
    c.drawString(x_left, y_current - 10, f"Thanh toán {data.get('HinhThucThanhToan', '')}")


# ----------------- 5. TẠO VÀ MỞ FILE -----------------
def create_file_name(data):
    ma_bhyt = data.get('BHYT', 'NO_BHYT')
    current_datetime = datetime.now()
    # Cập nhật ngày tháng vào data để dùng chung cho cả tính toán và vẽ
    data['NgayThang'] = current_datetime.strftime("Ngày %d tháng %m năm %Y")
    safe_date = current_datetime.strftime("%d%m%Y_%H%M%S")
    return f"HoaDon_{ma_bhyt}_{safe_date}.pdf"


def create_and_open_pdf_for_printing(data):
    try:
        os.makedirs(TARGET_DIR, exist_ok=True)
        file_name = create_file_name(data)
        pdf_path = os.path.join(TARGET_DIR, file_name)

        # BƯỚC 1: Tính toán
        needed_height = calculate_needed_height(data)
        final_height = needed_height + 5 * mm  # Cộng thêm 5mm margin dưới cùng an toàn

        # print(f"Chiều dài giấy: {final_height / mm:.1f} mm")

        # BƯỚC 2: Tạo Canvas
        c = canvas.Canvas(pdf_path, pagesize=(K_WIDTH, final_height))

        # BƯỚC 3: Vẽ
        draw_bill_form(c, data, final_height)

        c.showPage()
        c.save()

        print_file_win32(pdf_path)
        # BƯỚC 4: Mở file
        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_and_open_pdf_for_printing(fake_data)