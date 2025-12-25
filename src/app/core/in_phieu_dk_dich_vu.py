from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import sys

from app.core.print_file import print_file_win32

# --- IMPORT UTILS ---
try:
    from app.core.utils import draw_multi_column_table
except ImportError:
    from utils import draw_multi_column_table

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
MARGIN_RIGHT = 15
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

# Tiêu đề Form
PHIEU_CHI_DINH_HEADER = 'PHIẾU CHỈ ĐỊNH'
TARGET_DIR = get_file_path('data/in_phieu_chi_dinh')

# Cấu hình Barcode/QR Code
BARCODE_WIDTH = 100
BARCODE_HEIGHT = 30

# Cấu hình Vị trí
MIN_FOOTER_SPACE = 80  # Khoảng trống tối thiểu bên dưới để vẽ footer

# Chiều rộng cột cho bảng Dịch vụ (Tổng = CONTENT_WIDTH)
# CONTENT_WIDTH ~ 118mm
# Cấu trúc: [STT, Tên dịch vụ, SL, Nơi thực hiện]
COL_WIDTHS = [
    10 * mm,  # STT
    60 * mm,  # Tên dịch vụ (Ưu tiên rộng nhất)
    15 * mm,  # Số lượng
    CONTENT_WIDTH - (85 * mm)  # Nơi thực hiện (Phần còn lại)
]
COL_ALIGNS = ['C', 'L', 'C', 'C']

# ----------------- CẤU HÌNH FONT TIẾNG VIỆT -----------------
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'
FONT_SIZE_BODY = 9
FONT_SIZE_HEADER = 10

try:
    pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
except Exception as e:
    print(f"!!! CẢNH BÁO: Lỗi đăng ký font: {e}")
    VIET_FONT = 'Times-Roman'
    VIET_FONT_BOLD = 'Times-Bold'
    VIET_FONT_ITALIC = 'Times-Italic'

# ----------------- 2. DỮ LIỆU MẪU -----------------
fake_data = {
    'TenBenhVien': 'BỆNH VIỆN ABC',
    'PhongKham': 'Nội tim mạch (P112)',
    'CSKH': '0123',
    'MaYTe': '701310.09081020',
    'BHYT': 'CT2797931871655',
    'DoiTuong': '37 BHYT 80%',
    'HoTen': 'TẠ THỊ HẢI',
    'Tuoi': '87',
    'GioiTinh': 'Nữ',

    # Dữ liệu dài để test xuống dòng
    'DiaChi': 'Số 8 Đường Đồng Thái, Phường Bến Nghé, Quận 1, TP. Hồ Chí Minh (Địa chỉ rất dài)',
    'SDT': '0908637897',
    'ChanDoan': 'TĂNG HUYẾT ÁP - RỐI LOẠN LIPID MÁU - ĐÁI THÁO ĐƯỜNG TYPE 2 BIẾN CHỨNG',
    'GhiChu': 'Bệnh nhân nhịn ăn sáng để xét nghiệm máu.',

    'SoTien': '70.600',
    'TongBenhNhanTra': '800.153',
    'NgayTao': '30/10/2025 07:01:49',
    'TenBacSi': 'Bs. Nguyễn Thị C',
    'DichVu': [
        {
            'MaNhomDichVu': 'DM001',
            'TenNhomDichVu': 'NHÓM DỊCH VỤ 1: XÉT NGHIỆM VÀ KHÁM TỔNG QUÁT',
            'DSDichVu': [
                {"STT": f'{i}',
                 "MaDichVu": f"DV{i:03d}",
                 # Tên dịch vụ dài để test wrap
                 "TenDichVu": f"Dịch Vụ {i} - Xét nghiệm sinh hóa máu toàn phần (32 chỉ số) phân tích tự động",
                 "SoLuong": "1", "NoiThucHien": f"P. {i:02d}"}
                for i in range(1, 15)
            ]
        },
    ]
}


