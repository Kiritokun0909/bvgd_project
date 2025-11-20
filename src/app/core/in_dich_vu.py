import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from app.utils.create_barcode import generate_ma_y_te_barcode, generate_so_tien_barcode
from app.utils.create_qr_code import generate_medical_qr_code
from app.utils.get_file_path import get_file_path
from app.utils.setting_loader import AppConfig
from app.core.pdf_common import register_vietnamese_fonts, open_pdf_file, sanitize_filename, get_paragraph_style

# Config Constants
TARGET_DIR = get_file_path('data/in_phieu_chi_dinh')
FONT_REG, FONT_BOLD, FONT_ITALIC = register_vietnamese_fonts()


class PhieuChiDinhPrinter:
    def __init__(self, data, group_index):
        self.data = data
        self.group_index = group_index
        self.nhom_dv = data['DichVu'][group_index]

        self.width, self.height = A5
        self.margin_left = 15

        # Assets
        self.barcode_bn = generate_ma_y_te_barcode(data.get('MaYTe', ''))
        self.barcode_tien = generate_so_tien_barcode(data.get('TongBenhNhanTra', '0'))
        self.qr_code = self._create_qr()

        # Layout config
        self.col_widths = [10 * mm, 200, 40, 130]
        self.min_footer_space = 100

    def _create_qr(self):
        return generate_medical_qr_code(
            ma_y_te=self.data.get('MaYTe', ''),
            so_bhyt=self.data.get('MaBHYT', ''),
            doi_tuong=self.data.get('DoiTuong', ''),
            ho_ten=self.data.get('HoTen', ''),
            tuoi=self.data.get('Tuoi', ''),
            gioi_tinh=self.data.get('GioiTinh', ''),
            dia_chi=self.data.get('DiaChi', ''),
            so_dien_thoai=self.data.get('SDT', ''),
            so_tien=self.data.get('TongBenhNhanTra', '')
        )

    def draw_header(self, c, y_start):
        """Vẽ thông tin hành chính"""
        d = self.data
        # Bệnh viện
        c.setFont(FONT_BOLD, 9)
        c.drawString(self.margin_left, y_start, AppConfig.TEN_DON_VI)
        c.setFont(FONT_REG, 9)
        c.drawString(self.margin_left, y_start - 10, d.get("PhongKham", ""))

        # Barcode & QR
        try:
            c.drawImage(self.barcode_bn, self.width - self.margin_left - 100, y_start - 10, 100, 30)
            c.drawImage(self.qr_code, self.width - self.margin_left - 70, y_start - 165, 45, 45)
        except:
            pass

        # Thông tin Mã
        c.setFont(FONT_BOLD, 10)
        c.drawRightString(self.width - self.margin_left, y_start - 20, f'Mã y tế: {d.get("MaYTe", "")}')
        c.setFont(FONT_REG, 9)
        c.drawRightString(self.width - self.margin_left, y_start - 35, f'Số BHYT: {d.get("MaBHYT", "")}')
        c.setFont(FONT_BOLD, 10)
        c.drawRightString(self.width - self.margin_left, y_start - 50, f'Đối tượng: {d.get("DoiTuong", "")}')

        # Tiêu đề
        c.setFont(FONT_BOLD, 12)
        c.drawCentredString(self.width / 2, y_start - 65, 'PHIẾU CHỈ ĐỊNH')

        # Thông tin bệnh nhân
        y_info = y_start - 90
        c.setFont(FONT_REG, 9)
        c.drawString(self.margin_left, y_info, "Họ tên: ")
        c.setFont(FONT_BOLD, 9)
        c.drawString(self.margin_left + 35, y_info, d.get('HoTen', ''))
        c.setFont(FONT_REG, 9)
        c.drawRightString(self.width - self.margin_left, y_info, f"Tuổi: {d.get('Tuoi')} - Giới tính: {d.get('GioiTinh')}")

        y_info -= 16
        c.drawString(self.margin_left, y_info, f"Địa chỉ: {d.get('DiaChi')}")
        c.drawRightString(self.width - self.margin_left, y_info, f"SĐT: {d.get('SDT')}")

        y_info -= 16
        c.drawString(self.margin_left, y_info, f"Chẩn đoán: {d.get('ChanDoan')}")

        y_info -= 16
        c.setFont(FONT_REG, 8)
        c.drawString(self.margin_left, y_info, f"Ghi chú: {d.get('GhiChu')}")

        y_info -= 16
        c.setFont(FONT_REG, 9)
        c.drawString(self.margin_left, y_info, f"Tổng tiền: {d.get('SoTien')} VNĐ")

        return y_info - 20

    def draw_table(self, c, y_start, rows):
        """Vẽ bảng dịch vụ"""
        style_body = get_paragraph_style(FONT_REG, 9)
        data_table = [['STT', 'Tên dịch vụ', 'SL', 'Nơi TH']]  # Header

        row_heights = [20]  # Header height

        for item in rows:
            p = Paragraph(item['TenDichVu'], style_body)
            # Tính chiều cao dòng
            w, h = p.wrap(self.col_widths[1] - 8, 1000)  # trừ padding
            data_table.append([item['STT'], p, item['SoLuong'], item['NoiThucHien']])
            row_heights.append(max(h + 8, 20))

        t = Table(data_table, colWidths=self.col_widths, rowHeights=row_heights)
        t.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        w, h = t.wrapOn(c, 0, 0)
        t.drawOn(c, self.margin_left, y_start - h)
        return y_start - h, h

    def create_pdf(self):
        os.makedirs(TARGET_DIR, exist_ok=True)
        file_name = f"PhieuChiDinh_{self.data.get('MaYTe')}_{sanitize_filename(self.data.get('NgayTao'))}_{self.nhom_dv['MaNhomDichVu']}.pdf"
        pdf_path = os.path.join(TARGET_DIR, file_name)

        c = canvas.Canvas(pdf_path, pagesize=A5)

        # Phân trang
        ds_dich_vu = self.nhom_dv['DSDichVu'][:]  # Copy list

        while True:
            y_curr = self.draw_header(c, self.height - 30)

            # Vẽ tên nhóm
            c.setFont(FONT_BOLD, 10)
            c.drawString(self.margin_left, y_curr, self.nhom_dv['TenNhomDichVu'])
            y_curr -= 15

            # Tính toán số dòng vừa trang này
            available_height = y_curr - self.min_footer_space
            rows_page = []
            current_h = 20  # Header table height

            # Logic lấy dòng đơn giản hóa (có thể thay bằng wrapOn chính xác hơn nếu cần)
            style_test = get_paragraph_style(FONT_REG, 9)
            while ds_dich_vu:
                dv = ds_dich_vu[0]
                p = Paragraph(dv['TenDichVu'], style_test)
                _, h = p.wrap(self.col_widths[1] - 8, 1000)
                row_h = max(h + 8, 20)

                if current_h + row_h > available_height:
                    break

                rows_page.append(ds_dich_vu.pop(0))
                current_h += row_h

            # Vẽ bảng
            y_end_table, _ = self.draw_table(c, y_curr, rows_page)
            
            # Nếu hết dịch vụ -> Vẽ footer
            self.draw_footer(c, y_end_table)
            if not ds_dich_vu:

                c.showPage()
                break
            else:
                c.showPage()  # Sang trang mới và lặp lại

        c.save()
        print(f"Đã tạo: {pdf_path}")
        return pdf_path

    def draw_footer(self, c, y_start):
        y = y_start - 15
        c.setFont(FONT_REG, 9)
        c.drawString(self.margin_left, y, f"Bệnh nhân thanh toán: {self.data.get('TongBenhNhanTra')} VNĐ")

        center_right = self.width - 70
        c.drawCentredString(center_right, y, f"Ngày {self.data.get('NgayTao')}")
        c.setFont(FONT_BOLD, 9)
        c.drawCentredString(center_right, y - 15, "Bác sĩ chỉ định")
        c.drawCentredString(center_right, y - 50, self.data.get("BacSi", ""))


def create_and_open_pdf_for_printing(data):
    for i in range(len(data.get('DichVu', []))):
        printer = PhieuChiDinhPrinter(data, i)
        pdf_path = printer.create_pdf()
        open_pdf_file(pdf_path)


if __name__ == "__main__":
    # Import fake_data from original file or define here
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
    create_and_open_pdf_for_printing(fake_data)
    pass