from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

from app.configs.drug_table_configs import *

TARGET_DIR = '../../data/in_phieu_toa_thuoc'

# ----------------- CẤU HÌNH TIẾNG VIỆT -----------------
# 1. Tên font sẽ sử dụng trong ReportLab
VIET_FONT = 'TimesNewRomanVN'
VIET_FONT_BOLD = 'TimesNewRomanVNBold'
VIET_FONT_ITALIC = 'TimesNewRomanVNItalic'

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
    'so_y_te': 'SỞ Y TẾ TP.HCM',
    'ten_benh_vien': 'BỆNH VIỆN ABC',
    'phong_kham': 'Nội tim mạch (P112)',
    'doi_tuong': '37 BHYT 100%',
    'ho_ten': 'TẠ THỊ HẢI',
    'tuoi': '87',
    'can_nang': '65.00',
    'gioi_tinh': 'Nữ',
    'ma_bhyt': 'CT27979318716',
    'dia_chi': '8 Đồng Thái, Phường Cầu, Tp Hồ Chí Minh',
    'sdt': '0908637',
    'ngay_tiep_nhan': '30/10/2025 07:01:49',
    'ngay_kham': '30',
    'thang_kham': '10',
    'nam_kham': '2025',
    'chan_doan': 'TĂNG HUYẾT ÁP - RỐI LOẠN LIPID MÁU',
    'mach': '',
    'HA': '136/62',
    'nhiet_do': '',
    'so_ngay_hen_tai_kham': '28',
    'ngay_hen_tai_kham': '27/11/2025',
    'ten_bac_si': 'Bs. Nguyễn Thị C',
    'dr_note': '',
    'ds_thuoc': [
        {'stt': '1', 'ten_thuoc': 'Lercanidipine hydrochloride', 'ten_thuoc_phu': '(Kafedipin), 10mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'},
        {'stt': '2', 'ten_thuoc': 'Telmisartan', 'ten_thuoc_phu': '(Zhekof), 40mg', 'don_vi_tinh': 'Viên - Uống ()',
         'sang': '2', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28', 'so_luong': '56'},
        {'stt': '3', 'ten_thuoc': 'Atorvastatin', 'ten_thuoc_phu': '(Insuact), 20mg', 'don_vi_tinh': 'Viên - Uống ()',
         'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28', 'so_luong': '28'},
        {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'},
        {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'}, {'stt': '4', 'ten_thuoc': 'Bisoprolol fumarate', 'ten_thuoc_phu': '(SaviProlol), 2,5mg',
         'don_vi_tinh': 'Viên - Uống ()', 'sang': '1', 'trua': '0', 'chieu': '0', 'toi': '0', 'so_ngay': '28',
         'so_luong': '28'},
    ]
}

# ----------------- 3. HÀM VẼ PHIẾU THUỐC -----------------
def draw_drug_form(c, data):
    width, height = A5
    margin_left = 30
    drug_line_height = 35

    # ------------------ KHỐI CHUNG ------------------
    c.setFont(VIET_FONT, 9)
    y_start = height - 30

    # Tiêu đề Bệnh viện & PHÒNG KHÁM IN PHIẾU
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left, y_start, SO_Y_TE)
    c.drawString(margin_left, y_start - 10, TEN_BENH_VIEN)
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_start - 20, data["phong_kham"])

    c.setFont(VIET_FONT_BOLD, 10)
    c.drawRightString(width - margin_left, y_start, 'MÃ Y TẾ')
    c.setFont(VIET_FONT, 9)
    c.drawRightString(width - margin_left, y_start - 10, data["doi_tuong"])

    # Tiêu đề Form
    c.setFont(VIET_FONT_BOLD, 12)
    c.drawCentredString(width / 2, y_start - 40, PHIEU_TOA_THUOC_HEADER)

    # ------------------ THÔNG TIN BỆNH NHÂN ------------------
    y_info = y_start - 60
    line_y_offset = -12

    c.setFont(VIET_FONT, 9)

    # Họ tên
    c.drawString(margin_left, y_info, "Họ tên: ")
    c.setFont(VIET_FONT_BOLD, 9)  # Tạm thời chuyển sang BOLD
    c.drawString(margin_left + 35, y_info, data['ho_ten'])

    # Tuổi
    c.setFont(VIET_FONT, 9)  # Quay lại font thường
    c.drawString(margin_left + 160, y_info, "Tuổi: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 185, y_info, data['tuoi'])

    # Cân nặng
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 230, y_info, "Cân nặng: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 275, y_info, data['can_nang'])

    # Giới tính
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left + 320, y_info, "Giới tính: ")
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawString(margin_left + 355, y_info, data['gioi_tinh'])

    y_info += line_y_offset
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, f"Mã số thẻ BHYT (nếu có): {data['ma_bhyt']}")

    y_info += line_y_offset
    c.drawString(margin_left, y_info, f"Địa Chỉ: {data['dia_chi']}")

    y_info += line_y_offset
    c.drawString(margin_left, y_info, f"Số ĐT: {data['sdt']}")
    c.drawString(margin_left + 110, y_info, f"Ngày tiếp nhận: {data['ngay_tiep_nhan']}")

    y_info += line_y_offset
    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_info, "Chẩn đoán: ")
    c.setFont(VIET_FONT_BOLD, 7.5)
    c.drawString(margin_left + 45, y_info, data['chan_doan'])
    c.setFont(VIET_FONT, 9)

    y_info += line_y_offset  # Tăng khoảng cách
    c.drawString(margin_left, y_info, f"Mạch: {data['mach']} lần/p")
    c.drawString(margin_left + 100, y_info, f"HA: {data['HA']} mmHg")
    c.drawString(margin_left + 210, y_info, f"Nhiệt độ: {data['nhiet_do']} °C")
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

    for drug in data["ds_thuoc"]:
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
        c.drawString(margin_left, y_drug, drug["stt"])
        c.drawString(margin_left + 10, y_drug, f"{drug['ten_thuoc']}  {drug['don_vi_tinh']}")
        c.drawString(margin_left + 230, y_drug, drug["ten_thuoc_phu"])

        c.setFont(VIET_FONT, 9)
        c.drawString(width - margin_left - 30, y_drug, f"SL: {drug['so_luong']}")
        c.line(width - margin_left - 15, y_drug - 2, width - margin_left, y_drug - 2)

        # Dòng 2: Liều dùng Sáng/Trưa/Chiều/Tối & Số ngày
        y_usage = y_drug - 15

        c.drawString(margin_left + 5, y_usage, f'Sáng: {drug['sang']}')
        c.line(margin_left + 30, y_usage - 2, margin_left + 60, y_usage - 2)
        c.drawString(margin_left + 70, y_usage, f'Trưa: {drug['trua']}')
        c.line(margin_left + 95, y_usage - 2, margin_left + 125, y_usage - 2)
        c.drawString(margin_left + 135, y_usage, f'Chiều: {drug['chieu']}')
        c.line(margin_left + 170, y_usage - 2, margin_left + 200, y_usage - 2)
        c.drawString(margin_left + 210, y_usage, f'Tối: {drug['toi']}')
        c.line(margin_left + 230, y_usage - 2, margin_left + 260, y_usage - 2)

        c.setFont(VIET_FONT_BOLD, 7.5)
        c.drawString(margin_left + 270, y_usage, f"Số ngày thuốc: {drug['so_ngay']}")

        y_drug -= drug_line_height

    # ------------------ LỜI DẶN VÀ CHỮ KÝ (ĐÃ CĂN GIỮA Ở NỬA PHẢI) ------------------
    y_footer = y_drug - 10

    # Tọa độ X căn giữa cho khối chữ ký (Ví dụ: giữa 210 và 390 là 300)
    center_right_x = 300

    c.setFont(VIET_FONT, 9)
    c.drawString(margin_left, y_footer, "Lời dặn của bác sĩ:")

    # Lời dặn cụ thể (Hẹn tái khám) - Giữ căn phải để giống hình ảnh gốc
    note = f"{data['dr_note']}"
    c.drawRightString(width - margin_left, y_footer, note)

    # Khối Căn giữa ở Nửa Phải (center_right_x)
    y_center_block = y_footer - 10

    # Ngày tháng
    c.drawCentredString(center_right_x, y_center_block, f'Ngày {data['ngay_kham']} tháng {data['thang_kham']} năm {data['nam_kham']}')

    # Bác sĩ điều trị
    c.drawCentredString(center_right_x, y_center_block - 15, "Bác sĩ điều trị")

    # Tên bác sĩ
    c.setFont(VIET_FONT_BOLD, 9)
    c.drawCentredString(center_right_x, y_center_block - 75, data["ten_bac_si"])

# ----------------- 4. HÀM TẠO TÊN FILE -----------------
def create_file_name(data):
    # 1. Tạo tên file
    ma_bhyt = data.get('ma_bhyt', 'NO_BHYT')
    ngay_tiep_nhan = data.get('ngay_tiep_nhan', 'NO_DATE')

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

        # 2. Tạo PDF
        c = canvas.Canvas(pdf_path, pagesize=A5)
        draw_drug_form(c, data)
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