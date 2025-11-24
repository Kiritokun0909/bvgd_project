from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# --- IMPORT UTILS ---
try:
    from app.core.utils import draw_multi_column_table
except ImportError:
    from utils import draw_multi_column_table

from app.utils.create_barcode import generate_ma_y_te_barcode
from app.utils.create_qr_code import generate_medical_qr_code
from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig

TARGET_DIR = get_file_path('data/in_phieu_toa_thuoc')

# ----------------- CẤU HÌNH TIẾNG VIỆT -----------------
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'

PHIEU_TOA_THUOC_HEADER = 'ĐƠN THUỐC BHYT'
SO_Y_TE = AppConfig.SO_Y_TE
TEN_DON_VI = AppConfig.TEN_DON_VI

try:
    pdfmetrics.registerFont(TTFont(VIET_FONT, 'C:/Windows/Fonts/times.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_BOLD, 'C:/Windows/Fonts/timesbd.ttf'))
    pdfmetrics.registerFont(TTFont(VIET_FONT_ITALIC, 'C:/Windows/Fonts/timesi.ttf'))
except Exception as e:
    VIET_FONT = 'Times-Roman'
    VIET_FONT_BOLD = 'Times-Bold'
    VIET_FONT_ITALIC = 'Times-Italic'

# ----------------- 2. DỮ LIỆU MẪU (Test thuốc tên dài) -----------------
fake_data = {
    "PhongKham": "Nội tim mạch (P112)",
    "TenBacSi": "Bs. Nguyễn Thị C",
    "NgayTiepNhan": "30/10/2025 07:01:49",
    "NgayKham": "30",
    "ThangKham": "10",
    "NamKham": "2025",
    "MaYTe": "123",
    "HoTen": "NGUYỄN VĂN A",
    "Tuoi": "87",
    "GioiTinh": "Nam",
    "DiaChi": "Số 8 Đường Đồng Thái, Phường Bến Nghé, Quận 1, TP.HCM",
    "SDT": "0908637xxx",
    "BHYT": "CT27979318716",
    "DoiTuong": "37 BHYT 100%",
    "ChanDoan": "Tăng huyết áp - Rối loạn lipid máu",
    "Mach": "80",
    "HA": "136/62",
    "NhietDo": "37",
    "CanNang": "65.00",
    "SoNgayHenTaiKham": "28",
    "NgayHenTaiKham": "27/11/2025",
    "DrNote": "Hạn chế ăn mặn.",

    # Dữ liệu thuốc test wrap text
    "ToaThuoc": [
        {
            "STT": "1",
            "TenThuoc": "Amoxicillin Trihydrate Clavulanate Potassium",  # Tên rất dài
            "TenThuocPhu": "(Augmentin 1g), 1000mg",  # Tên phụ
            "DonViTinh": "Viên",
            "Sang": "1", "Trua": "0", "Chieu": "0", "Toi": "1",
            "SoNgay": "7", "SoLuong": "14"
        },
        {
            "STT": "2",
            "TenThuoc": "Paracetamol",
            "TenThuocPhu": "(Panadol Extra)",
            "DonViTinh": "Viên",
            "Sang": "1", "Trua": "1", "Chieu": "1", "Toi": "1",
            "SoNgay": "5", "SoLuong": "20"
        },
    ]
}


# ----------------- 3. HÀM VẼ PHIẾU THUỐC -----------------
def draw_drug_form(c, data, thong_tin_qrcode):
    width, height = A5
    margin_left = 30
    w_content = width - (margin_left * 2)

    # --- HEADER ---
    c.setFont(VIET_FONT, 9)
    y_start = height - 30

    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left, y_start, SO_Y_TE)
    c.drawString(margin_left, y_start - 10, TEN_DON_VI)
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_start - 20, data.get('PhongKham', ''))

    try:
        c.drawImage(thong_tin_qrcode, width - margin_left * 2, y_start - 12, 40, 40)
    except:
        pass

    c.setFont(VIET_FONT_BOLD, 10)
    c.drawRightString(width - margin_left, y_start - 20, data.get('MaYTe', ''))
    c.setFont(VIET_FONT, 9)
    c.drawRightString(width - margin_left, y_start - 30, data.get('DoiTuong', ''))

    c.setFont(VIET_FONT_BOLD, 12)
    c.drawCentredString(width / 2, y_start - 50, PHIEU_TOA_THUOC_HEADER)

    # --- THÔNG TIN BỆNH NHÂN ---
    y_info = y_start - 70

    # Dòng 1: Họ tên - Tuổi...
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, "Họ tên: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 35, y_info, data.get('HoTen', ''))
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 160, y_info, "Tuổi: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 185, y_info, data.get('Tuoi', ''))
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 230, y_info, "Cân nặng: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 275, y_info, data.get('CanNang', ''))
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 320, y_info, "Giới tính: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 355, y_info, data.get('GioiTinh', ''))

    y_info -= 12
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, f"Mã số thẻ BHYT: {data.get('BHYT', '')}")
    y_info -= 2

    # Địa chỉ
    dia_chi_str = f"Địa chỉ: <font name='{VIET_FONT_BOLD}'>{data.get('DiaChi', '')}</font>"
    y_info = draw_multi_column_table(c, margin_left, y_info, [[dia_chi_str]], [w_content], ['L'], VIET_FONT, 9,
                                     border_width=0, padding=0)
    y_info -= 2

    # SĐT + Ngày
    sdt_str = f"Số ĐT: <font name='{VIET_FONT_BOLD}'>{data.get('SDT', '')}</font>"
    ngay_tn_str = f"Ngày tiếp nhận: <font name='{VIET_FONT_BOLD}'>{data.get('NgayTiepNhan', '')}</font>"
    y_info = draw_multi_column_table(c, margin_left, y_info, [[sdt_str, ngay_tn_str]],
                                     [w_content * 0.4, w_content * 0.6], ['L', 'L'], VIET_FONT, 9, border_width=0,
                                     padding=0)
    y_info -= 2

    # Chẩn đoán
    chan_doan_str = f"Chẩn đoán: <font name='{VIET_FONT_BOLD}'>{data.get('ChanDoan', '')}</font>"
    y_info = draw_multi_column_table(c, margin_left, y_info, [[chan_doan_str]], [w_content], ['L'], VIET_FONT, 9,
                                     border_width=0, padding=0)
    y_info -= 2

    # Sinh tồn
    line_vital = [f"Mạch: {data.get('Mach', '')} l/p", f"HA: {data.get('HA', '')} mmHg",
                  f"Nhiệt: {data.get('NhietDo', '')} °C", "ĐH: ......"]
    y_info = draw_multi_column_table(c, margin_left, y_info, [line_vital], [w_content * 0.25] * 4, ['L', 'L', 'L', 'R'],
                                     VIET_FONT, 9, border_width=0, padding=0)

    # --- DANH SÁCH THUỐC ---
    Y_BREAK_POINT = 50  # Điểm ngắt trang
    y_drug = y_info - 10
    # c.setLineWidth(0.5)
    # c.line(margin_left, y_drug, width - margin_left, y_drug)  # Kẻ ngang phân cách
    # y_drug -= 5  # Dịch xuống sau dòng kẻ

    # Định nghĩa độ rộng các cột cho dòng thuốc
    # Cấu trúc: [STT, Tên thuốc + Tên phụ, ĐVT, SL]
    w_stt = 20
    w_sl = 40
    w_dvt = 40
    w_ten = w_content - w_stt - w_sl - w_dvt
    drug_col_widths = [w_stt, w_ten, w_dvt, w_sl]
    drug_col_aligns = ['L', 'L', 'L', 'R']  # SL căn phải

    for drug in data.get('ToaThuoc', []):
        # 1. Check Page Break (Ước lượng an toàn: 40pt cho 1 thuốc)
        if y_drug < Y_BREAK_POINT + 40:
            c.showPage()
            y_drug = height - 40
            c.setFont(VIET_FONT, 9)

        # 2. Chuẩn bị dữ liệu dòng Tên thuốc
        # Kết hợp Tên chính (Đậm) và Tên phụ (Nghiêng) vào 1 ô Paragraph
        ten_thuoc_full = f"<b>{drug.get('TenThuoc', '')}</b> <font name='{VIET_FONT_ITALIC}'>{drug.get('TenThuocPhu', '')}</font>"

        row_data = [
            drug.get('STT', ''),
            ten_thuoc_full,
            drug.get('DonViTinh', ''),
            f"SL: <b>{drug.get('SoLuong', '')}</b>"  # In đậm số lượng
        ]

        # 3. Vẽ dòng Tên thuốc (Row 1)
        # Hàm này trả về toạ độ Y SAU KHI vẽ xong (đã tính wrap text)
        y_after_name = draw_multi_column_table(
            c, margin_left, y_drug,
            [row_data],
            drug_col_widths,
            drug_col_aligns,
            VIET_FONT, 9,
            border_width=0, padding=0
        )

        # 4. Vẽ dòng Cách dùng (Row 2) ngay bên dưới
        y_usage = y_after_name - 2  # Cách dòng tên thuốc 2pt

        c.setFont(VIET_FONT, 8)
        # Vẽ text hướng dẫn
        c.drawString(margin_left + 20, y_usage - 8, f"Sáng: {drug.get('Sang', '-')}")
        c.drawString(margin_left + 80, y_usage - 8, f"Trưa: {drug.get('Trua', '-')}")
        c.drawString(margin_left + 140, y_usage - 8, f"Chiều: {drug.get('Chieu', '-')}")
        c.drawString(margin_left + 200, y_usage - 8, f"Tối: {drug.get('Toi', '-')}")

        # Vẽ các đường kẻ mờ dưới chân số lượng (như mẫu cũ)
        c.setLineWidth(0.3)
        c.line(margin_left + 35, y_usage - 10, margin_left + 60, y_usage - 10)  # Line Sáng
        c.line(margin_left + 95, y_usage - 10, margin_left + 120, y_usage - 10)  # Line Trưa
        c.line(margin_left + 160, y_usage - 10, margin_left + 180, y_usage - 10)  # Line Chiều
        c.line(margin_left + 215, y_usage - 10, margin_left + 240, y_usage - 10)  # Line Tối

        # Số ngày (Căn phải)
        c.setFont(VIET_FONT_ITALIC, 8)
        c.drawRightString(width - margin_left, y_usage - 8, f"({drug.get('SoNgay', '')} ngày)")

        # 5. Cập nhật y_drug cho thuốc tiếp theo
        # Trừ thêm khoảng cách cho dòng usage (khoảng 15pt) + khoảng cách giữa các thuốc (5pt)
        y_drug = y_usage - 15

        # --- FOOTER ---
    if y_drug - 80 < Y_BREAK_POINT:
        c.showPage()
        y_drug = height - 40

    y_footer = y_drug - 10
    center_right_x = width * 0.75

    # c.setFont(VIET_FONT_BOLD, 9)
    # c.drawString(margin_left, y_footer, "Lời dặn:")
    note_content = data.get('DrNote', '')
    tong_tien_thuoc = f'Tổng tiền thuốc: {data.get('TongTienThuoc','0,000')} VNĐ'
    tong_benh_nhan_tra = f'Bệnh nhân thanh toán: {data.get('TongBenhNhanTra','0,000')} VNĐ'
    y_note_end = draw_multi_column_table(c, margin_left, y_footer,
                                         [
                                             ['Lời dặn:', tong_tien_thuoc],
                                             [note_content, tong_benh_nhan_tra]
                                         ],
                                         [w_content * 0.4, w_content * 0.6],
                                         ['L', 'R'],
                                         VIET_FONT, 8, border_width=0, padding=1)

    y_footer = y_note_end - 10
    c.setFont(VIET_FONT_ITALIC, 9)
    c.drawCentredString(center_right_x, y_footer,
                        f"Ngày {data.get('NgayKham', '')} tháng {data.get('ThangKham', '')} năm {data.get('NamKham', '')}")
    y_footer -= 12
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_footer, "Bác sĩ điều trị")
    y_footer -= 40
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_footer, data.get('TenBacSi', ''))