# ==============================================================================
# ----------------------------- 3. CÁC HÀM VẼ CHI TIẾT -------------------------
# ==============================================================================

def draw_header_info(c, data, barcode_ma_y_te_path, qr_thong_tin):
    """Vẽ khối thông tin Bệnh viện và Bệnh nhân (Sử dụng Paragraph cho Địa chỉ/Chẩn đoán)."""
    y_start = PAGE_HEIGHT - 30

    # --- 1. Header Logo/Tên viện ---
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(MARGIN_LEFT, y_start, TEN_BENH_VIEN)
    c.setFont(VIET_FONT, 9)
    c.drawString(MARGIN_LEFT, y_start - 10, data.get("PhongKham", ""))

    # QR code thông tin
    try:
        x_qr = PAGE_WIDTH - MARGIN_LEFT - 45
        c.drawImage(qr_thong_tin, x_qr, y_start - 20, 45, 45)
    except:
        pass

    # Thông tin Mã YT/BHYT bên phải
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT - 50, y_start + 10, f'Mã y tế: {data.get("MaYTe", "")}')
    c.setFont(VIET_FONT, 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT - 50, y_start , f'Số BHYT: {data.get("BHYT", "")}')
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT - 50, y_start -10, f'Đối tượng: {data.get("DoiTuong", "")}')

    # Tiêu đề Form
    c.setFont(VIET_FONT_BOLD, 12)
    c.drawCentredString(PAGE_WIDTH / 2, y_start - 50, PHIEU_CHI_DINH_HEADER)

    # --- 2. Thông tin Bệnh nhân (Sử dụng Table để Wrap text) ---
    y_info = y_start - 70

    # Dòng 1: Họ tên - Tuổi - Giới tính (Ít khi bị tràn dòng nên dùng drawString hoặc bảng đơn giản)
    c.setFont(VIET_FONT, 9)
    c.drawString(MARGIN_LEFT, y_info, "Họ tên: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(MARGIN_LEFT + 35, y_info, data.get('HoTen', ''))

    info_tuoi_gt = f"Tuổi: {data.get('Tuoi', '')}      Giới tính: {data.get('GioiTinh', '')}"
    c.setFont(VIET_FONT, 9)
    c.drawRightString(PAGE_WIDTH - MARGIN_LEFT, y_info, info_tuoi_gt)

    y_info -= 12  # Xuống dòng

    # Dòng 2: Địa chỉ (Dài) & SĐT (Ngắn) -> Dùng draw_multi_column_table
    # Chia cột: Địa chỉ 70%, SĐT 30%
    addr_str = f"Địa chỉ: <font name='{VIET_FONT_BOLD}'>{data.get('DiaChi', '')}</font>"
    phone_str = f"SĐT: <font name='{VIET_FONT_BOLD}'>{data.get('SDT', '')}</font>"

    y_info = draw_multi_column_table(
        c, MARGIN_LEFT, y_info,
        [[addr_str, phone_str]],  # Data
        [CONTENT_WIDTH * 0.7, CONTENT_WIDTH * 0.3],  # Widths
        ['L', 'L'],  # Aligns
        VIET_FONT, 9, border_width=0, padding=2
    )
    y_info -= 2

    # Dòng 3: Chẩn đoán (Rất dài)
    chan_doan_str = f"Chẩn đoán: <font name='{VIET_FONT_BOLD}'>{data.get('ChanDoan', '')}</font>"
    y_info = draw_multi_column_table(
        c, MARGIN_LEFT, y_info,
        [[chan_doan_str]],
        [CONTENT_WIDTH],
        ['L'],
        VIET_FONT, 9, border_width=0, padding=0
    )
    y_info -= 2

    # Dòng 4: Ghi chú
    note_str = f"Ghi chú: {data.get('GhiChu', '')}"
    y_info = draw_multi_column_table(
        c, MARGIN_LEFT, y_info,
        [[note_str]], [CONTENT_WIDTH], ['L'],
        VIET_FONT, 8, border_width=0, padding=0
    )
    y_info -= 2

    # Dòng 5: Số tiền (Wrap nếu cần, nhưng thường ngắn)
    money_str = f"Tổng tiền: <font name='{VIET_FONT_BOLD}'>{data.get('SoTien', '')} VNĐ</font>"
    y_info = draw_multi_column_table(
        c, MARGIN_LEFT, y_info,
        [[money_str]], [CONTENT_WIDTH], ['L'],
        VIET_FONT, 9, border_width=0, padding=0
    )

    return y_info - 10  # Trả về vị trí Y để bắt đầu vẽ bảng dịch vụ


def draw_footer_info(c, data, y_current):
    """Vẽ footer (chữ ký)."""
    # Nếu y_current quá thấp, sang trang mới vẽ footer
    if y_current < 60:
        c.showPage()
        y_current = PAGE_HEIGHT - 40

    center_right_x = PAGE_WIDTH - 80
    y_footer = y_current - 10

    # Tổng tiền người bệnh trả
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(MARGIN_LEFT, y_footer, f"Bệnh nhân thanh toán: {data.get('TongBenhNhanTra', '')} VNĐ")

    # Ngày tháng & Bác sĩ
    c.setFont(VIET_FONT_ITALIC, 9)
    c.drawCentredString(center_right_x, y_footer, f"Ngày {data.get('NgayTao', '')}")

    y_footer -= 12
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_footer, "Bác sĩ chỉ định")

    y_footer -= 45  # Khoảng ký
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_footer, data.get('TenBacSi', ''))

    return y_footer


