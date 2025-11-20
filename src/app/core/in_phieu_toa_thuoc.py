from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

from app.utils.create_barcode import generate_ma_y_te_barcode
from app.utils.create_qr_code import generate_medical_qr_code
from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig


TARGET_DIR = get_file_path('data/in_phieu_toa_thuoc')

# ----------------- CẤU HÌNH TIẾNG VIỆT -----------------
# 1. Tên font sẽ sử dụng trong ReportLab
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'

PHIEU_TOA_THUOC_HEADER = 'ĐƠN THUỐC BHYT'
SO_Y_TE = AppConfig.SO_Y_TE
TEN_DON_VI = AppConfig.TEN_DON_VI

# Cấu hình Barcode/QR Code
BARCODE_WIDTH = 100
BARCODE_HEIGHT = 30

try:
    # Font Thường (Regular), Font Đậm (Bold), Font Nghiêng (Italic)
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
    "PhongKham": "Nội tim mạch (P112)",
    "TenBacSi": "Bs. Nguyễn Thị C",
    "NgayTiepNhan": "30/10/2025 07:01:49",
    "NgayKham": "30",
    "ThangKham": "10",
    "NamKham": "2025",

    "MaYTe": "123",
    "HoTen": "TẠ THỊ HẢI",
    "Tuoi": "87",
    "GioiTinh": "Nữ",
    "DiaChi": "8 Đồng Thái, Phường Cầu, Tp Hồ Chí Minh",
    "SDT": "0908637",
    "BHYT": "CT27979318716",
    "DoiTuong": "37 BHYT 100%",

    "ChanDoan": "TĂNG HUYẾT ÁP - RỐI LOẠN LIPID MÁU",
    "Mach": "",
    "HA": "136/62",
    "NhietDo": "",
    "CanNang": "65.00",

    "SoNgayHenTaiKham": "28",
    "NgayHenTaiKham": "27/11/2025",
    "DrNote": "",
    "ToaThuoc": [
        {
            "Stt": "1",
            "TenThuoc": "Lercanidipine hydrochloride",
            "TenThuocPhu": "(Kafedipin), 10mg",
            "DonViTinh": "Viên - Uống ()",
            "Sang": "1",
            "Trua": "0",
            "Chieu": "0",
            "Toi": "0",
            "SoNgay": "28",
            "SoLuong": "28"
        },
    ]
}

