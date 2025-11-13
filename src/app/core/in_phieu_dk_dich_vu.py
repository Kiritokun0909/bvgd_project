from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER

import os
import sys

from app.utils.create_barcode import generate_ma_y_te_barcode, generate_so_tien_barcode
from app.utils.create_qr_code import generate_medical_qr_code
from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

TEN_BENH_VIEN = AppConfig.TEN_DON_VI


# ==============================================================================
# ----------------------------- 1. CẤU HÌNH CHUNG ------------------------------
# ==============================================================================

# Kích thước trang
PAGE_WIDTH, PAGE_HEIGHT = A5
MARGIN_LEFT = 15
LINE_SPACING_Y = 16

# Tiêu đề Form
PHIEU_CHI_DINH_HEADER = 'PHIẾU CHỈ ĐỊNH'

# Đường dẫn/Cấu hình đầu ra (Đã đổi tên thư mục để phân biệt file phân trang)
TARGET_DIR = get_file_path('data/in_phieu_chi_dinh')

# Cấu hình Barcode/QR Code
BARCODE_WIDTH = 100
BARCODE_HEIGHT = 30

BARCODE_TIEN_WIDTH = 120
BARCODE_TIEN_HEIGHT = 45

# Cấu hình Vị trí
Y_START_HEADER = PAGE_HEIGHT - 30
MIN_FOOTER_SPACE = 130  # Vị trí Y thấp nhất cho phép vẽ bảng (để lại chỗ cho footer)
TABLE_HEADER_HEIGHT = 20  # Chiều cao ước tính cho dòng tiêu đề bảng

# Chiều rộng cột cho bảng Dịch vụ
COL_WIDTHS = [
    10 * mm,  # STT (~28.3pt)
    200,  # Tên dịch vụ
    40,  # Số lượng
    130  # Nơi thực hiện
]
NOI_DUNG_COL_WIDTH = COL_WIDTHS[1]  # Chiều rộng cột Tên dịch vụ để tính wrap

# ----------------- CẤU HÌNH FONT TIẾNG VIỆT -----------------
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'
FONT_SIZE_BODY = 9
FONT_SIZE_HEADER = 10

try:
    # Đảm bảo các font đã được đăng ký (giữ nguyên logic gốc)
    pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
except Exception as e:
    print(f"!!! CẢNH BÁO: Lỗi đăng ký font: {e}")
    VIET_FONT = 'Times-Roman'
    VIET_FONT_BOLD = 'Times-Bold'
    VIET_FONT_ITALIC = 'Times-Italic'

# ----------------- 2. DỮ LIỆU MẪU (Đã cập nhật để test phân trang) -----------------
fake_data = {
    'TenBenhVien': 'BỆNH VIỆN ABC',
    'PhongKham': 'Nội tim mạch (P112)',
    'CSKH': '0123',
    'MaYTe': '701310.09081020',
    'MaBHYT': 'CT2797931871655',
    'DoiTuong': '37 BHYT 80%',
    'HoTen': 'TẠ THỊ HẢI',
    'Tuoi': '87',
    'GioiTinh': 'Nữ',
    'DiaChi': '8 Đồng Thái, Phường Cầu, Tp Hồ Chí Minh',
    'SDT': '0908637897',
    'ChanDoan': 'TĂNG HUYẾT ÁP - RỐI LOẠN LIPID MÁU',
    'GhiChu': '',
    'SoTien': '70.600,000',
    'TongBenhNhanTra': '800.153,000',
    'NgayTao': '30/10/2025 07:01:49',
    'BacSi': 'Bs. Nguyễn Thị C',
    'DichVu': [
        {
            'MaNhomDichVu': 'DM001',
            'TenNhomDichVu': 'NHÓM DỊCH VỤ 1: XÉT NGHIỆM VÀ KHÁM TỔNG QUÁT',
            'DSDichVu': [
                # Thêm 20 dòng để đảm bảo tràn trang A5 (thường chỉ chứa được khoảng 15-18 dòng)
                {"STT": f'{i}',
                 "MaDichVu": f"DV{i:03d}",
                 "TenDichVu": f"Dịch Vụ {i} - Khám Bệnh/Xét Nghiệm - "
                              f"Nội dung mô tả dịch vụ rất dài để đảm bảo nó chiếm ít nhất"
                            ,
                 "SoLuong": "1", "NoiThucHien": f"Phòng {i:02d}"}
                for i in range(1, 20)
            ]
        },
        {
            'MaNhomDichVu': 'DM002',
            'TenNhomDichVu': 'NHÓM DỊCH VỤ 2: CHẨN ĐOÁN HÌNH ẢNH',
            'DSDichVu': [
                {"STT": '1',
                 "MaDichVu": "DV00301", "TenDichVu": "Dịch Vụ 301 - Chụp X-quang Phổi", "SoLuong": "1",
                 "NoiThucHien": "Phòng X-quang A"},
            ]
        }
    ]
}