# ==============================================================================
# --------------------------- 4. HÀM VẼ PHIẾU CÓ PHÂN TRANG --------------------
# ==============================================================================

def draw_phieu_chi_dinh_paged(c, data, thu_tu, barcode_ma_y_te_path, qr_thong_tin):
    """Vẽ Phiếu Chỉ Định sử dụng Utility để vẽ bảng dịch vụ và phân trang đơn giản."""

    nhom_dv = data['DichVu'][thu_tu]
    ds_dich_vu = nhom_dv['DSDichVu']

    # 1. Vẽ Header & Thông tin BN (Lần đầu)
    y_current = draw_header_info(c, data, barcode_ma_y_te_path, qr_thong_tin)

    # 2. Vẽ tên nhóm dịch vụ
    c.setFont(VIET_FONT_BOLD, 10)
    c.drawString(MARGIN_LEFT, y_current, nhom_dv['TenNhomDichVu'])
    y_current -= 15

    # 3. Vẽ Header Bảng Dịch vụ (Dùng Utility vẽ 1 dòng header có nền xám)
    header_row = ['STT', 'Tên dịch vụ', 'Số lương', 'Nơi thực hiện']
    y_current = draw_multi_column_table(
        c, MARGIN_LEFT, y_current,
        [header_row], COL_WIDTHS, COL_ALIGNS,
        VIET_FONT_BOLD, 9,
        border_color=colors.black, border_width=0.5,
        header_bg_color=colors.lightgrey, padding=1
    )

    # 4. Vòng lặp vẽ từng dòng dịch vụ
    for item in ds_dich_vu:
        # Kiểm tra ngắt trang
        # Ước lượng 1 dòng dịch vụ wrap text tối đa khoảng 30-40pt.
        # Nếu y_current < MIN_FOOTER_SPACE, ngắt trang.
        if y_current < MIN_FOOTER_SPACE:
            c.showPage()

            # Vẽ lại Header trang mới
            y_current = draw_header_info(c, data, barcode_ma_y_te_path, qr_thong_tin)

            # Vẽ lại tên nhóm
            c.setFont(VIET_FONT_BOLD, 10)
            c.drawString(MARGIN_LEFT, y_current, f"{nhom_dv['TenNhomDichVu']} (Tiếp)")
            y_current -= 15

            # Vẽ lại Header Bảng
            y_current = draw_multi_column_table(
                c, MARGIN_LEFT, y_current,
                [header_row], COL_WIDTHS, COL_ALIGNS,
                VIET_FONT_BOLD, 9,
                border_color=colors.black, border_width=0.5,
                header_bg_color=colors.lightgrey, padding=4
            )

        # Chuẩn bị dữ liệu dòng
        # Item: STT | Tên (Wrap) | SL | Nơi TH
        row_data = [
            item['STT'],
            item['TenDichVu'],  # Utility sẽ tự wrap text này
            item['SoLuong'],
            item['NoiThucHien']
        ]

        # Vẽ dòng bằng Utility
        # Lưu ý: Utility trả về Y mới sau khi vẽ xong dòng đó
        y_current = draw_multi_column_table(
            c, MARGIN_LEFT, y_current,
            [row_data], COL_WIDTHS, COL_ALIGNS,
            VIET_FONT, 9,
            border_color=colors.black, border_width=0.5,
            padding=4  # Padding rộng rãi cho dễ đọc
        )

    # 5. Vẽ Footer cuối cùng
    draw_footer_info(c, data, y_current)


