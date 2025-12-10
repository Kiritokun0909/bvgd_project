from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QRegularExpression, QDate
from PyQt6.QtGui import QIntValidator, QRegularExpressionValidator
from PyQt6.QtWidgets import QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QMessageBox, QLineEdit
import json

from app.core.in_phieu_toa_thuoc import create_and_open_pdf_for_printing

from app.services.BenhNhanService import get_benh_nhan_by_id
from app.services.DoiTuongService import get_list_doi_tuong
from app.services.PhongBanService import get_list_phong_ban

from app.styles.styles import DELETE_BTN_STYLE, ADD_BTN_STYLE, TUOI_STYLE, COMPLETER_THUOC_STYLE

from app.ui.TabKhamBenh import Ui_formKhamBenh

from app.utils.config_manager import ConfigManager
from app.utils.cong_thuc_tinh_bhyt import tinh_tien_mien_giam
from app.utils.constants import MA_Y_TE_LENGTH
from app.utils.ui_helpers import IcdCompleterHandler, DuocCompleterHandler
from app.utils.utils import populate_combobox, \
    calculate_age, format_currency_vn, unformat_currency_to_float, populate_list_to_combobox

from app.configs.table_thuoc_configs import *
from app.utils.constants import GIAI_QUYET_FILE_PATH
from app.utils.write_json_line import write_json_lines, MODE_JSON


def _get_int_value(table: QtWidgets.QTableWidget, row: int, col: int) -> int:
    """Hàm tiện ích để lấy giá trị số từ QLineEdit, trả về 0 nếu rỗng/lỗi."""
    widget = table.cellWidget(row, col)
    if widget and widget.text().strip():
        try:
            return int(widget.text())
        except ValueError:
            pass
    return 0


