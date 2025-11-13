import cv2
from PyQt6.QtGui import QImage, QPixmap

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QLocale, QDate
from PyQt6.QtGui import QDoubleValidator
import sys

from PyQt6.QtWidgets import QMessageBox

from app.configs.table_thuoc_configs import ExcelBenhNhan, BENH_NHAN_FILE_PATH, DOI_TUONG_FILE_PATH
from app.core.in_hoa_don import create_and_open_pdf_for_printing
from app.styles.styles import TUOI_STYLE, TAI_VU_STYLE, ADD_BTN_STYLE
from app.ui.TabTaiVu import Ui_formTaiVu
from app.utils.chuyen_tien_thanh_chu import chuyen_tien_thanh_chu

from app.utils.config_manager import ConfigManager
from app.utils.constants import MA_Y_TE_LENGTH
from app.utils.utils import format_currency_vn, unformat_currency_to_float, calculate_age, load_data_from_csv, \
    filter_data_by_foreign_key, get_first_row_data

MAX_DOUBLE_VALUE = sys.float_info.max


class TaiVuTabController(QtWidgets.QWidget):
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.doi_tuong_df = load_data_from_csv(DOI_TUONG_FILE_PATH)
        self.bhyt = None

        # <editor-fold desc="Init UI">
        self.ui_tai_vu = Ui_formTaiVu()
        self.ui_tai_vu.setupUi(tab_widget_container)
        # </editor-fold>

        self.reset_all()
        self.setup_dong_ho()
        self.setup_validator()
        self.init_camera()

        self.config_manager = ConfigManager()
        self.load_saved_settings()

        self.connect_signals()
        self.set_stylesheet()


    # <editor-fold desc="Set stylesheet">
    def set_stylesheet(self):
        ui = self.ui_tai_vu
        ui.ho_ten.setStyleSheet(TAI_VU_STYLE)
        ui.tuoi.setStyleSheet(TAI_VU_STYLE)
        ui.doi_tuong.setStyleSheet(TAI_VU_STYLE)
        ui.dia_chi.setStyleSheet(TAI_VU_STYLE)
        ui.so_tien_text.setStyleSheet(TUOI_STYLE)
        ui.thanh_chu_text.setStyleSheet("font-size: 16px;")

        ui.btn_in_hoa_don.setStyleSheet(ADD_BTN_STYLE)
        ui.btn_reset_all.setStyleSheet(ADD_BTN_STYLE)
        ui.btn_in_hoa_don.setStyleSheet(ADD_BTN_STYLE)
    # </editor-fold>


    # <editor-fold desc="Save & load setting người tạo và ngươời thu cũ của tài vụ">
    def save_settings(self):
        """Lưu tên người tạo và tên người thu hiện tại vào QSettings."""
        nguoi_tao = self.ui_tai_vu.ho_ten_nguoi_tao.text()
        nguoi_thu = self.ui_tai_vu.ho_ten_nguoi_thu.text()
        self.config_manager.save_last_tai_vu_selection(nguoi_tao, nguoi_thu)

    def load_saved_settings(self):
        """Tải giá trị đã lưu và áp dụng chúng cho các widget."""
        ten_nguoi_tao, ten_nguoi_thu = self.config_manager.load_last_tai_vu_selection()

        if ten_nguoi_tao:
            self.ui_tai_vu.ho_ten_nguoi_tao.setText(ten_nguoi_tao)

        if ten_nguoi_thu:
            self.ui_tai_vu.ho_ten_nguoi_thu.setText(ten_nguoi_thu)
    # </editor-fold>

    # <editor-fold desc="Setup validator cho field nhập số tiền">
    def setup_validator(self):
        validator = QDoubleValidator(0.00, MAX_DOUBLE_VALUE, 3, self)
        # -----------------------------------------------------------------
        # BƯỚC QUAN TRỌNG: Ép buộc Locale thành US (sử dụng dấu chấm)
        # -----------------------------------------------------------------

        # 1. Tạo Locale US/English
        # QLocale.Language.English và QLocale.Country.UnitedStates
        us_locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)

        # 2. Gán Locale này cho validator
        validator.setLocale(us_locale)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.ui_tai_vu.tong_so_tien.setValidator(validator)
    # </editor-fold>

    # <editor-fold desc="Setup đồng hồ ngày tạo, ngày thu">
    def setup_dong_ho(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_datetime_edit)
        self.timer.start(1000)
        self.update_datetime_edit()

    def update_datetime_edit(self):
        self.ui_tai_vu.ngay_tao.setDateTime(QtCore.QDateTime.currentDateTime())
        self.ui_tai_vu.ngay_thu.setDateTime(QtCore.QDateTime.currentDateTime())

    # </editor-fold>

    # <editor-fold desc="Xử lý các sự kiện của nút hoặc nhập liệu">
    def connect_signals(self):
        ui = self.ui_tai_vu

        ui.ho_ten_nguoi_tao.textEdited.connect(self.save_settings)
        ui.ho_ten_nguoi_thu.textEdited.connect(self.save_settings)

        ui.tong_so_tien.textEdited.connect(self.format_tong_so_tien)

        ui.btn_in_hoa_don.clicked.connect(self.handle_in_hoa_don)
        ui.btn_reset_all.clicked.connect(self.reset_all)

        ui.btn_camera.clicked.connect(self.toggle_camera)
        ui.ma_y_te.textEdited.connect(self.load_thong_tin_benh_nhan)

    # </editor-fold>

    # <editor-fold desc="Load thông tin bệnh nhân">
    def set_thong_tin_benh_nhan(self, patient_data: dict):
        ui = self.ui_tai_vu

        ma_y_te = str(patient_data.get(ExcelBenhNhan.COL_MA_Y_TE, '')).upper()
        ui.ma_y_te.setText(ma_y_te)
        ui.ho_ten.setText(str(patient_data.get(ExcelBenhNhan.COL_HO_TEN, '')))
        ui.dia_chi.setText(str(patient_data.get(ExcelBenhNhan.COL_DIA_CHI, '')))

        date_format = "dd/MM/yyyy"
        ngay_sinh = QtCore.QDate.fromString(str(patient_data.get(ExcelBenhNhan.COL_NGAY_SINH, '')), date_format)

        ui.tuoi.setText(str(calculate_age(ngay_sinh.toString('dd/MM/yyyy'))))
        ui.tuoi.setStyleSheet(TUOI_STYLE)

        ma_doi_tuong = str(patient_data.get(ExcelBenhNhan.COL_MA_DOI_TUONG, ''))
        filtered_df = filter_data_by_foreign_key(
            data_frame=self.doi_tuong_df,
            fk_key_value=ma_doi_tuong,
            fk_column_name='MaDT'
        )

        doi_tuong_data = get_first_row_data(filtered_df)
        ui.doi_tuong.setText(doi_tuong_data.get('TenDT', ''))

        so_bhyt = str(patient_data.get(ExcelBenhNhan.COL_SO_BHYT, ''))
        if so_bhyt == 'nan':
            so_bhyt = 'Không'
        self.bhyt = so_bhyt

    def load_thong_tin_benh_nhan(self, ma_y_te: str):
        """Lọc dữ liệu bệnh nhân và cập nhật giao diện."""
        if len(ma_y_te) != MA_Y_TE_LENGTH:
            return

        try:
            benh_nhan_df = load_data_from_csv(BENH_NHAN_FILE_PATH)
            filtered_df = filter_data_by_foreign_key(
                data_frame=benh_nhan_df,
                fk_key_value=ma_y_te,
                fk_column_name='MaYTe'
            )

            if len(filtered_df) < 1:
                print(f'Không tìm thấy bênh nhân với mã {ma_y_te}')
                return

            patient_data = get_first_row_data(filtered_df)
            self.set_thong_tin_benh_nhan(patient_data)
        except Exception as e:
            print(f"Lỗi xảy ra trong quá trình cập nhật thông tin bệnh nhân: {e}")
    # </editor-fold>

    # <editor-fold desc="Format tổng số tiền"
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
        data['DiaChi'] = ui.dia_chi.text()
        data['TongTienThanhToan'] = ui.so_tien_text.text()
        data['SoTienBangChu'] = ui.thanh_chu_text.text()
        data['HinhThucThanhToan'] = ui.cb_hinh_thuc_tt.currentText()

        return data

    def check_required_data(self, data: dict) -> bool:
        required_fields = {
            'MaYTe': 'Mã Y Tế',
            'BHYT': 'Bảo Hiểm Y Tế',
            'HoTen': 'Họ Tên',
            'DiaChi': 'Địa Chỉ',
            'TongTienThanhToan': 'Tổng Tiền Thanh Toán',
            'SoTienBangChu': 'Số Tiền Bằng Chữ',
            'HinhThucThanhToan': 'Hình Thức Thanh Toán',
        }

        # Lặp qua các trường bắt buộc
        for key, display_name in required_fields.items():
            value = data.get(key)

            # Kiểm tra nếu giá trị là None (không có key) hoặc là chuỗi rỗng sau khi loại bỏ khoảng trắng
            if value is None or (isinstance(value, str) and value.strip() == ""):
                return False

        # Nếu tất cả các trường đều hợp lệ
        return True

    def handle_in_hoa_don(self):
        data = self.get_thong_tin()
        if not self.check_required_data(data):
            QMessageBox.warning(self, 'Cảnh báo',
                                f'Chua có đủ thông tin in phiếu hoá đơn!')
            return

        create_and_open_pdf_for_printing(data)

        reply = QMessageBox.question(self, "Xác nhận",
                                     f"Reset màn hình?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.reset_all()
    # </editor-fold>

    # <editor-fold desc="Reset all">
    def reset_all(self):
        ui = self.ui_tai_vu
        ui.ma_y_te.clear()
        ui.ho_ten.clear()
        ui.dia_chi.clear()
        ui.tuoi.clear()
        ui.doi_tuong.clear()
        ui.tong_so_tien.clear()

    # </editor-fold>

    # <editor-fold desc="Setup camera và QR code">
    def init_camera(self):
        """Khởi tạo các thuộc tính liên quan đến camera và QR Detector."""
        self.camera_is_on = False
        self.cap = None  # Đối tượng VideoCapture của OpenCV

        # Khởi tạo OpenCV QR Code Detector
        self.qr_detector = cv2.QRCodeDetector()

        # Timer riêng để cập nhật khung hình
        self.camera_timer = QtCore.QTimer(self)
        self.camera_timer.timeout.connect(self.update_frame)

    def toggle_camera(self):
        """Bật/Tắt camera và thay đổi trạng thái hiển thị của camera_feed_label."""
        ui = self.ui_tai_vu

        # Đảm bảo camera_feed_label tồn tại (đã khắc phục lỗi UI)
        if not hasattr(ui, 'camera_feed_label'):
            print("Lỗi: UI thiếu widget 'camera_feed_label'.")
            return

        if not self.camera_is_on:
            # BẬT CAMERA
            self.cap = cv2.VideoCapture(0)
            if self.cap.isOpened():
                self.camera_timer.start(30)
                self.camera_is_on = True

                # Hiển thị QLabel chứa Camera Feed
                ui.camera_feed_label.show()

                print("Camera đã bật.")
            else:
                print("Không thể mở camera. Vui lòng kiểm tra webcam.")

        else:
            # TẮT CAMERA
            self.camera_timer.stop()
            if self.cap:
                self.cap.release()
                self.cap = None

            # Ẩn QLabel chứa Camera Feed
            ui.camera_feed_label.clear()
            ui.camera_feed_label.setText("CAMERA TẮT")
            ui.camera_feed_label.hide()  # <-- Ẩn widget đi

            self.camera_is_on = False
            # Bỏ dòng ui.btn_mo_tat_camera.setText(...)
            print("Camera đã tắt.")

    def update_frame(self):
        """Lấy khung hình, hiển thị lên QLabel, và decode QR bằng cv2.QRCodeDetector."""
        if not self.cap or not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if ret:
            # 1. Giải mã QR code sử dụng cv2.QRCodeDetector
            data, bbox, rectified_img = self.qr_detector.detectAndDecode(frame)

            if data:
                # Nếu giải mã thành công
                self.process_qr_data(data)

                # Tắt camera sau khi quét thành công
                self.toggle_camera()
                return  # Thoát sớm

            # 2. Hiển thị khung hình lên QLabel
            # Chuyển đổi màu sắc từ BGR (OpenCV) sang RGB (PyQt)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w

            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            p = convert_to_qt_format.scaled(self.ui_tai_vu.camera_feed_label.size(),
                                            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                            QtCore.Qt.TransformationMode.SmoothTransformation)

            self.ui_tai_vu.camera_feed_label.setPixmap(QPixmap.fromImage(p))

    def process_qr_data(self, data: str):
        """
        Xử lý dữ liệu mã QR và điền vào form dựa trên định dạng 'Trường:Giá trị|Trường:Giá trị'.

        Định dạng dữ liệu QR được kỳ vọng:
        'MaYTe:BN0002|BHYT:...|DTuong:...|Ten:...|Tuoi:...|GT:...|DC:...|SĐT:...|Tien:...'
        """
        # print(f"Dữ liệu QR Code được quét: {data}")
        ui = self.ui_tai_vu

        # Dictionary để lưu trữ các cặp key-value
        data_parts = {}

        try:
            # 1. Tách chuỗi bằng dấu '|'
            pairs = data.split('|')

            # 2. Tách từng cặp key:value và lưu vào dictionary
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)  # Chỉ tách ở dấu ':' đầu tiên
                    data_parts[key.strip()] = value.strip()

            # 3. Áp dụng giá trị vào các trường (Sử dụng .get() để an toàn nếu thiếu trường)

            # Thông tin cơ bản
            ui.ma_y_te.setText(data_parts.get('MaYTe', ''))
            ui.ho_ten.setText(data_parts.get('Ten', ''))
            ui.dia_chi.setText(data_parts.get('DC', ''))
            ui.tuoi.setText(data_parts.get('Tuoi', ''))
            self.bhyt = data_parts.get('BHYT', '')

            # Đối tượng (sử dụng trường DTuong)
            ui.doi_tuong.setText(data_parts.get('DTuong', ''))

            # Tổng số tiền (loại bỏ " VND" và dấu phẩy, sau đó format lại)
            tong_tien_raw = data_parts.get('Tien', '')
            if tong_tien_raw:
                # Xóa " VND" và dấu '.'
                # Thay dấu ',' bằng dấu '.'
                tong_tien_input = (tong_tien_raw.replace(' VND', '')
                                   .replace('.','')
                                   .replace(',', '.'))

                # Điền số tiền đã làm sạch vào QLineEdit (để format_tong_so_tien xử lý)
                ui.tong_so_tien.setText(tong_tien_input)

                # Gọi hàm format để tự động cập nhật số tiền và thành chữ
                self.format_tong_so_tien()

            QtWidgets.QMessageBox.information(self, "Thành công", "Đã điền thông tin khách hàng từ QR Code.")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Lỗi Xử Lý", f"Có lỗi xảy ra khi xử lý dữ liệu: {e}")

    # </editor-fold>