# ==============================================================================
# ------------------------- 5. HÀM TẠO TÊN FILE & RUN --------------------------
# ==============================================================================

def create_file_name(data, thu_tu: int):
    ma_bhyt = data.get('BHYT', 'NO_BHYT')
    ngay_tao = data.get('NgayTao', 'NO_DATE')
    ma_nhom_dv = data['DichVu'][thu_tu]['MaNhomDichVu']
    safe_date_string = ngay_tao.replace('/', '_').replace(':', '_').replace(' ', '__')
    return f"PhieuChiDinh_{ma_bhyt}_{safe_date_string}_{ma_nhom_dv}.pdf"


def create_and_open_pdf_for_printing(data):
    try:
        os.makedirs(TARGET_DIR, exist_ok=True)

        barcode_ma_y_te_path = generate_ma_y_te_barcode(data.get('MaYTe', ''))

        # --- 1. CHUẨN BỊ DATA CHO QR CODE ---
        # Data dịch vụ đang nằm trong các Nhóm (Group), cần làm phẳng (flatten)
        qr_items = []
        list_nhom_dv = data.get('DichVu', [])

        for nhom in list_nhom_dv:
            ds_dv = nhom.get('DSDichVu', [])
            for dv in ds_dv:
                qr_items.append({
                    'id': dv.get('DichVuId', ''),
                    'lg': dv.get('MaLoaiGia', ''),
                    'q': dv.get('SoLuong', '1'),
                    'kht': dv.get('KhongHoTro', 0),
                    'ktt': dv.get('KhongThuTien', 0)
                })

        qr_thong_tin = generate_medical_qr_code(
            ma_y_te=data.get('MaYTe', ''),
            so_bhyt=data.get('BHYT', ''),
            doi_tuong=data.get('DoiTuong', ''),
            ho_ten=data.get('HoTen', ''),
            tuoi=data.get('Tuoi', ''),
            gioi_tinh=data.get('GioiTinh', ''),
            dia_chi=data.get('DiaChi', ''),
            so_dien_thoai=data.get('SDT', ''),
            so_tien=data.get('TongBenhNhanTra', '0'),

            bill_type="DICH_VU",  # Đánh dấu đây là phiếu dịch vụ
            items=qr_items
        )

        for i in range(len(data.get('DichVu', []))):
            file_name = create_file_name(data, i)
            pdf_path = os.path.join(TARGET_DIR, file_name)

            c = canvas.Canvas(pdf_path, pagesize=A5)

            # GỌI HÀM MỚI
            draw_phieu_chi_dinh_paged(c, data, i, barcode_ma_y_te_path, qr_thong_tin)

            c.save()

            print_file_win32(pdf_path)
            if sys.platform == "win32":
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                os.system(f'open "{pdf_path}"')
            else:
                os.system(f'xdg-open "{pdf_path}"')

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_and_open_pdf_for_printing(fake_data)