class KhamBenhTabController(QtWidgets.QWidget):

    # <editor-fold desc="Khoi tao man hinh kham benh">
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.ma_y_te = None
        self.dia_chi = None

        self.input_drug_name = None
        self.input_drug_so_luong = None

        self.duoc_handler = None
        self.icd_handler = IcdCompleterHandler(self, min_search_length=1)

        # <editor-fold desc="Init UI">
        self.ui_kham = Ui_formKhamBenh()
        self.ui_kham.setupUi(tab_widget_container)
        self.ui_kham.ds_benh_nhan_cho.clear()
        # </editor-fold>

        self.duoc_handler = DuocCompleterHandler(
            table_widget=self.ui_kham.ds_thuoc,
            parent=self,
            min_search_length=1,
            popup_min_width=1000)

        # <editor-fold desc="Load data, connect signals,...">
        self.init()
        self.setup_ngay_gio_kham_realtime_clock()
        self.setup_prescription_table()

        self.config_manager = ConfigManager()
        self._load_saved_settings()
        self._connect_signals()
        self.apply_stylesheet()
        # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="Reset thông tin màn hình">
    def reset_data(self):
        self.ma_y_te = ''
        self.ui_kham.ma_y_te.clear()
        self.ui_kham.ho_ten_bn.clear()
        self.ui_kham.dia_chi.clear()
        self.ui_kham.tuoi.clear()
        self.ui_kham.so_bhyt.clear()
        self.ui_kham.sdt.clear()
        self.ui_kham.cb_doi_tuong.setCurrentIndex(0)

        current_date = QDate.currentDate()
        self.ui_kham.bhyt_from.setDate(current_date)
        self.ui_kham.bhyt_to.setDate(current_date)
        self.ui_kham.ngay_sinh.setDate(current_date)

        self.ui_kham.mach.clear()
        self.ui_kham.nhiet_do.clear()
        self.ui_kham.nhiet_do.clear()
        self.ui_kham.huyet_ap_1.clear()
        self.ui_kham.huyet_ap_2.clear()
        self.ui_kham.chieu_cao.clear()
        self.ui_kham.can_nang.clear()
        self.ui_kham.duong_huyet.clear()
        self.ui_kham.spo2.clear()

        self.ui_kham.chan_doan.clear()
        self.ui_kham.ma_icd.clear()  # Đã thay đổi
        self.ui_kham.ma_icd_phu.clear()
        self.ui_kham.cb_cach_giai_quyet.setCurrentIndex(0)

        self.ui_kham.is_hen_kham.setChecked(False)
        self.ui_kham.so_ngay_hen.clear()
        self.ui_kham.ngay_hen_kham.setDate(QtCore.QDate.currentDate())
    # </editor-fold>

    # <editor-fold desc="Load thong tin lan dau khoi tao man hinh">
    def init(self):
        """Đổ dữ liệu ban đầu vào các combo_box."""
        populate_combobox(self.ui_kham.cb_cach_giai_quyet, 'TenGiaiQuyet', 'MaGiaiQuyet', GIAI_QUYET_FILE_PATH)

        doi_tuong_data = get_list_doi_tuong()
        populate_list_to_combobox(self.ui_kham.cb_doi_tuong,
                                  data=doi_tuong_data,
                                  display_col=2, key_col=0)
        phong_ban_data = get_list_phong_ban()
        populate_list_to_combobox(self.ui_kham.cb_phong_kham,
                                  data=phong_ban_data,
                                  display_col=2, key_col=0)

        # <editor-fold desc="set validator">
        int_validator = QIntValidator(0, 9999)
        self.ui_kham.so_ngay_hen.setValidator(int_validator)
        self.ui_kham.mach.setValidator(int_validator)
        self.ui_kham.nhiet_do.setValidator(int_validator)
        self.ui_kham.nhip_tho.setValidator(int_validator)
        self.ui_kham.huyet_ap_1.setValidator(int_validator)
        self.ui_kham.huyet_ap_2.setValidator(int_validator)
        self.ui_kham.chieu_cao.setValidator(int_validator)
        self.ui_kham.can_nang.setValidator(int_validator)
        self.ui_kham.duong_huyet.setValidator(int_validator)
        self.ui_kham.spo2.setValidator(int_validator)
        self.ui_kham.sdt.setValidator(QRegularExpressionValidator(QRegularExpression(r'^\d{10}$')))

        self.ui_kham.so_ngay_hen.setReadOnly(True)
        # </editor-fold>

        self.reset_data()

    # </editor-fold>

    # <editor-fold desc="Setup event cho cac vung nhap lieu va cac nut">
    def _connect_signals(self):
        """Kết nối tất cả các tín hiệu và slot."""
        self.ui_kham.ma_y_te.textEdited.connect(self.load_thong_tin_benh_nhan)
        self.ui_kham.cb_phong_kham.currentIndexChanged.connect(self._save_settings)
        self.ui_kham.ten_bac_si.textEdited.connect(self._save_settings)
        self.ui_kham.is_hen_kham.clicked.connect(self.update_ngay_hen)
        self.ui_kham.so_ngay_hen.textEdited.connect(self.update_ngay_hen_kham_date)
        self.ui_kham.btn_in_phieu.clicked.connect(self.print_drug_bill)
        self.ui_kham.btn_reset_all.clicked.connect(self.reset_all)

        self.ui_kham.ngay_sinh.dateChanged.connect(self.update_tuoi)

        self.icd_handler.connect_to(self.ui_kham.ma_icd)
        self.icd_handler.activated_with_data.connect(self._on_icd_selected)
    # </editor-fold>

    # <editor-fold desc="Load & Save setting phòng khám">
    def _save_settings(self):
        """Lưu Mã phòng khám và Tên bác sĩ hiện tại vào QSettings."""
        phong_kham_code = self.ui_kham.cb_phong_kham.currentText()
        ten_bac_si_hien_tai = self.ui_kham.ten_bac_si.text()
        self.config_manager.save_last_selection(phong_kham_code, ten_bac_si_hien_tai)

    def _load_saved_settings(self):
        """Tải giá trị đã lưu và áp dụng chúng cho các widget."""
        phong_kham_saved, bac_si_saved = self.config_manager.load_last_selection()

        if phong_kham_saved:
            index = self.ui_kham.cb_phong_kham.findText(phong_kham_saved)
            if index != -1:
                self.ui_kham.cb_phong_kham.setCurrentIndex(index)

        if bac_si_saved:
            self.ui_kham.ten_bac_si.setText(bac_si_saved)

    # </editor-fold>

    def apply_stylesheet(self):
        self.ui_kham.btn_in_phieu.setStyleSheet(ADD_BTN_STYLE)
        self.ui_kham.btn_reset_all.setStyleSheet(ADD_BTN_STYLE)
        self.ui_kham.cb_phong_kham.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_kham.cb_doi_tuong.setStyleSheet(COMPLETER_THUOC_STYLE)

        self.ui_kham.ma_icd.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_kham.cb_gioi_tinh.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_kham.cb_cach_giai_quyet.setStyleSheet(COMPLETER_THUOC_STYLE)
        # self.ui_kham.ma_icd.completer().popup().setStyleSheet(COMPLETER_THUOC_STYLE)

    # <editor-fold desc="Load thông tin bệnh nhân">
    def update_tuoi(self):
        ui = self.ui_kham
        ngay_sinh = ui.ngay_sinh.date()
        tuoi = str(calculate_age(ngay_sinh.toString('dd/MM/yyyy')))
        ui.tuoi.setText(tuoi)
        ui.tuoi.setStyleSheet(TUOI_STYLE)

    def set_thong_tin_benh_nhan(self, benh_nhan_data: tuple):
        ui = self.ui_kham

        self.ma_y_te = str(benh_nhan_data[0]).upper()
        ho_ten = benh_nhan_data[1]
        gioi_tinh = benh_nhan_data[2]
        nam_sinh = benh_nhan_data[3]
        sdt = benh_nhan_data[4]
        dia_chi = benh_nhan_data[5]

        ngay_sinh = QDate(int(nam_sinh), 1, 1) if nam_sinh is not None else QDate.currentDate()

        ui.ma_y_te.setText(self.ma_y_te)
        ui.ho_ten_bn.setText(str(ho_ten) if ho_ten is not None else '')
        ui.cb_gioi_tinh.setCurrentText('Nữ' if gioi_tinh == 'G' else 'Nam')
        ui.ngay_sinh.setDate(ngay_sinh)
        ui.sdt.setText(str(sdt) if sdt is not None else '')
        ui.dia_chi.setText(str(dia_chi) if dia_chi is not None else '')
        self.update_tuoi()

    def load_thong_tin_benh_nhan(self, ma_y_te: str):
        """Lọc dữ liệu bệnh nhân và cập nhật giao diện."""
        if len(ma_y_te) != MA_Y_TE_LENGTH:
            return

        benh_nhan_data = get_benh_nhan_by_id(ma_y_te)
        if benh_nhan_data is None:
            print(f'Không tìm thấy bệnh nhân với mã {ma_y_te}')
            return

        self.set_thong_tin_benh_nhan(benh_nhan_data)

    # </editor-fold>

    # <editor-fold desc="Setup đồng hồ ngày giờ khám">
    def setup_ngay_gio_kham_realtime_clock(self):
        """Thiết lập QTimer để cập nhật ngay_gio_kham mỗi giây."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_ngay_gio_kham_datetime_edit)
        self.timer.start(1000)
        self.update_ngay_gio_kham_datetime_edit()

    def update_ngay_gio_kham_datetime_edit(self):
        """Hàm cập nhật QDateTimeEdit với thời gian hệ thống."""
        self.ui_kham.ngay_gio_kham.setDateTime(QtCore.QDateTime.currentDateTime())

    # </editor-fold>

    # <editor-fold desc="Handle & Cập nhật ngày hẹn khám">
    def update_ngay_hen(self):
        """Xử lý logic khi checkbox hẹn khám được click."""
        is_checked = self.ui_kham.is_hen_kham.isChecked()
        self.ui_kham.so_ngay_hen.setReadOnly(not is_checked)
        if not is_checked:
            self.ui_kham.so_ngay_hen.setText('')
            self.ui_kham.ngay_hen_kham.setDate(QtCore.QDate.currentDate())
        else:
            self.update_ngay_hen_kham_date(self.ui_kham.so_ngay_hen.text())

    def update_ngay_hen_kham_date(self, days_text: str):
        """Tính toán ngày hẹn khám dựa trên số ngày nhập vào."""
        try:
            days = int(days_text)
            if days < 0:
                days = 0

            new_date = QtCore.QDate.currentDate().addDays(days)
            self.ui_kham.ngay_hen_kham.setDate(new_date)

        except ValueError:
            if not days_text:
                self.ui_kham.ngay_hen_kham.setDate(QtCore.QDate.currentDate())
            pass  # Giữ giá trị cũ nếu nhập ký tự không phải số

    # </editor-fold>

    # <editor-fold desc="Setup table toa thuôc">
    def setup_prescription_table(self):
        """Thiết lập cấu trúc cột và khởi tạo dòng nhập liệu."""
        self.ui_kham.ds_thuoc.setColumnCount(DRUG_COL_COUNT)
        self.ui_kham.ds_thuoc.setHorizontalHeaderLabels(HEADER_THUOC)

        # ẨN CỘT MÃ THUỐC (Chỉ dùng cho dữ liệu, không hiển thị cho người dùng)
        self.ui_kham.ds_thuoc.setColumnHidden(COL_MA_THUOC, True)

        # Thiết lập chiều rộng
        self.ui_kham.ds_thuoc.setColumnWidth(COL_TEN_THUOC, COL_TEN_THUOC_WIDTH)

        self.add_input_row()

    # </editor-fold>

    # <editor-fold desc="Hàm xử lý chọn thuốc">
    def _on_duoc_selected(self, raw_data: tuple, row_index: int):
        """
        Xử lý khi một thuốc được chọn từ completer.
        Điền dữ liệu vào dòng nhập liệu (dòng 0).
        """
        if not raw_data or row_index != 0:
            return

        table = self.ui_kham.ds_thuoc

        # Data từ DuocService:
        # (Duoc_Id, MaDuoc, TenDuocDayDu, DonGia, TenDonViTinh, CachDung)
        try:
            ma_duoc = str(raw_data[1])
            ten_duoc = str(raw_data[2])
            don_gia = float(raw_data[3])
            don_vi_tinh = str(raw_data[4])
            cach_dung = str(raw_data[5])
        except (IndexError, TypeError, ValueError) as e:
            print(f"Lỗi xử lý dữ liệu dược: {e}, data: {raw_data}")
            return

        # 1. Cột MÃ THUỐC (COL_MA_THUOC) - ẨN
        ma_thuoc_widget = table.cellWidget(row_index, COL_MA_THUOC)
        if ma_thuoc_widget and isinstance(ma_thuoc_widget, QLineEdit):
            ma_thuoc_widget.setText(ma_duoc)

        # 2. Cột TÊN THUỐC (COL_TEN_THUOC)
        ten_thuoc_widget = table.cellWidget(row_index, COL_TEN_THUOC)
        if ten_thuoc_widget and isinstance(ten_thuoc_widget, QLineEdit):
            # Block signal để tránh kích hoạt lại tìm kiếm
            ten_thuoc_widget.blockSignals(True)
            ten_thuoc_widget.setText(ten_duoc)
            ten_thuoc_widget.blockSignals(False)

        # 3. Cột Đơn vị tính (COL_DON_VI_TINH)
        unit_widget = table.cellWidget(row_index, COL_DON_VI_TINH)
        if unit_widget and isinstance(unit_widget, QLineEdit):
            unit_widget.setText(don_vi_tinh)

        # 4. Cột Đơn giá (COL_DON_GIA)
        price_widget = table.cellWidget(row_index, COL_DON_GIA)
        if price_widget and isinstance(price_widget, QLineEdit):
            price_widget.setText(format_currency_vn(don_gia))

        # 5. Cột Đường dùng (COL_DUONG_DUNG)
        duong_dung_widget = table.cellWidget(row_index, COL_DUONG_DUNG)
        if duong_dung_widget and isinstance(duong_dung_widget, QLineEdit):
            duong_dung_widget.setText(cach_dung)

        # Tự động focus vào ô tiếp theo (Sáng)
        sang_widget = table.cellWidget(row_index, COL_SANG)
        if sang_widget:
            sang_widget.setFocus()

    # </editor-fold>

    # <editor-fold desc="Cập nhật tính toán số lượng thuốc">
    def calculate_quantity(self, input_row_index: int) -> int:
        """Tính toán Số lượng = (Sáng + Trưa + Chiều + Tối) x Số Ngày."""
        table = self.ui_kham.ds_thuoc

        so_ngay = _get_int_value(table, input_row_index, COL_SO_NGAY)
        tong_lieu = sum([_get_int_value(table, input_row_index, col)
                         for col in [COL_SANG, COL_TRUA, COL_CHIEU, COL_TOI]])

        return tong_lieu * so_ngay

    def update_quantity(self):
        """Cập nhật Số lượng khi liều lượng hoặc số ngày thay đổi."""
        quantity = self.calculate_quantity(0)
        self.input_drug_so_luong.setText(str(quantity))

    # </editor-fold>

    # <editor-fold desc="Thêm dòng input row mới vào đầu bảng">
    def add_input_row(self):
        """Tạo dòng nhập liệu mới tại index 0 (luôn là dòng đầu tiên)."""
        table = self.ui_kham.ds_thuoc
        table.insertRow(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText("")
        table.setVerticalHeaderItem(0, item)

        # 1a. TẠO CỘT MÃ THUỐC (ReadOnly, rỗng)
        ma_thuoc = QLineEdit()
        ma_thuoc.setReadOnly(True)
        table.setCellWidget(0, COL_MA_THUOC, ma_thuoc)

        # 1b. Tạo QLineEdit TÊN THUỐC và gán QCompleter
        input_drug_name = QLineEdit()

        # Kết nối QLineEdit với DuocCompleterHandler
        self.duoc_handler.connect_to(input_drug_name)

        # Kết nối tín hiệu khi chọn một mục
        # Chúng ta cần `raw_data` và `row_index` (luôn là 0)
        self.duoc_handler.activated_with_data.connect(
            lambda text, raw_data: self._on_duoc_selected(raw_data, 0)
        )

        # Gán LineEdit vào ô TÊN THUỐC
        table.setCellWidget(0, COL_TEN_THUOC, input_drug_name)

        # Cập nhật biến tham chiếu
        self.input_drug_name = input_drug_name

        # 2. Các cột dữ liệu còn lại (Bắt đầu từ cột Đơn vị tính, index 2)
        # DRUG_COL_COUNT - 1 là cột cuối cùng (Huỷ)
        for col in range(COL_DON_VI_TINH, DRUG_COL_COUNT - 1):  # Bắt đầu từ COL_DON_VI_TINH (index 2)
            line_edit = QLineEdit()

            # Thiết lập READ-ONLY (Đơn vị tính, Đơn giá, Số lượng)
            if HEADER_THUOC[col] in COLUMN_REQUIRE_READ_ONLY:
                line_edit.setReadOnly(True)

            # ... (Các kết nối và validator khác không đổi) ...
            if HEADER_THUOC[col] in COLUMN_REQUIRE_ONLY_NUMBER:
                line_edit.setValidator(QtGui.QIntValidator())

            table.setCellWidget(0, col, line_edit)

            if COL_SANG <= col <= COL_SO_NGAY:
                line_edit.textEdited.connect(self.update_quantity)

            if col >= COL_SANG:
                line_edit.returnPressed.connect(lambda: self.finalize_drug_entry(0))

            if col == COL_SO_LUONG:
                self.input_drug_so_luong = line_edit

        # Cột Hủy ở dòng nhập liệu (dòng nhập liệu không cần nút Hủy)
        table.setCellWidget(0, COL_HUY, QWidget())

    # </editor-fold>

    # <editor-fold desc="Thêm dòng thuốc mới vào bảng thuốc">
    def validate_drug_entry(self, input_row_index: int) -> bool:
        """Xác thực dữ liệu nhập vào trước khi thêm vào bảng tĩnh."""
        table = self.ui_kham.ds_thuoc

        drug_name_widget = table.cellWidget(input_row_index, COL_TEN_THUOC)

        # 1. Kiểm tra Tên Thuốc
        if not drug_name_widget or not drug_name_widget.text().strip():
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập và chọn Tên Thuốc.")
            drug_name_widget.setFocus()
            return False


        # 2. Kiểm tra Mã Thuốc
        ma_thuoc_widget = table.cellWidget(input_row_index, COL_MA_THUOC)
        if not ma_thuoc_widget or not ma_thuoc_widget.text().strip():
            QMessageBox.warning(self, "Lỗi xác thực",
                                f"Tên thuốc '{drug_name_widget.text()}' không hợp lệ. \n"
                                f"Vui lòng chọn thuốc từ danh sách gợi ý.")
            drug_name_widget.setFocus()
            drug_name_widget.selectAll()
            return False

        so_ngay = _get_int_value(table, input_row_index, COL_SO_NGAY)
        if so_ngay == 0:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Số Ngày phải lớn hơn 0.")
            table.cellWidget(input_row_index, COL_SO_NGAY).setFocus()
            return False

        tong_lieu = self.calculate_quantity(input_row_index)

        if tong_lieu == 0:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Ít nhất phải nhập liều Sáng, Trưa, Chiều, hoặc Tối.")
            table.cellWidget(input_row_index, COL_SANG).setFocus()
            return False

        if self.calculate_quantity(input_row_index) == 0:
            QMessageBox.warning(self, "Lỗi nhập liệu", "Số lượng tính toán phải lớn hơn 0.")
            table.cellWidget(input_row_index, COL_SO_NGAY).setFocus()
            return False

        return True

    def _extract_drug_data(self, input_row_index: int) -> list:
        """Trích xuất toàn bộ dữ liệu từ dòng nhập liệu (trừ cột Hủy) và tính Số lượng."""
        table = self.ui_kham.ds_thuoc
        final_drug_data = []
        so_luong_tinh_toan = self.calculate_quantity(input_row_index)

        # DRUG_COL_COUNT - 1 là số cột dữ liệu (không bao gồm cột Hủy)
        for col in range(DRUG_COL_COUNT - 1):
            # Mã thuốc và Tên thuốc là widget, Số lượng được tính toán
            if col == COL_MA_THUOC:
                widget = table.cellWidget(input_row_index, COL_MA_THUOC)
                final_drug_data.append(widget.text() if widget else "")
            elif col == COL_TEN_THUOC:
                widget = table.cellWidget(input_row_index, COL_TEN_THUOC)
                final_drug_data.append(widget.text() if widget else "")
            elif col == COL_SO_LUONG:
                final_drug_data.append(str(so_luong_tinh_toan))
            else:
                line_edit = table.cellWidget(input_row_index, col)
                final_drug_data.append(line_edit.text() if line_edit else "")

        return final_drug_data

    def _insert_static_drug_row(self, table: QtWidgets.QTableWidget, data_row_index: int, drug_data: list):
        """Chèn dòng dữ liệu tĩnh và nút Hủy vào bảng."""
        table.insertRow(data_row_index)

        for col, value in enumerate(drug_data):
            item = QTableWidgetItem(str(value))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            table.setItem(data_row_index, col, item)

        # Thêm nút Hủy
        delete_btn = QPushButton("Hủy")
        delete_btn.setStyleSheet(DELETE_BTN_STYLE)
        delete_btn.clicked.connect(self.handle_delete_row)

        widget_container = QWidget()
        layout = QHBoxLayout(widget_container)
        layout.addWidget(delete_btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        table.setCellWidget(data_row_index, COL_HUY, widget_container)

    def finalize_drug_entry(self, input_row_index: int):
        """Xác thực, đọc dữ liệu, chuyển dòng nhập liệu thành tĩnh và tạo dòng nhập liệu mới."""
        if not self.validate_drug_entry(input_row_index):
            return

        table = self.ui_kham.ds_thuoc

        # 1. Trích xuất dữ liệu
        final_drug_data = self._extract_drug_data(input_row_index)

        # 2. Xóa dòng nhập liệu cũ
        table.removeRow(input_row_index)

        # 3. Chèn dòng dữ liệu tĩnh mới
        self._insert_static_drug_row(table, data_row_index=0, drug_data=final_drug_data)

        # 4. Tạo lại dòng nhập liệu mới tại index 0
        self.add_input_row()
        self.update_row_numbers()

        # 5. Tự động focus lại
        if self.input_drug_name:
            self.input_drug_name.setFocus()

    # </editor-fold>

    # <editor-fold desc="Xoá dòng thuốc trong bảng thuốc">
    def handle_delete_row(self):
        """Xử lý sự kiện khi nút Hủy (xóa dòng) được click."""
        table = self.ui_kham.ds_thuoc
        button = self.sender()
        if button is None or not isinstance(button, QPushButton):
            return

        # Tìm dòng chứa nút bấm
        widget_container = button.parent()
        global_pos = widget_container.mapToGlobal(QtCore.QPoint(0, 0))
        local_pos = table.viewport().mapFromGlobal(global_pos)
        row_index = table.indexAt(local_pos).row()

        if row_index <= 0 or row_index >= table.rowCount():
            return

        reply = QMessageBox.question(self, "Xác nhận",
                                     f"Bạn có chắc muốn hủy dòng thuốc số {row_index}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            table.removeRow(row_index)

        self.update_row_numbers()

    # </editor-fold>

    # <editor-fold desc="Cập nhật số dòng thuốc trong bảng">
    def update_row_numbers(self):
        """Đánh số lại các dòng dữ liệu sau khi thêm hoặc xóa."""
        table = self.ui_kham.ds_thuoc
        # Bắt đầu từ dòng 1 (vì dòng 0 là dòng nhập liệu)
        for i in range(1, table.rowCount()):
            item = QtWidgets.QTableWidgetItem(str(i))
            table.setVerticalHeaderItem(i, item)

    # </editor-fold>

    def _on_icd_selected(self, selected_text: str, raw_data: object):
        """
        Xử lý khi một mục ICD được chọn từ handler.
        raw_data chính là tuple ('A01', 'Bệnh tả')
        """
        if raw_data:
            ma_icd = raw_data[0] # Lấy mã
            self.ui_kham.ma_icd.blockSignals(True)
            self.ui_kham.ma_icd.setText(ma_icd)
            self.ui_kham.ma_icd.blockSignals(False)
        else:
            # Fallback nếu không có raw data
            ma_icd = selected_text.split(' - ')[0].strip()
            self.ui_kham.ma_icd.blockSignals(True)
            self.ui_kham.ma_icd.setText(ma_icd)
            self.ui_kham.ma_icd.blockSignals(False)

    def reset_prescription_table(self):
        """Xóa tất cả các dòng thuốc tĩnh (từ dòng 1 trở đi) và giữ lại dòng nhập liệu."""
        table = self.ui_kham.ds_thuoc

        # Xóa tất cả các dòng (ngoại trừ dòng nhập liệu tại index 0)
        # Bắt đầu từ dòng cuối cùng (rowCount() - 1) lùi về dòng 1
        for i in range(table.rowCount() - 1, 0, -1):
            table.removeRow(i)

        # Đảm bảo rằng luôn có đúng 1 dòng nhập liệu sau khi reset
        if table.rowCount() == 0:
            self.add_input_row()

        self.update_row_numbers()

    def reset_all(self):
        self.reset_data()
        self.reset_prescription_table()

    # <editor-fold desc="Xử lý nút in toa thuốc">
    def get_thong_tin_kham(self):
        ui = self.ui_kham
        ngay_gio_kham = ui.ngay_gio_kham.dateTime().toString("dd/MM/yyyy HH:mm:ss")

        # Xử lý Huyết áp
        huyet_ap = f"{ui.huyet_ap_1.text().strip()}/{ui.huyet_ap_2.text().strip()}"
        if huyet_ap == '/': huyet_ap = ''

        ngay_hen_kham = ui.ngay_hen_kham.date().toString("dd/MM/yyyy")
        is_checked = ui.is_hen_kham.isChecked()
        so_ngay_hen = ui.so_ngay_hen.text()
        so_ngay_hen = 0 if not so_ngay_hen else int(so_ngay_hen)
        dr_note_text = (f"Hẹn tái khám {ui.so_ngay_hen.text().strip()} ngày "
                        f"({ngay_hen_kham})") if is_checked and so_ngay_hen > 0 else ""

        table = ui.ds_thuoc
        drug_list = []
        tong_tien_thuoc = 0.0

        # Bắt đầu từ dòng 1 (vì dòng 0 là dòng nhập liệu)
        for row in range(1, table.rowCount()):
            drug_row_data = {}

            # Thu thập các cột dữ liệu khác từ bảng
            for col_index, header in enumerate(HEADER_THUOC):
                # Bỏ qua cột Hủy
                if header == 'Huỷ':
                    continue

                # Sử dụng FIELD_MAPPING để đặt tên field tiếng Anh
                field_name = FIELD_MAPPING.get(header, header)

                item = table.item(row, col_index)
                drug_row_data[field_name] = item.text().strip() if item else ""

            drug_list.append(drug_row_data)

        mapped_drugs = []
        for idx, drug in enumerate(drug_list):
            mapped_drugs.append({
                'STT': str(idx + 1),
                'TenThuoc': drug.get('TenThuoc', ''),
                'TenThuocPhu': drug.get('DuongDung', ''),
                'DonViTinh': drug.get('DonViTinh', ''),
                'Sang': drug.get('Sang', '0'),
                'Trua': drug.get('Trua', '0'),
                'Chieu': drug.get('Chieu', '0'),
                'Toi': drug.get('Toi', '0'),
                'SoNgay': drug.get('SoNgay', '0'),
                'SoLuong': drug.get('SoLuong', '0'),
                'DonGia': drug.get('DonGia', '0'),
            })

            so_luong = drug.get('SoLuong', '0')
            don_gia = drug.get('DonGia', '0')
            tong_tien_thuoc += int(so_luong) * unformat_currency_to_float(don_gia)

        ma_doi_tuong = str(ui.cb_doi_tuong.currentData())
        tong_bhyt_thanh_toan = tinh_tien_mien_giam(tong_tien_thuoc, tong_tien_thuoc, ma_doi_tuong)
        tong_benh_nhan_thanh_toan = tong_tien_thuoc - tong_bhyt_thanh_toan

        data = {
            'PhongKham': ui.cb_phong_kham.currentText(),
            'TenBacSi': ui.ten_bac_si.text().strip(),
            'NgayTiepNhan': ngay_gio_kham,
            'NgayKham': ui.ngay_gio_kham.date().toString('dd'),
            'ThangKham': ui.ngay_gio_kham.date().toString('MM'),
            'NamKham': ui.ngay_gio_kham.date().toString('yyyy'),

            'MaYTe': ui.ma_y_te.text().strip().upper(),
            'HoTen': ui.ho_ten_bn.text().strip(),
            'GioiTinh': ui.cb_gioi_tinh.currentText(),
            'Tuoi': ui.tuoi.text().strip(),
            'DiaChi': ui.dia_chi.text().strip(),
            'SDT': ui.sdt.text().strip(),
            'BHYT': ui.so_bhyt.text().strip().upper(),
            'MaDoiTuong': ui.cb_doi_tuong.currentData(),
            'DoiTuong': ui.cb_doi_tuong.currentText(),

            'ChanDoan': ui.chan_doan.text().strip(),
            'Mach': ui.mach.text().strip(),
            'HA': huyet_ap,
            'NhietDo': ui.nhiet_do.text().strip(),
            'CanNang': ui.can_nang.text().strip(),

            'SoNgayHenTaiKham': ui.so_ngay_hen.text().strip(),
            'NgayHenTaiKham': ui.ngay_hen_kham.date().toString("dd/MM/yyyy"),
            'DrNote': dr_note_text,
            'ToaThuoc': mapped_drugs,
            'TongTienThuoc': format_currency_vn(tong_tien_thuoc),
            'TongBHYTChiTra': format_currency_vn(tong_bhyt_thanh_toan),
            'TongBenhNhanTra': format_currency_vn(tong_benh_nhan_thanh_toan),
        }

        return data

    def validate_patient_info(self) -> bool:
        """
        Xác thực thông tin hành chính bệnh nhân: Họ tên, Địa chỉ, SĐT, Số BHYT.
        Trả về True nếu hợp lệ, False nếu thiếu và hiển thị cảnh báo.
        """
        ui = self.ui_kham

        # Danh sách các trường cần xác thực: (widget, tên hiển thị)
        fields_to_check = [
            (ui.ho_ten_bn, "Họ tên bệnh nhân"),
            (ui.dia_chi, "Địa chỉ"),
            (ui.sdt, "Số điện thoại"),
            (ui.chan_doan, "Chẩn đoán")
            # (ui.so_bhyt, "Số BHYT"),
        ]

        if not ui.ngay_sinh.date().isValid():
            QMessageBox.warning(self, "Thiếu dữ liệu", "Vui lòng nhập Ngày sinh hợp lệ.")
            ui.ngay_sinh.setFocus()
            return False

        # Kiểm tra các trường QLineEdit
        for field, name in fields_to_check:
            if not field.text().strip():
                QMessageBox.warning(self, "Thiếu dữ liệu", f"Vui lòng nhập {name}!")
                field.setFocus()
                return False

        return True

    def print_drug_bill(self):
        """
            Thu thập tất cả dữ liệu từ form Khám bệnh và bảng thuốc
            để chuẩn bị cho việc in ấn hoặc lưu trữ.
        """
        if not self.validate_patient_info():
            return

        data = self.get_thong_tin_kham()

        if len(data.get('ToaThuoc')) < 1:
            QMessageBox.warning(self,
                                "Thông báo",
                                f"Chưa có thuốc nào trong toa thuốc.")
            return

        json_data = json.dumps(data, indent=4, ensure_ascii=False)
        write_json_lines(json_data, MODE_JSON.PHIEU_TOA_THUOC_MODE)

        # Bổ sung logic in hoặc lưu trữ ở đây
        # QMessageBox.information(self, "Thông báo", "Đã thu thập dữ liệu form thành công. Sẵn sàng cho việc in/lưu.")

        create_and_open_pdf_for_printing(data)

        # --- THÔNG BÁO HỎI RESET MÀN HÌNH ---
        # reply = QMessageBox.question(self, "Xác nhận",
        #                              f"Khám cho bệnh nhân mới?",
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        #
        # if reply == QMessageBox.StandardButton.Yes:
        #     self.reset_all()

    # </editor-fold>

    # <editor-fold desc="Lấy thông tin bệnh nhân và phòng khám chuyển sang màn hình đăng ký dịch vụ">
    def get_hanh_chinh_data(self) -> dict:
        """
        Thu thập các thông tin hành chính cơ bản của bệnh nhân
        để chuyển sang tab/màn hình khác.
        """
        ui = self.ui_kham

        data = {
            'MaYTe': self.ma_y_te,
            'HoTenBN': ui.ho_ten_bn.text().strip(),
            'GioiTinh': ui.cb_gioi_tinh.currentText(),
            'NgaySinh': ui.ngay_sinh.date().toString('yyyy'),

            'SoBHYT': ui.so_bhyt.text().strip(),
            'BHYT_Tu': ui.bhyt_from.date().toString("dd/MM/yyyy"),
            'BHYT_Den': ui.bhyt_to.date().toString("dd/MM/yyyy"),
            'DiaChi': ui.dia_chi.text().strip(),
            'SDT': ui.sdt.text().strip(),

            'Tuoi': ui.tuoi.text().strip(),
            'MaDoiTuong': ui.cb_doi_tuong.currentData(),
            'TenDoiTuong': ui.cb_doi_tuong.currentText(),

            'MaPhongKham': ui.cb_phong_kham.currentData(),
            'PhongKham': ui.cb_phong_kham.currentText(),
            'TenBacSi': ui.ten_bac_si.text().strip(),
            'NgayGioKham': ui.ngay_gio_kham.dateTime().toString("dd/MM/yyyy HH:mm:ss"),

            'MaGiaiQuyet': ui.cb_cach_giai_quyet.currentData(),
            'ChanDoan': ui.chan_doan.text(),
        }

        return data
    # </editor-fold>