# ----------------- 3. HÀM VẼ PHIẾU THUỐC -----------------
def draw_drug_form(c, data, ma_y_te_barcode, thong_tin_qrcode):
    width, height = A5
    margin_left = 30
    drug_line_height = 35

    # ------------------ KHỐI CHUNG ------------------
    c.setFont(VIET_FONT, 9)
    y_start = height - 30

    # Tiêu đề Bệnh viện & PHÒNG KHÁM IN PHIẾU
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left, y_start, SO_Y_TE)
    c.drawString(margin_left, y_start - 10, TEN_DON_VI)
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_start - 20, data.get('PhongKham', ''))

    # try:
    #     x_barcode = width - margin_left - BARCODE_WIDTH
    #     c.drawImage(ma_y_te_barcode, x_barcode, y_start - 10, BARCODE_WIDTH, BARCODE_HEIGHT)
    # except FileNotFoundError:
    #     pass

    try:
        x_barcode = width - margin_left * 2
        c.drawImage(thong_tin_qrcode, x_barcode, y_start - 12, 40, 40)
    except FileNotFoundError:
        pass

    c.setFont(VIET_FONT_BOLD, 10)
    c.drawRightString(width - margin_left, y_start - 20, data.get('MaYTe', ''))
    c.setFont(VIET_FONT, 9)
    c.drawRightString(width - margin_left, y_start - 30, data.get('DoiTuong', ''))

    # Tiêu đề Form
    c.setFont(VIET_FONT_BOLD, 12)
    c.drawCentredString(width / 2, y_start - 40, PHIEU_TOA_THUOC_HEADER)

    # ------------------ THÔNG TIN BỆNH NHÂN ------------------
    y_info = y_start - 60
    line_y_offset = -12

    c.setFont(VIET_FONT, 9)

    # Họ tên
    c.drawString(margin_left, y_info, "Họ tên: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 35, y_info, data.get('HoTen', ''))

    # Tuổi
    c.setFont(VIET_FONT, 9)  # Quay lại font thường
    c.drawString(margin_left + 160, y_info, "Tuổi: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 185, y_info, data.get('Tuoi', ''))

    # Cân nặng
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 230, y_info, "Cân nặng: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 275, y_info, data.get('CanNang', ''))

    # Giới tính
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 320, y_info, "Giới tính: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 355, y_info,  data.get('GioiTinh', ''))

    y_info += line_y_offset
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, f"Mã số thẻ BHYT (nếu có): {data.get('BHYT', '')}")

    y_info += line_y_offset
    c.drawString(margin_left, y_info, f"Địa Chỉ: { data.get('DiaChi', '')}")

    y_info += line_y_offset
    c.drawString(margin_left, y_info, f"Số ĐT: { data.get('SDT', '')}")
    c.drawString(margin_left + 110, y_info, f"Ngày tiếp nhận: { data.get('NgayTiepNhan', '')}")

    y_info += line_y_offset
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, "Chẩn đoán: ")
    c.setFont(VIET_FONT_BOLD, 7.5)
    c.drawString(margin_left + 45, y_info,  data.get('ChanDoan', ''))
    c.setFont(VIET_FONT, 9)

    y_info += line_y_offset  # Tăng khoảng cách
    c.drawString(margin_left, y_info, f"Mạch: { data.get('Mach', '')} lần/p")
    c.drawString(margin_left + 100, y_info, f"HA: { data.get('HA', '')} mmHg")
    c.drawString(margin_left + 210, y_info, f"Nhiệt độ: { data.get('NhietDo', '')} °C")
    c.drawString(width - margin_left - 25, y_info, f"ĐH: ")

    # ------------------ DANH SÁCH THUỐC ------------------

    # ------------------------------------------------------------------
    # 2. Xử lý Vòng lặp Thuốc và Phân Trang
    # ------------------------------------------------------------------

    # Y_BREAK_POINT: Vị trí Y thấp nhất cho phép (chừa khoảng 120pt cho chân trang)
    Y_BREAK_POINT = 30

    # y_drug: Vị trí Y bắt đầu của danh sách thuốc trên trang hiện tại
    y_drug = y_info - 20

    # Biến theo dõi STT dòng (Dùng để reset Y khi chuyển trang)
    y_reset_point = y_drug

    for drug in data.get('ToaThuoc', []):
        # ------------------------------------------------------
        # KIỂM TRA PHÂN TRANG:
        # Nếu dòng thuốc mới sẽ chạm hoặc vượt qua điểm ngắt
        # ------------------------------------------------------
        if y_drug - drug_line_height < Y_BREAK_POINT:
            c.showPage()

            # Reset y_drug về vị trí bắt đầu mới (thường là gần đỉnh trang 2)
            y_drug = height - 50

        # ------------------------------------------------------
        # VẼ DÒNG THUỐC
        # ------------------------------------------------------

        # Dòng 1: Tên thuốc, Đơn vị tính, Tên phụ, SL
        c.setFont(VIET_FONT_BOLD, 9)
        c.drawString(margin_left, y_drug, drug.get('STT', ''))
        c.drawString(margin_left + 10, y_drug, f"{drug.get('TenThuoc', '')}  {drug.get('DonViTinh', '')}")
        c.drawString(margin_left + 230, y_drug, drug.get('TenThuocPhu', ''))

        c.setFont(VIET_FONT, 9)
        c.drawString(width - margin_left - 30, y_drug, f"SL: {drug.get('SoLuong', '')}")
        c.line(width - margin_left - 15, y_drug - 2, width - margin_left, y_drug - 2)

        # Dòng 2: Liều dùng Sáng/Trưa/Chiều/Tối & Số ngày
        y_usage = y_drug - 15

        c.drawString(margin_left + 5, y_usage, f'Sáng: {drug.get('Sang', '')}')
        c.line(margin_left + 30, y_usage - 2, margin_left + 60, y_usage - 2)
        c.drawString(margin_left + 70, y_usage, f'Trưa: {drug.get('Trua', '')}')
        c.line(margin_left + 95, y_usage - 2, margin_left + 125, y_usage - 2)
        c.drawString(margin_left + 135, y_usage, f'Chiều: {drug.get('Chieu', '')}')
        c.line(margin_left + 170, y_usage - 2, margin_left + 200, y_usage - 2)
        c.drawString(margin_left + 210, y_usage, f'Tối: {drug.get('Toi', '')}')
        c.line(margin_left + 230, y_usage - 2, margin_left + 260, y_usage - 2)

        c.setFont(VIET_FONT_BOLD, 7.5)
        c.drawString(margin_left + 270, y_usage, f"Số ngày thuốc: {drug.get('SoNgay', '')}")

        y_drug -= drug_line_height

    # ------------------ LỜI DẶN VÀ CHỮ KÝ (ĐÃ CĂN GIỮA Ở NỬA PHẢI) ------------------
    y_footer = y_drug - 10

    # Tọa độ X căn giữa cho khối chữ ký (Ví dụ: giữa 210 và 390 là 300)
    center_right_x = 300

    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_footer, "Lời dặn của bác sĩ:")

    # Lời dặn cụ thể (Hẹn tái khám) - Giữ căn phải để giống hình ảnh gốc
    note = data.get('DrNote', '')
    c.drawRightString(width - margin_left, y_footer, note)

    # Khối Căn giữa ở Nửa Phải (center_right_x)
    y_center_block = y_footer - 10

    # Ngày tháng
    c.drawCentredString(center_right_x, y_center_block, f'Ngày {data.get('NgayKham','')} '
                                                        f'tháng {data.get('ThangKham','')} '
                                                        f'năm {data.get('NamKham', '')}')

    # Bác sĩ điều trị
    c.drawCentredString(center_right_x, y_center_block - 15, "Bác sĩ điều trị")

    # Tên bác sĩ
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_center_block - 75, data.get('TenBacSi', ''))