# ==============================================================================
# ----------------------------- 3. HÀM HỖ TRỢ VẼ/PHÂN TRANG --------------------
# ==============================================================================

def get_paragraph_style(font_name, font_size):
    """Tạo ParagraphStyle cho nội dung dịch vụ và Table."""
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        name='ServiceContent',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 3,  # Dãn dòng
        alignment=TA_LEFT
    )


def get_row_height(item_name, font_style, col_width):
    """Tính toán chiều cao tối thiểu cần thiết cho một dòng dựa trên nội dung."""
    # 1. Tạo Paragraph flowable
    p = Paragraph(item_name, font_style)

    # 2. wrapOn (tính toán chiều cao)
    # col_width: Chiều rộng dành cho cột Tên dịch vụ (NOI_DUNG_COL_WIDTH)
    temp_c = canvas.Canvas('temp_for_height.pdf', pagesize=A5)
    p.wrapOn(temp_c, col_width - 20, 10000)  # Chiều cao ảo 10000

    # 3. Trả về chiều cao đã tính
    # Chiều cao ReportLab trả về đã bao gồm padding cơ bản
    height = p.height

    # Đảm bảo chiều cao tối thiểu, ví dụ 9pt + 3pt leading + 4pt padding = 16pt
    min_height = font_style.fontSize + 8
    return max(height, min_height)


def draw_header_info(c, data,  barcode_ma_y_te_path, qr_thong_tin):
    """Vẽ khối thông tin Bệnh viện và Bệnh nhân."""
    # ------------------ KHỐI CHUNG (HEADER) ------------------
    y_start = Y_START_HEADER

    # Tiêu đề Bệnh viện & PHÒNG KHÁM IN PHIẾU
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(MARGIN_LEFT, y_start, TEN_BENH_VIEN)
    c.setFont(VIET_FONT, 9)
    c.drawString(MARGIN_LEFT, y_start - 10, data["PhongKham"])

    # Mã vạch (Barcode)
    try:
        x_barcode = PAGE_WIDTH - MARGIN_LEFT - BARCODE_WIDTH
        c.drawImage( barcode_ma_y_te_path, x_barcode, y_start - 10, BARCODE_WIDTH, BARCODE_HEIGHT)
    except FileNotFoundError:
        pass

    # QR code thông tin bệnh nhân
    try:
        x_barcode = PAGE_WIDTH - MARGIN_LEFT - BARCODE_WIDTH
        c.drawImage(qr_thong_tin, x_barcode +30, y_start - 165, 45, 45)
    except FileNotFoundError:
        pass

    # Thông tin Mã YT/BHYT/Đối tượng
    c.setFont(VIET_FONT_BOLD, 10)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_start - 20, f'Mã y tế: {data.get('MaYTe', '')}')
    c.setFont(VIET_FONT, 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_start - 35, f'Số BHYT: {data["MaBHYT"]}')
    c.setFont(VIET_FONT_BOLD, 10)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_start - 50, f'Đối tượng: {data["DoiTuong"]}')

    # Tiêu đề Form
    c.setFont(VIET_FONT_BOLD, 12)
    c.drawCentredString(PAGE_WIDTH / 2, y_start - 65, PHIEU_CHI_DINH_HEADER)

    # ------------------ KHỐI THÔNG TIN BỆNH NHÂN ------------------
    y_info = y_start - 90  # Vị trí Y bắt đầu khối thông tin

    c.setFont(VIET_FONT, 9)

    # Dòng 1: Họ tên / Tuổi / Giới tính
    c.drawString(MARGIN_LEFT, y_info, "Họ tên: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(MARGIN_LEFT + 35, y_info, data['HoTen'])
    c.setFont(VIET_FONT, 9)
    info_tuoi_gt = f'Tuổi: {data['Tuoi']}       Giới tính: {data['GioiTinh']}'
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_info, info_tuoi_gt)

    y_info -= LINE_SPACING_Y
    # Dòng 2: Địa Chỉ / Số ĐT
    c.drawString(MARGIN_LEFT, y_info, f"Địa Chỉ: {data['DiaChi']}")
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_info, f"Số ĐT: {data['SDT']}")

    y_info -= LINE_SPACING_Y
    # Dòng 3: Chẩn đoán
    c.drawString(MARGIN_LEFT, y_info, f'Chẩn đoán: {data['ChanDoan']}')

    y_info -= LINE_SPACING_Y
    # Dòng 4: Ghi chú
    c.setFont(VIET_FONT, 8)
    c.drawString(MARGIN_LEFT, y_info, f'Ghi chú: {data['GhiChu']}')

    y_info -= LINE_SPACING_Y
    # Dòng 5: Số tiền
    c.drawString(MARGIN_LEFT, y_info, f'Tổng tiền: {data['SoTien']} VNĐ')

    y_current = y_info - 20
    return y_current


