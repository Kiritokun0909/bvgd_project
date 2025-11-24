from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QLocale, QDate, Qt
from PyQt6.QtGui import QDoubleValidator
import sys

from PyQt6.QtWidgets import QMessageBox

# Giả định các import service của bạn vẫn giữ nguyên
from app.core.in_hoa_don import create_and_open_pdf_for_printing
from app.services.BenhNhanService import get_benh_nhan_by_id
from app.services.DoiTuongService import get_list_doi_tuong
from app.styles.styles import TUOI_STYLE, TAI_VU_STYLE, ADD_BTN_STYLE, COMPLETER_THUOC_STYLE
from app.ui.TabTaiVu import Ui_formTaiVu
from app.utils.chuyen_tien_thanh_chu import chuyen_tien_thanh_chu
from app.utils.config_manager import ConfigManager
from app.utils.utils import format_currency_vn, unformat_currency_to_float, calculate_age, populate_list_to_combobox

MAX_DOUBLE_VALUE = sys.float_info.max


class TaiVuTabController(QtWidgets.QWidget):
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.bhyt = None

        # <editor-fold desc="Init UI">
        self.ui_tai_vu = Ui_formTaiVu()
        self.ui_tai_vu.setupUi(tab_widget_container)
        # </editor-fold>

        doi_tuong_data = get_list_doi_tuong()
        populate_list_to_combobox(self.ui_tai_vu.cb_doi_tuong,
                                  data=doi_tuong_data,
                                  display_col=2,  # TenDoiTuong
                                  key_col=0)  # DoiTuong_Id

        self.reset_all()
        self.setup_dong_ho()
        self.setup_validator()

        self.config_manager = ConfigManager()
        self.load_saved_settings()

        self.connect_signals()
        self.set_stylesheet()

    # <editor-fold desc="Set stylesheet">
    def set_stylesheet(self):
        ui = self.ui_tai_vu
        ui.ho_ten.setStyleSheet(TAI_VU_STYLE)
        ui.tuoi.setStyleSheet(TAI_VU_STYLE)
        ui.cb_doi_tuong.setStyleSheet(COMPLETER_THUOC_STYLE)
        ui.cb_hinh_thuc_tt.setStyleSheet(COMPLETER_THUOC_STYLE)
        ui.dia_chi.setStyleSheet(TAI_VU_STYLE)
        ui.so_tien_text.setStyleSheet(TUOI_STYLE)
        ui.thanh_chu_text.setStyleSheet("font-size: 12px;")

        ui.btn_in_hoa_don.setStyleSheet(ADD_BTN_STYLE)
        ui.btn_reset_all.setStyleSheet(ADD_BTN_STYLE)

    # </editor-fold>

    # <editor-fold desc="Save & load setting">
    def save_settings(self):
        nguoi_tao = self.ui_tai_vu.ho_ten_nguoi_tao.text()
        nguoi_thu = self.ui_tai_vu.ho_ten_nguoi_thu.text()
        self.config_manager.save_last_tai_vu_selection(nguoi_tao, nguoi_thu)

    def load_saved_settings(self):
        ten_nguoi_tao, ten_nguoi_thu = self.config_manager.load_last_tai_vu_selection()
        if ten_nguoi_tao:
            self.ui_tai_vu.ho_ten_nguoi_tao.setText(ten_nguoi_tao)
        if ten_nguoi_thu:
            self.ui_tai_vu.ho_ten_nguoi_thu.setText(ten_nguoi_thu)

    # </editor-fold>

    # <editor-fold desc="Setup validator">
    def setup_validator(self):
        validator = QDoubleValidator(0.00, MAX_DOUBLE_VALUE, 3, self)
        us_locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
        validator.setLocale(us_locale)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.ui_tai_vu.tong_so_tien.setValidator(validator)

    # </editor-fold>

    # <editor-fold desc="Setup đồng hồ">
    def setup_dong_ho(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_datetime_edit)
        self.timer.start(1000)
        self.update_datetime_edit()

    def update_datetime_edit(self):
        self.ui_tai_vu.ngay_tao.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui_tai_vu.ngay_thu.setDateTime(QtCore.QDateTime.currentDateTime())

    # </editor-fold>

    # <editor-fold desc="Connect Signals">
    def connect_signals(self):
        ui = self.ui_tai_vu

        ui.ho_ten_nguoi_tao.textEdited.connect(self.save_settings)
        ui.ho_ten_nguoi_thu.textEdited.connect(self.save_settings)

        ui.tong_so_tien.textEdited.connect(self.format_tong_so_tien)
        ui.btn_in_hoa_don.clicked.connect(self.handle_in_hoa_don)
        ui.btn_reset_all.clicked.connect(self.reset_all)

        # --- THAY ĐỔI QUAN TRỌNG CHO MÁY QUÉT ---
        # Không dùng textEdited cho ma_y_te nữa vì máy quét gõ rất nhanh sẽ gây lag
        # Dùng returnPressed: Sự kiện khi nhấn Enter (Máy quét thường tự gửi Enter cuối cùng)
        ui.ma_y_te.returnPressed.connect(self.handle_scan_or_enter)

    # </editor-fold>

    # <editor-fold desc="Xử lý nhập liệu (Máy quét & Nhập tay)">
    def handle_scan_or_enter(self):
        """
        Hàm này xử lý 2 trường hợp:
        1. Máy quét bắn vào chuỗi dài (có chứa ký tự đặc biệt hoặc dấu phân cách).
        2. Người dùng nhập tay Mã Y Tế ngắn và nhấn Enter.
        """
        input_text = self.ui_tai_vu.ma_y_te.text().strip()

        if not input_text:
            return

        # Kiểm tra xem đây là chuỗi QR đầy đủ hay chỉ là Mã Y Tế nhập tay
        # Dấu hiệu nhận biết: Chuỗi QR của bạn có chứa dấu '|' hoặc dài hơn mã y tế chuẩn
        if "|" in input_text or ":" in input_text:
            # Trường hợp 1: Dữ liệu từ máy quét QR
            self.process_qr_data(input_text)
        else:
            # Trường hợp 2: Nhập tay Mã Y Tế (ví dụ: BN0001)
            self.load_thong_tin_benh_nhan(input_text)

    def process_qr_data(self, data: str):
        """
        Phân tích chuỗi dữ liệu từ máy quét và điền vào form.
        Format: 'MaYTe:BN0002|BHYT:...|DTuong:...|Ten:...|...'
        """
        ui = self.ui_tai_vu
        data_parts = {}

        try:
            # Tách chuỗi bằng dấu '|'
            pairs = data.split('|')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    data_parts[key.strip()] = value.strip()

            # --- Điền dữ liệu ---
            # Lưu ý: Sau khi parse xong, ta chỉ để lại Mã Y Tế ngắn gọn trên ô input
            extracted_ma_y_te = data_parts.get('MaYTe', '')
            ui.ma_y_te.setText(extracted_ma_y_te)

            ui.ho_ten.setText(data_parts.get('Ten', ''))
            ui.dia_chi.setText(data_parts.get('DC', ''))
            ui.tuoi.setText(data_parts.get('Tuoi', ''))
            self.bhyt = data_parts.get('BHYT', '')

            ma_dt = data_parts.get('MaDT', '')
            index = ui.cb_doi_tuong.findData(ma_dt)
            if index != -1:
                ui.cb_doi_tuong.setCurrentIndex(index)

            # Xử lý tiền
            tong_tien_raw = data_parts.get('Tien', '')
            if tong_tien_raw:
                tong_tien_input = (tong_tien_raw.replace(' VND', '')
                                   .replace('.', '')
                                   .replace(',', '.'))
                ui.tong_so_tien.setText(tong_tien_input)
                self.format_tong_so_tien()

            # (Tùy chọn) Sau khi quét xong, chuyển focus sang nút in hoặc ô tiền
            ui.tong_so_tien.setFocus()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi Dữ Liệu", f"QR không đúng định dạng: {e}")
            self.reset_all()

    def load_thong_tin_benh_nhan(self, ma_y_te: str):
        """Load dữ liệu từ Database khi nhập tay ID"""
        benh_nhan_data = get_benh_nhan_by_id(ma_y_te)
        if benh_nhan_data is None:
            QMessageBox.warning(self, "Không tìm thấy", f"Không tìm thấy bệnh nhân: {ma_y_te}")
            return

        # print(benh_nhan_data)
        self.set_thong_tin_benh_nhan(benh_nhan_data)

    def set_thong_tin_benh_nhan(self, benh_nhan_data: tuple):
        ui = self.ui_tai_vu
        ma_y_te = str(benh_nhan_data[0]).upper()
        ho_ten = benh_nhan_data[1]
        nam_sinh = benh_nhan_data[3]
        dia_chi = benh_nhan_data[5]
        ngay_sinh = QDate(int(nam_sinh), 1, 1) if nam_sinh is not None else QDate.currentDate()
        tuoi = str(calculate_age(ngay_sinh.toString('dd/MM/yyyy'))) if nam_sinh is not None else '0'

        ui.ma_y_te.setText(ma_y_te)
        ui.ho_ten.setText(ho_ten)
        ui.dia_chi.setText(dia_chi)
        ui.tuoi.setText(tuoi)
        ui.tuoi.setStyleSheet(TUOI_STYLE)

    # </editor-fold>

    # <editor-fold desc="Format tổng số tiền">
    def format_tong_so_tien(self):
        so_tien_input = self.ui_tai_vu.tong_so_tien.text()
        so_tien_input = so_tien_input.replace(',', '')

        if not so_tien_input:
            self.ui_tai_vu.so_tien_text.setText('<Số tiền>')
            self.ui_tai_vu.thanh_chu_text.setText('<Thành chữ>')
            return

        formatted_so_tien = format_currency_vn(so_tien_input)
        thanh_chu = chuyen_tien_thanh_chu(unformat_currency_to_float(formatted_so_tien))

        self.ui_tai_vu.tong_so_tien.setText(so_tien_input)
        self.ui_tai_vu.so_tien_text.setText(formatted_so_tien + ' VNĐ')
        self.ui_tai_vu.thanh_chu_text.setText(thanh_chu)

    # </editor-fold>

    # <editor-fold desc="Handle in hoá đơn">
    def get_thong_tin(self) -> dict:
        ui = self.ui_tai_vu
        data = dict()
        data['MaYTe'] = ui.ma_y_te.text()
        data['BHYT'] = str(self.bhyt)
        data['HoTen'] = ui.ho_ten.text()
        data['DiaChi'] = ui.dia_chi.toPlainText()
        data['TongTienThanhToan'] = ui.so_tien_text.text()
        data['SoTienBangChu'] = ui.thanh_chu_text.text()
        data['HinhThucThanhToan'] = ui.cb_hinh_thuc_tt.currentText()
        data['NguoiThuTien'] = ui.ho_ten_nguoi_thu.text().strip()
        return data

    def check_required_data(self, data: dict) -> bool:
        required_fields = {
            # 'MaYTe': 'Mã Y Tế',
            'HoTen': 'Họ Tên',
            'TongTienThanhToan': 'Tổng Tiền Thanh Toán',
        }
        for key, display_name in required_fields.items():
            value = data.get(key)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return False
        return True

    def handle_in_hoa_don(self):
        data = self.get_thong_tin()
        if not self.check_required_data(data):
            QMessageBox.warning(self, 'Cảnh báo', 'Chưa có đủ thông tin in phiếu hoá đơn!')
            return

        create_and_open_pdf_for_printing(data)

        # reply = QMessageBox.question(self, "Xác nhận", "Reset màn hình?",
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        # if reply == QMessageBox.StandardButton.Yes:
        #     self.reset_all()

    # </editor-fold>

    # <editor-fold desc="Reset all">
    def reset_all(self):
        ui = self.ui_tai_vu
        ui.ma_y_te.clear()
        ui.ho_ten.clear()
        ui.dia_chi.clear()
        ui.tuoi.clear()
        ui.cb_doi_tuong.setCurrentIndex(0)
        ui.tong_so_tien.clear()
        ui.so_tien_text.setText("<Số tiền>")
        ui.thanh_chu_text.setText("<Thành chữ>")

        # QUAN TRỌNG: Set focus vào ô Mã Y Tế để sẵn sàng quét ngay sau khi reset
        ui.ma_y_te.setFocus()
    # </editor-fold>