# ----------------- 4. HÀM TẠO TÊN FILE -----------------
def create_file_name(data):
    # 1. Tạo tên file
    ma_bhyt = data.get('BHYT', 'NO_BHYT')
    ngay_tiep_nhan = data.get('NgayTiepNhan', 'NO_DATE')

    # Xử lý chuỗi ngày tiếp nhận để loại bỏ ký tự không hợp lệ cho tên file
    # Thay thế '/', ':', ' ' bằng '_'
    safe_date_string = ngay_tiep_nhan.replace('/', '_').replace(':', '_').replace(' ', '__')

    # Tên file PDF
    file_name = f"DonThuoc_{ma_bhyt}_{safe_date_string}.pdf"

    return file_name

# ----------------- 5. HÀM TẠO FILE PDF TOA THUỐC -----------------
def create_and_open_pdf_for_printing(data):
    """Tạo file PDF với tên file là mã BHYT và ngày tiếp nhận, sau đó mở file."""
    try:
        # 1. Tạo thư mục nếu chưa có. exist_ok=True tránh báo lỗi nếu thư mục đã tồn tại
        os.makedirs(TARGET_DIR, exist_ok=True)
        pdf_path = os.path.join(TARGET_DIR, create_file_name(data))

        ma_y_te_barcode = generate_ma_y_te_barcode(ma_y_te=data.get('MaYTe', '00000000'))
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

        # 2. Tạo PDF
        c = canvas.Canvas(pdf_path, pagesize=A5)
        draw_drug_form(c, data, ma_y_te_barcode, thong_tin_qrcode)
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