def draw_group_header(c, ten_nhom_dv, y_current):
    """Vẽ tiêu đề nhóm dịch vụ."""
    c.setFont(VIET_FONT_BOLD, FONT_SIZE_HEADER)
    c.drawString(MARGIN_LEFT, y_current, f'{ten_nhom_dv}')
    return y_current - 10


def draw_table_header(c, y_current):
    """Vẽ header của bảng dịch vụ (dòng STT, Tên dịch vụ...)."""
    table_data = [['STT', 'Tên dịch vụ', 'Số lượng', 'Nơi thực hiện']]

    table = Table(table_data, colWidths=COL_WIDTHS, rowHeights=[TABLE_HEADER_HEIGHT])
    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.85, 0.85, 0.85)),
        ('FONTNAME', (0, 0), (-1, 0), VIET_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ])
    table.setStyle(table_style)

    table.wrapOn(c, 0, 0)
    y_position = y_current - TABLE_HEADER_HEIGHT
    table.drawOn(c, MARGIN_LEFT, y_position)

    return y_position


def draw_table_rows(c, start_y, rows_to_draw):
    """Vẽ các dòng dữ liệu của bảng."""
    styleN = get_paragraph_style(VIET_FONT, FONT_SIZE_BODY)

    table_data = []
    row_heights = []
    ROW_BOTTOM_PADDING = 4

    for i, dv in enumerate(rows_to_draw):
        stt = dv['STT']

        # Bọc TenDichVu trong Paragraph để đảm bảo xuống dòng
        p_ten_dv = Paragraph(dv["TenDichVu"], styleN)

        # Tính chiều cao dòng thực tế
        height = get_row_height(dv["TenDichVu"], styleN, NOI_DUNG_COL_WIDTH)
        row_heights.append(height + ROW_BOTTOM_PADDING)

        table_row = [
            str(stt),
            p_ten_dv,
            dv["SoLuong"],
            dv["NoiThucHien"]
        ]
        table_data.append(table_row)

    # 4. Định nghĩa và áp dụng Table Style
    table = Table(table_data, colWidths=COL_WIDTHS, rowHeights=row_heights)

    table_style = TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), VIET_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), FONT_SIZE_BODY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # STT
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Số lượng
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), ROW_BOTTOM_PADDING),
    ])

    table.setStyle(table_style)

    # 5. Tính toán kích thước và vẽ Bảng
    table_width, table_height = table.wrapOn(c, 0, 0)
    x_position = MARGIN_LEFT
    y_position = start_y - table_height

    table.drawOn(c, x_position, y_position)

    # Trả về vị trí Y cuối cùng của bảng
    return y_position, table_height