# --- INIT ---
def create_file_name(data):
    return f"DonThuoc_{data.get('BHYT', 'NoID')}_{data.get('NgayKham', '00')}.pdf"


def create_and_open_pdf_for_printing(data):
    try:
        os.makedirs(TARGET_DIR, exist_ok=True)
        pdf_path = os.path.join(TARGET_DIR, create_file_name(data))
        # Mock QR/Barcode calls if needed
        thong_tin_qrcode = generate_medical_qr_code(
            ma_y_te=data.get('MaYTe', ''),
            so_bhyt=data.get('BHYT', ''),
            doi_tuong=data.get('MaDoiTuong', ''),
            ho_ten=data.get('HoTen', ''),
            tuoi=data.get('Tuoi', ''),
            gioi_tinh=data.get('GioiTinh', ''),
            dia_chi=data.get('DiaChi', ''),
            so_dien_thoai=data.get('SDT', ''),
            so_tien=data.get('TongBenhNhanTra', '0,000') + ' VND',
        )

        c = canvas.Canvas(pdf_path, pagesize=A5)
        draw_drug_form(c, data, thong_tin_qrcode)
        c.showPage()
        c.save()

        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')
    except Exception as e:
        print(f"Err: {e}")


if __name__ == "__main__":
    create_and_open_pdf_for_printing(fake_data)