def draw_footer_info(c, data, y_table_end, barcode_tien_path):
    """Vẽ khối chữ ký/ngày tháng."""
    y_footer_start = y_table_end - 15
    center_right_x = PAGE_WIDTH - 100

    # Ngày tháng
    c.setFont(VIET_FONT, 9)
    benh_nhan_tra = data['TongBenhNhanTra']
    c.drawString(MARGIN_LEFT, y_footer_start, f'Bệnh nhân thanh toán: {benh_nhan_tra} VNĐ')

    # Mã vạch (Barcode)
    # try:
    #     c.drawImage(barcode_tien_path, MARGIN_LEFT, y_footer_start - 75, BARCODE_TIEN_WIDTH, BARCODE_TIEN_HEIGHT)
    # except FileNotFoundError:
    #     pass

    # Ngày tháng
    c.setFont(VIET_FONT, 9)
    ngay_tao_date = data['NgayTao']
    c.drawCentredString(center_right_x, y_footer_start, f'Ngày {ngay_tao_date}')

    # Chữ ký
    c.setFont(VIET_FONT, 9)
    c.drawCentredString(center_right_x, y_footer_start - 15, f'Bác sĩ chỉ định')

    # Bác sĩ
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_footer_start - 65, data["BacSi"])

    return y_footer_start - 55


# ==============================================================================
# --------------------------- 4. HÀM VẼ PHIẾU CÓ PHÂN TRANG --------------------
# ==============================================================================

def draw_drug_form_paged(c, data, thu_tu, barcode_ma_y_te_path,
                         barcode_tien_path, qr_thong_tin):
    """Vẽ Phiếu Chỉ Định có xử lý phân trang cho danh sách dịch vụ."""
    ten_nhom_dv = data['DichVu'][thu_tu]['TenNhomDichVu']
    ds_dich_vu = data['DichVu'][thu_tu]['DSDichVu']

    # Lấy Paragraph Style để tính toán chiều cao dòng
    styleN = get_paragraph_style(VIET_FONT, FONT_SIZE_BODY)

    # # --- Trang 1: Vẽ Header và Thông tin Bệnh nhân ---
    # y_current = draw_header_info(c, data)

    # --- Chuẩn bị phân trang ---
    remaining_services = ds_dich_vu
    stt_counter = 1
    page_count = 1

    while remaining_services:
        if page_count > 1:
            # Nếu là trang thứ 2 trở đi, thêm trang mới và vẽ lại header
            c.showPage()

        # Vẽ lại thông tin header cơ bản (Hospital, Room, Barcode) và Tiêu đề Form
        y_current = draw_header_info(c, data, barcode_ma_y_te_path, qr_thong_tin)

        # Vẽ Tiêu đề Nhóm Dịch vụ (lặp lại)
        y_current = draw_group_header(c, ten_nhom_dv, y_current)

        # 1. Vẽ Header Bảng (lặp lại trên mỗi trang)
        y_current = draw_table_header(c, y_current)

        # Vị trí Y bắt đầu vẽ các dòng
        y_table_start = y_current

        # Chiều cao còn lại trên trang hiện tại (trừ khoảng trống cho Footer)
        max_height_available = y_table_start - MIN_FOOTER_SPACE

        rows_for_this_page = []
        rows_height = 0

        # 2. Lặp qua các dòng còn lại để chọn dòng cho trang này
        i = 0
        while i < len(remaining_services):
            dv = remaining_services[i]

            # Tính chiều cao của dòng hiện tại
            row_height = get_row_height(dv["TenDichVu"], styleN, NOI_DUNG_COL_WIDTH)

            # Kiểm tra xem dòng này có làm tràn trang không
            if rows_height + row_height <= max_height_available:
                rows_for_this_page.append(dv)
                rows_height += row_height
                i += 1
            else:
                # Nếu không thể chứa, kết thúc việc chọn dòng cho trang này
                break

        # 3. Vẽ các dòng đã chọn lên trang hiện tại
        if rows_for_this_page:
            # y_table_end là vị trí Y cuối cùng của bảng đã vẽ
            y_table_end, _ = draw_table_rows(c, y_table_start, rows_for_this_page)

            # Cập nhật STT và danh sách còn lại
            stt_counter += len(rows_for_this_page)
            remaining_services = remaining_services[len(rows_for_this_page):]
        else:
            # Trường hợp không thể chứa bất kỳ dòng nào (rất hiếm)
            print(
                "CẢNH BÁO: Không đủ không gian để vẽ ít nhất một dòng dịch vụ. Tăng MIN_FOOTER_SPACE hoặc giảm kích thước font/dòng.")
            break

        # 4. Vẽ Footer nếu đây là trang cuối cùng
        # if not remaining_services:
        draw_footer_info(c, data, y_table_end, barcode_tien_path)

        page_count += 1

    # --- Kết thúc nhóm dịch vụ ---


# ==============================================================================
# ------------------------- 5. HÀM TẠO TÊN FILE & RUN --------------------------
# ==============================================================================

def create_file_name(data, thu_tu: int):
    """Tạo tên file theo format: PhieuDangKyDichVu_[MaBHYT]_[NgayTao]_[NhomDV].pdf"""
    ma_bhyt = data.get('MaBHYT', 'NO_BHYT')
    ngay_tao = data.get('NgayTao', 'NO_DATE')
    ma_nhom_dv = data['DichVu'][thu_tu]['MaNhomDichVu']

    # Xử lý chuỗi ngày tiếp nhận để loại bỏ ký tự không hợp lệ cho tên file
    safe_date_string = ngay_tao.replace('/', '_').replace(':', '_').replace(' ', '__')

    # Tên file PDF
    file_name = f"PhieuDangKyDichVu_{ma_bhyt}_{safe_date_string}_{ma_nhom_dv}.pdf"
    return file_name


def create_and_open_pdf_for_printing(data):
    """Tạo file PDF cho mỗi nhóm dịch vụ và mở file."""
    try:
        # 1. Tạo thư mục nếu chưa có.
        os.makedirs(TARGET_DIR, exist_ok=True)
        print(f"Đã tạo thư mục đầu ra: {os.path.abspath(TARGET_DIR)}")

        # 1. Tạo thư mục nếu chưa có.
        os.makedirs(TARGET_DIR, exist_ok=True)
        print(f"Đã tạo thư mục đầu ra: {os.path.abspath(TARGET_DIR)}")

        # 2. TẠO BARCODE VÀ LƯU ĐƯỜNG DẪN TẠI ĐÂY
        barcode_ma_y_te_path = generate_ma_y_te_barcode(data.get('MaYTe', ''))
        barcode_tien_path = generate_so_tien_barcode(data['TongBenhNhanTra'])
        qr_thong_tin = generate_medical_qr_code(
            ma_y_te=data.get('MaYTe', ''),
            so_bhyt=data.get('MaBHYT', ''),
            doi_tuong=data.get('DoiTuong', ''),
            ho_ten=data.get('HoTen', ''),
            tuoi=data.get('Tuoi', ''),
            gioi_tinh=data.get('GioiTinh', ''),
            dia_chi=data.get('DiaChi', ''),
            so_dien_thoai=data.get('SDT', ''),
            so_tien=data.get('TongBenhNhanTra', '')
        )

        for i in range(len(data.get('DichVu', 0))):
            file_name = create_file_name(data, i)
            pdf_path = os.path.join(TARGET_DIR, file_name)

            # 2. Tạo PDF
            c = canvas.Canvas(pdf_path, pagesize=A5)
            # SỬ DỤNG HÀM PHÂN TRANG MỚI
            draw_drug_form_paged(c, data, i, barcode_ma_y_te_path, barcode_tien_path,
                                 qr_thong_tin)
            c.save()

            print(f"Đã tạo file: {file_name}")

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