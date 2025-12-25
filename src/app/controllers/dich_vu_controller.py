import json
from datetime import datetime

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)

from app.configs.table_dich_vu_configs import *
from app.core.in_phieu_dk_dich_vu import create_and_open_pdf_for_printing

from app.services.DoiTuongService import get_list_doi_tuong
from app.services.DichVuService import (
    get_dich_vu_by_input_code,
    get_gia_dich_vu, get_list_dich_vu_by_ma_nhom_dich_vu, get_dich_vu_by_dich_vu_id, get_noi_thuc_hien_dich_vu
)
from app.services.LoaiGiaService import get_list_loai_gia_by_doi_tuong_id, get_list_loai_gia_by_dich_vu_id
from app.services.NhomDichVuService import get_nhom_dich_vu_by_ma_doi_tuong, get_all_nhom_dich_vu
from app.services.PhongBanService import get_list_phong_ban

from app.styles.styles import ADD_BTN_STYLE, DELETE_BTN_STYLE, COMPLETER_THUOC_STYLE
from app.ui.TabDichVu import Ui_formDichVu
from app.utils.cong_thuc_tinh_bhyt import tinh_tien_mien_giam
from app.utils.export_excel import export_and_show_dialog

from app.utils.ui_helpers import DichVuCompleterHandler
from app.utils.utils import (
    format_currency_vn,
    unformat_currency_to_float,
    populate_list_to_combobox,
)
from app.utils.write_json_line import write_json_lines, MODE_JSON


def create_checkbox_widget(is_checked: bool, func=None):
    widget = QWidget()
    layout = QHBoxLayout(widget)
    checkbox = QCheckBox()
    checkbox.setChecked(is_checked)
    if func:
        checkbox.clicked.connect(func)
    layout.addWidget(checkbox)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return widget

def get_checkbox_state(table, row: int, column: int) -> bool:
    widget = table.cellWidget(row, column)
    if widget:
        layout = widget.layout()
        if layout and layout.count() > 0:
            checkbox = layout.itemAt(0).widget()
            return checkbox.isChecked()
    return False

class DangKyDichVuTabController(QtWidgets.QWidget):
    dich_vu_completed = QtCore.pyqtSignal()

    # <editor-fold desc="Khoi tao man hinh dang ky dich vu">
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.thong_tin_benh_nhan = None
        self.ma_nhom_dv = None
        self.added_dich_vu_ids = set()

        # <editor-fold desc="Init UI">
        self.ui_dich_vu = Ui_formDichVu()
        self.ui_dich_vu.setupUi(tab_widget_container)
        self.ui_dich_vu.so_luong.setValidator(QtGui.QIntValidator())
        # </editor-fold>

        # <editor-fold desc="Init model search completer">
        self.dich_vu_handler = DichVuCompleterHandler(
            parent=self,
            min_search_length=0,
            popup_min_width=1000
        )
        # </editor-fold>

        # <editor-fold desc="Load data, connect signals,...">
        self.init_data()
        self.setup_table_dich_vu()
        self.connect_signals()
        self.apply_stylesheet()
        self.update_cay_dich_vu()
        # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="Reset thông tin bệnh nhân">
    def reset_thong_tin_bn(self):
        self.ui_dich_vu.ho_ten_bn.clear()
        self.ui_dich_vu.dia_chi.clear()
        self.ui_dich_vu.gioi_tinh.clear()
        self.ui_dich_vu.tuoi.clear()
        self.ui_dich_vu.nam_sinh.clear()
        self.ui_dich_vu.nghe_nghiep.clear()
        self.thong_tin_benh_nhan = None
    # </editor-fold>

    # <editor-fold desc="Load thông tin lần đầu">
    def init_data(self):
        """Load dữ liệu ban đầu từ services."""
        ui = self.ui_dich_vu

        doi_tuong_data = get_list_doi_tuong()
        populate_list_to_combobox(ui.cb_doi_tuong,
                                  data=doi_tuong_data,
                                  display_col=2,    # TenDoiTuong
                                  key_col=0)        # DoiTuong_Id

        phong_ban_data = get_list_phong_ban()
        populate_list_to_combobox(ui.cb_noi_yeu_cau,
                                  data=phong_ban_data,
                                  display_col=2,     # TenPhongBan
                                  key_col=0)         # PhongBan_Id
        populate_list_to_combobox(ui.cb_noi_thuc_hien,
                                  data=phong_ban_data,
                                  display_col=2,    # TenPhongBan
                                  key_col=0)        # PhongBan_Id

        self.handle_update_doi_tuong()
        self.load_loai_gia()
        self.load_nhom_dich_vu()

        self.reset_thong_tin_bn()

    # </editor-fold>

    # <editor-fold desc="Apply stylesheet">
    def apply_stylesheet(self):
        label_style = 'font-weight: 700; font-size: 14px'
        self.ui_dich_vu.ho_ten_bn.setStyleSheet(label_style)
        self.ui_dich_vu.nam_sinh.setStyleSheet(label_style)
        self.ui_dich_vu.tuoi.setStyleSheet(label_style)
        self.ui_dich_vu.gioi_tinh.setStyleSheet(label_style)
        self.ui_dich_vu.nghe_nghiep.setStyleSheet(label_style)
        self.ui_dich_vu.dia_chi.setStyleSheet(label_style)

        self.ui_dich_vu.btn_them.setStyleSheet(ADD_BTN_STYLE)
        self.ui_dich_vu.btn_huy.setStyleSheet(DELETE_BTN_STYLE)
        self.ui_dich_vu.btn_in_phieu.setStyleSheet(ADD_BTN_STYLE)
        self.ui_dich_vu.btn_reset_all.setStyleSheet(ADD_BTN_STYLE)
        self.ui_dich_vu.btn_xoa_dich_vu.setStyleSheet(DELETE_BTN_STYLE)
        self.ui_dich_vu.btn_export.setStyleSheet(ADD_BTN_STYLE)

        self.ui_dich_vu.cb_nhom_dich_vu.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_doi_tuong.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_loai_gia.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_noi_yeu_cau.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_noi_thuc_hien.setStyleSheet(COMPLETER_THUOC_STYLE)

    # </editor-fold>

    # <editor-fold desc="Connect signals">
    def connect_signals(self):
        ui = self.ui_dich_vu

        ui.ma_dich_vu.textEdited.connect(
            lambda: self.search_dich_vu_by_id(mode = SEARCH_BY_INPUT_CODE)
        )
        self.dich_vu_handler.connect_to(ui.ten_dich_vu)
        self.dich_vu_handler.activated_with_data.connect(self._on_dich_vu_selected)

        ui.cb_nhom_dich_vu.currentIndexChanged.connect(self.update_cay_dich_vu)
        ui.list_dich_vu.cellClicked.connect(self.handle_cell_item_one_clicked)
        ui.list_dich_vu.cellDoubleClicked.connect(self.handle_cell_item_double_clicked)

        ui.cb_doi_tuong.currentIndexChanged.connect(self.handle_update_doi_tuong)

        ui.cb_loai_gia.currentIndexChanged.connect(self.update_don_gia_dich_vu)
        ui.so_luong.textEdited.connect(self.calculate_thanh_tien)
        ui.don_gia.textEdited.connect(self.calculate_thanh_tien)
        ui.table_dich_vu.cellClicked.connect(self.handle_table_cell_clicked)

        ui.so_luong.returnPressed.connect(self.btn_them_handle)
        ui.ma_dich_vu.returnPressed.connect(self.btn_them_handle)

        ui.btn_them.clicked.connect(self.btn_them_handle)
        ui.btn_huy.clicked.connect(self._clear_input_fields)
        ui.btn_in_phieu.clicked.connect(self.btn_in_phieu_handle)
        ui.btn_reset_all.clicked.connect(self.reset_all)
        ui.btn_xoa_dich_vu.clicked.connect(self.delete_all_rows)
        ui.btn_export.clicked.connect(lambda: export_and_show_dialog(self))

    # </editor-fold>

    def handle_update_doi_tuong(self):
        doi_tuong_id = self.ui_dich_vu.cb_doi_tuong.currentData()
        if doi_tuong_id:
            self.dich_vu_handler.set_ma_doi_tuong(str(doi_tuong_id))

        self.delete_all_rows()
        self.load_loai_gia()
        self.load_nhom_dich_vu()
        self.update_cay_dich_vu()

    # <editor-fold desc="Load thông tin loại giá và nhóm dịch vụ">
    def load_loai_gia(self):
        doi_tuong_id = str(self.ui_dich_vu.cb_doi_tuong.currentData())
        if not doi_tuong_id:
            self.ui_dich_vu.cb_loai_gia.clear()
            return

        loai_gia_data = get_list_loai_gia_by_doi_tuong_id(doi_tuong_id)

        populate_list_to_combobox(
            self.ui_dich_vu.cb_loai_gia,
            data=loai_gia_data,
            display_col=2,  # TenLoaiGia
            key_col=0  # LoaiGia_Id
        )

    def load_nhom_dich_vu(self):
        doi_tuong_id = str(self.ui_dich_vu.cb_doi_tuong.currentData())
        if not doi_tuong_id:
            self.ui_dich_vu.cb_nhom_dich_vu.clear()
            return

        nhom_dv_data = get_nhom_dich_vu_by_ma_doi_tuong(doi_tuong_id)

        populate_list_to_combobox(
            self.ui_dich_vu.cb_nhom_dich_vu,
            data=nhom_dv_data,
            display_col=1,  # TEN_NHOM_DICH_VU
            key_col=0  # NHOM_DICH_VU_ID
        )
    # </editor-fold>

    # <editor-fold desc="Load thong tin benh nhan tu man hinh kham benh">
    def set_thong_tin_benh_nhan(self, benh_nhan: dict):
        ui = self.ui_dich_vu
        ui.ho_ten_bn.setText(benh_nhan.get('HoTenBN', 'N/A'))
        ui.nam_sinh.setText(benh_nhan.get('NgaySinh', 'N/A'))
        ui.tuoi.setText(benh_nhan.get('Tuoi', 'N/A'))
        ui.gioi_tinh.setText(benh_nhan.get('GioiTinh', 'N/A'))
        ui.dia_chi.setText(benh_nhan.get('DiaChi', 'N/A'))

        ma_dt = benh_nhan.get('MaDoiTuong', '')  # Đây là DoiTuong_Id
        index = ui.cb_doi_tuong.findData(ma_dt)
        if index != -1:
            ui.cb_doi_tuong.setCurrentIndex(index)
        else:
            ui.cb_doi_tuong.setCurrentText(benh_nhan.get('TenDoiTuong', 'N/A'))

    def set_thong_tin_chi_dinh(self, data):
        ui = self.ui_dich_vu
        ui.bac_si_chi_dinh.setText(data.get('TenBacSi', 'N/A'))
        phong_kham = data.get('PhongKham', '')
        if phong_kham:
            index = self.ui_dich_vu.cb_noi_yeu_cau.findText(phong_kham)
            if index != -1:
                self.ui_dich_vu.cb_noi_yeu_cau.setCurrentIndex(index)
                self.ui_dich_vu.cb_noi_thuc_hien.setCurrentIndex(index)

        chan_doan = data.get('ChanDoan', '')
        self.ui_dich_vu.chan_doan.setText(chan_doan)

        dt_str = data.get('NgayGioKham', '')
        dt = QtCore.QDateTime.fromString(dt_str, "dd/MM/yyyy HH:mm:ss")
        if dt.isValid():
            ui.dateTimeEdit.setDateTime(dt)

    def load_thong_tin_benh_nhan(self, data: dict):
        if not data:
            print("--- dk_dich_vu_controller: load_thong_tin_benh_nhan() ---")
            print("Lỗi: Không có dữ liệu bệnh nhân từ màn hình khám bệnh.")
            return

        self.thong_tin_benh_nhan = data

        self.set_thong_tin_benh_nhan(data)
        self.set_thong_tin_chi_dinh(data)

        self.ui_dich_vu.ma_dich_vu.setFocus()

    # </editor-fold>

    # <editor-fold desc="Setup table dịch vụ">
    def setup_table_dich_vu(self):
        table = self.ui_dich_vu.table_dich_vu
        table.horizontalHeader().setMinimumHeight(MIN_COLUMN_HEIGHT)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter |
                                                     Qt.TextFlag.TextWordWrap)
        self.ui_dich_vu.table_dich_vu.setColumnCount(DICH_VU_COL_COUNT)
        self.ui_dich_vu.table_dich_vu.setHorizontalHeaderLabels(HEADER_DICH_VU)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_MA_NHOM_DV, True)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_MA_DV, True)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_MA_LOAI_GIA, True)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_DICH_VU_ID, True)
        for i in range(len(HEADER_DICH_VU)):
            table.setColumnWidth(i, MIN_COLUMN_WIDTH)

        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_TEN_DV, COL_SERVICE_TABLE_DEFAULT_WIDTH * 2)
        self.update_table_dich_vu_row_number()

    # </editor-fold>

    # <editor-fold desc="Calculate thành tiền">
    def calculate_thanh_tien(self):
        ui = self.ui_dich_vu
        try:
            don_gia = float(ui.don_gia.text().replace(',', ''))
            so_luong = int(ui.so_luong.text())
            thanh_tien = don_gia * so_luong
            ui.thanh_tien.setText(f"{thanh_tien:.3f}")
        except ValueError:
            ui.thanh_tien.setText("0")

    # </editor-fold>

    # <editor-fold desc="Search dich vu">
    def search_gia_dich_vu(self, dich_vu_id: str, loai_gia_id: str) -> float:
        """Lấy đơn giá từ DB bằng INPUT_CODE và LOAI_GIA_ID."""
        if not dich_vu_id or not loai_gia_id:
            return 0.0

        don_gia = get_gia_dich_vu(dich_vu_id, loai_gia_id)

        if don_gia and don_gia[0] is not None:
            try:
                return float(don_gia[0])
            except (ValueError, TypeError):
                return 0.0
        return 0.0

    def set_thong_tin_dich_vu(self, dich_vu: dict, mode=SEARCH_BY_DICH_VU_ID):
        if dich_vu:
            nhom_dich_vu_id = str(dich_vu.get('NhomDanhMuc_Id'))
            self.ma_nhom_dv = nhom_dich_vu_id

            self.ui_dich_vu.ten_dich_vu.blockSignals(True)
            ten_dich_vu = str(dich_vu.get('TenDichVu'))
            self.ui_dich_vu.ten_dich_vu.setText(ten_dich_vu)
            self.ui_dich_vu.ten_dich_vu.blockSignals(False)

            if mode == SEARCH_BY_DICH_VU_ID:
                ma_dich_vu = str(dich_vu.get('InputCode'))
                self.ui_dich_vu.ma_dich_vu.setText(ma_dich_vu)

            dich_vu_id = str(dich_vu.get('DichVu_Id'))
            noi_thuc_hien_data = get_noi_thuc_hien_dich_vu(dich_vu_id)
            populate_list_to_combobox(
                combobox=self.ui_dich_vu.cb_noi_thuc_hien,
                data=noi_thuc_hien_data,
                display_col=2,
                key_col=0
            )

            doi_tuong_id = self.ui_dich_vu.cb_doi_tuong.currentData()
            loai_gia_data = get_list_loai_gia_by_dich_vu_id(doi_tuong_id, dich_vu_id)

            populate_list_to_combobox(
                combobox=self.ui_dich_vu.cb_loai_gia,
                data=loai_gia_data,
                display_col=1,
                key_col=0
            )

            don_gia = self.search_gia_dich_vu(
                dich_vu_id,
                self.ui_dich_vu.cb_loai_gia.currentData()
            )

            self.ui_dich_vu.don_gia.setText(str(don_gia))
            self.ui_dich_vu.so_luong.setText('1')
            self.calculate_thanh_tien()

    def search_dich_vu_by_id(self, input_code: str = '', mode=SEARCH_BY_DICH_VU_ID):
        doi_tuong_id = str(self.ui_dich_vu.cb_doi_tuong.currentData())
        if not doi_tuong_id:
            self.ui_dich_vu.ten_dich_vu.clear()
            self.ui_dich_vu.don_gia.clear()
            self.ui_dich_vu.thanh_tien.setText("0")
            return

        dich_vu_data = None
        if mode == SEARCH_BY_INPUT_CODE:
            if not input_code:
                input_code = self.ui_dich_vu.ma_dich_vu.text().strip()
            dich_vu_data = get_dich_vu_by_input_code(doi_tuong_id, input_code)
        elif mode == SEARCH_BY_DICH_VU_ID:
            dich_vu_data = get_dich_vu_by_dich_vu_id(doi_tuong_id, input_code)

        if dich_vu_data is None:
            self.ui_dich_vu.ten_dich_vu.clear()
            self.ui_dich_vu.don_gia.clear()
            self.ui_dich_vu.thanh_tien.setText("0")
            return

        dich_vu_dict = {
            'DichVu_Id': dich_vu_data[0],
            'InputCode': dich_vu_data[1],
            'TenDichVu': dich_vu_data[2],
            'NhomDanhMuc_Id': dich_vu_data[3],
        }
        self.set_thong_tin_dich_vu(dich_vu_dict)

    # </editor-fold>

    # <editor-fold desc="Update cây dịch vụ theo nhóm dịch vụ">
    def handle_nhom_dv_check_state_changed(self, is_checked: bool, input_code: str):
        if not input_code:
            return
        if is_checked:
            if input_code not in self.added_dich_vu_ids:
                self.search_dich_vu_by_id(input_code, SEARCH_BY_INPUT_CODE)
                self.add_service_row(ADD_FROM_TREE_ITEM)
                self.ui_dich_vu.ma_dich_vu.setFocus()
        else:
            if input_code in self.added_dich_vu_ids:
                self.delete_dich_vu_by_dich_vu_id(input_code)

    def create_checkbox_list_danh_muc(self, is_checked: bool, input_code: str):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        checkbox = QCheckBox()
        checkbox.setChecked(is_checked)
        checkbox.clicked.connect(lambda state: self.handle_nhom_dv_check_state_changed(state, input_code))
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    def update_cay_dich_vu(self):
        ui = self.ui_dich_vu
        table = ui.list_dich_vu

        table.blockSignals(True)
        table.clear()
        table.setRowCount(0)

        self.ui_dich_vu.list_dich_vu.verticalHeader().setVisible(False)
        ten_nhom_dich_vu = ui.cb_nhom_dich_vu.currentText()

        doi_tuong_id = ui.cb_doi_tuong.currentData()
        nhom_dich_vu_id = ui.cb_nhom_dich_vu.currentData()

        new_header = ["", f"{ten_nhom_dich_vu}"]
        table.setColumnCount(len(new_header))
        table.setHorizontalHeaderLabels(new_header)
        table.setColumnWidth(TREE_COL_DICH_VU_CHECKBOX, 45)
        table.horizontalHeader().setSectionResizeMode(TREE_COL_DICH_VU, QtWidgets.QHeaderView.ResizeMode.Stretch)

        if nhom_dich_vu_id:
            list_dich_vu = get_list_dich_vu_by_ma_nhom_dich_vu(doi_tuong_id, nhom_dich_vu_id)

            for i in range(len(list_dich_vu)):
                input_code = str(list_dich_vu[i][1])
                ten_dich_vu = str(list_dich_vu[i][2])

                current_row = table.rowCount()
                table.insertRow(current_row)

                is_checked = input_code in self.added_dich_vu_ids
                checkbox_widget = self.create_checkbox_list_danh_muc(
                    is_checked=is_checked,
                    input_code=input_code
                )
                table.setCellWidget(current_row, TREE_COL_DICH_VU_CHECKBOX, checkbox_widget)

                item_ten_dv = QTableWidgetItem(ten_dich_vu)
                item_ten_dv.setData(QtCore.Qt.ItemDataRole.UserRole, input_code)
                item_ten_dv.setFlags(item_ten_dv.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(current_row, TREE_COL_DICH_VU, item_ten_dv)

            table.blockSignals(False)

    # </editor-fold>

    # <editor-fold desc="Handle click dịch vụ trong cây nhóm dịch vụ">
    def handle_cell_item_one_clicked(self, row, column):
        table = self.ui_dich_vu.list_dich_vu
        item = table.item(row, TREE_COL_DICH_VU)
        if not item: 
            return

        input_code = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if input_code:
            self.search_dich_vu_by_id(input_code, mode=SEARCH_BY_INPUT_CODE)

    def handle_cell_item_double_clicked(self, row, column):
        self.handle_cell_item_one_clicked(row, column)
        self.add_service_row(mode=ADD_FROM_TREE_ITEM)

    # </editor-fold>

    # <editor-fold desc="Validate data">
    def validate_service_row(self, mode=None):
        ui = self.ui_dich_vu
        ma_dv = ui.ma_dich_vu.text().strip()  # INPUT_CODE
        if ma_dv in self.added_dich_vu_ids:
            QMessageBox.warning(self, "Dịch vụ đã tồn tại",
                                f"Dịch vụ có mã {ma_dv} đã được thêm vào bảng.")
            return False
        if mode == ADD_FROM_TREE_ITEM:
            return True
        if not ma_dv:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng nhập Mã dịch vụ.")
            return False
        ten_dv = ui.ten_dich_vu.text().strip()
        don_gia_str = ui.don_gia.text().strip()
        so_luong_str = ui.so_luong.text().strip()

        try:
            don_gia = float(don_gia_str.replace(',', ''))
            so_luong = int(so_luong_str)
        except ValueError:
            QMessageBox.warning(self, "Lỗi giá trị",
                                "Đơn giá hoặc số lượng không hợp lệ.")
            return False

        if not ten_dv or don_gia <= 0 or so_luong <= 0:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng kiểm tra đầy đủ tên dịch vụ, đơn giá (> 0) và số lượng (> 0).")
            return False

        return True

    # </editor-fold>

    # <editor-fold desc="Thêm dòng dịch vụ mới">
    def prepare_row_data(self):
        ui = self.ui_dich_vu

        input_code = ui.ma_dich_vu.text().strip()
        doi_tuong_id = ui.cb_doi_tuong.currentData()
        dich_vu_data = get_dich_vu_by_input_code(doi_tuong_id, input_code)

        if dich_vu_data is None:
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy dịch vụ {input_code}.")
            return None

        # (DICH_VU_ID, INPUT_CODE, TEN_DICH_VU, NHOM_DICH_VU_ID)
        dich_vu_id = dich_vu_data[0]
        ma_dv = dich_vu_data[1]
        ten_dv = dich_vu_data[2]
        nhom_dich_vu_id = str(dich_vu_data[3])

        thanh_tien = ui.thanh_tien.text().strip()
        bao_hiem_thanh_toan = "0"
        benh_nhan_thanh_toan = str(float(thanh_tien.replace(',', '')) - float(bao_hiem_thanh_toan))

        data = {
            COL_DICH_VU_ID: dich_vu_id,
            COL_MA_DV: ma_dv,
            COL_MA_NHOM_DV: nhom_dich_vu_id,
            COL_TEN_DV: ten_dv,
            COL_DON_GIA_DOANH_THU: format_currency_vn(ui.don_gia.text().strip()),
            COL_SO_LUONG: ui.so_luong.text().strip(),
            COL_THANH_TIEN_DOANH_THU: format_currency_vn(ui.thanh_tien.text().strip()),
            COL_TY_LE_TT: ui.cb_ty_le.currentText(),
            COL_MA_LOAI_GIA: ui.cb_loai_gia.currentData(),
            COL_LOAI_GIA: ui.cb_loai_gia.currentText(),
            COL_NOI_THUC_HIEN: ui.cb_noi_thuc_hien.currentText(),
            COL_BH_TT: format_currency_vn(bao_hiem_thanh_toan),
            COL_BN_TT: format_currency_vn(benh_nhan_thanh_toan),
            COL_SO_PHIEU: '',
            COL_LY_DO_KHONG_THU: '',
        }
        return data

    def add_service_row(self, mode=ADD_FROM_TREE_ITEM):
        ui = self.ui_dich_vu
        table = ui.table_dich_vu

        if not self.validate_service_row(mode):
            return

        new_row_data = self.prepare_row_data()

        if new_row_data is None:
            return

        is_khong_thu_tien = ui.is_khong_thu_tien.isChecked()
        is_khong_ho_tro = ui.is_khong_ho_tro.isChecked()
        is_chon_in = True

        current_row_count = table.rowCount()
        table.insertRow(current_row_count)

        for col, value in new_row_data.items():
            if col not in [COL_KHONG_THU_TIEN, COL_KHONG_HO_TRO, COL_CHON_IN, COL_HUY]:
                item = QTableWidgetItem(str(value))

                if col == COL_LOAI_GIA:
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, new_row_data.get(LOAI_GIA.COL_MA_LOAI_GIA_HEADER))

                if col not in [COL_SO_PHIEU, COL_LY_DO_KHONG_THU]:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(current_row_count, col, item)

        table.setCellWidget(
            current_row_count,
            COL_KHONG_THU_TIEN,
            create_checkbox_widget(is_khong_thu_tien, self.update_table_dich_vu_row_number)
        )
        table.setCellWidget(
            current_row_count,
            COL_KHONG_HO_TRO,
            create_checkbox_widget(is_khong_ho_tro, self.update_table_dich_vu_row_number)
        )
        table.setCellWidget(current_row_count, COL_CHON_IN, create_checkbox_widget(is_chon_in))
        table.setCellWidget(current_row_count, COL_HUY, self.create_delete_button_widget(new_row_data[COL_MA_DV]))

        self.update_table_dich_vu_row_number()
        self._clear_input_fields()
        self.added_dich_vu_ids.add(new_row_data[COL_MA_DV])

        self._set_list_danh_muc_checkbox_state(new_row_data[COL_MA_DV], True)
        ui.ma_dich_vu.setFocus()

    # </editor-fold>

    # <editor-fold desc="Xoá dịch vụ">
    def _set_list_danh_muc_checkbox_state(self, input_code: str, is_checked: bool):
        table = self.ui_dich_vu.list_dich_vu
        dich_vu = get_dich_vu_by_input_code(
            doi_tuong_id=self.ui_dich_vu.cb_doi_tuong.currentData(),
            input_code=input_code
        )
        for row in range(table.rowCount()):
            item = table.item(row, TREE_COL_DICH_VU)
            if not item:
                continue
            row_input_code = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if row_input_code == input_code:
                widget = table.cellWidget(row, TREE_COL_DICH_VU_CHECKBOX)
                if widget:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(is_checked)
                        return

    def find_row_by_dich_vu_id(self, dich_vu_id: str) -> int:
        table = self.ui_dich_vu.table_dich_vu
        for row in range(table.rowCount()):
            item = table.item(row, COL_MA_DV)
            if item and item.text() == dich_vu_id:
                return row
        return -1

    def delete_dich_vu_by_dich_vu_id(self, dich_vu_id: str):
        table = self.ui_dich_vu.table_dich_vu
        row_index = self.find_row_by_dich_vu_id(dich_vu_id)
        if row_index == -1:
            QMessageBox.warning(self, "Lỗi",
                                f"Không tìm thấy dịch vụ có mã {dich_vu_id} trong bảng.")
            return
        reply = QMessageBox.question(self, "Xác nhận",
                                     f"Bạn có chắc muốn hủy dịch vụ có mã {dich_vu_id}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            table.removeRow(row_index)

            if dich_vu_id in self.added_dich_vu_ids:
                self.added_dich_vu_ids.remove(dich_vu_id)
                self._set_list_danh_muc_checkbox_state(dich_vu_id, False)

            self.update_table_dich_vu_row_number()

    def delete_all_rows(self):
        table = self.ui_dich_vu.table_dich_vu
        # Xóa các dòng từ cuối lên đầu, trừ dòng tổng (nếu có)
        # Cách an toàn hơn là xóa cho đến khi rowCount == 1 (chỉ còn dòng tổng)
        while table.rowCount() > 1:
            table.removeRow(0)

        self.added_dich_vu_ids.clear()
        self.update_table_dich_vu_row_number()
        self.update_cay_dich_vu()

    # </editor-fold>

    def create_delete_button_widget(self, dich_vu_id: str):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        btn_delete = QPushButton("Xóa")
        btn_delete.setStyleSheet(DELETE_BTN_STYLE)
        btn_delete.clicked.connect(lambda: self.delete_dich_vu_by_dich_vu_id(dich_vu_id))
        layout.addWidget(btn_delete)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    # <editor-fold desc="Handle chọn dịch vụ từ completer tên dịch vụ">
    def _on_dich_vu_selected(self, selected_text: str, raw_data: tuple):
        print(raw_data)
        if raw_data:
            input_code = str(raw_data[1])
            ten_dich_vu = str(raw_data[2])

            # 1. Cập nhật lại ô 'ten_dich_vu' cho sạch
            self.ui_dich_vu.ten_dich_vu.blockSignals(True)
            self.ui_dich_vu.ten_dich_vu.setText(ten_dich_vu)
            self.ui_dich_vu.ten_dich_vu.blockSignals(False)

            # 2. Gọi logic tìm kiếm theo ID (để điền Mã DV, Đơn giá, v.v.)
            self.search_dich_vu_by_id(
                input_code=input_code,
                mode=SEARCH_BY_INPUT_CODE
            )

            # 3. Focus vào ô số lượng để nhập tiếp
            self.ui_dich_vu.so_luong.setFocus()
        else:
            print(f"Lỗi: Không tìm thấy raw_data cho {selected_text}")

    # </editor-fold>

    def _clear_input_fields(self):
        ui = self.ui_dich_vu
        ui.ma_dich_vu.clear()
        ui.ten_dich_vu.clear()
        ui.don_gia.clear()
        ui.so_luong.setText('1')
        ui.thanh_tien.setText('0')
        ui.icd_kiem_tra.clear()
        ui.cb_ty_le.setCurrentIndex(0)
        ui.is_khong_thu_tien.setChecked(False)
        ui.is_khong_ho_tro.setChecked(False)
        ui.is_bnvp.setChecked(False)
        ui.is_dich_vu_ty_le.setChecked(False)

    def handle_table_cell_clicked(self, row, col):
        if col == COL_HUY:
            return
        pass

    # <editor-fold desc="TÍNH TOÁN BHYT VÀ CẬP NHẬT BẢNG DỊCH VỤ">
    def _calculate_table_summary(self) -> dict:
        table = self.ui_dich_vu.table_dich_vu
        ma_doi_tuong = self.ui_dich_vu.cb_doi_tuong.currentData()
        total_thanh_tien = 0.0
        total_thanh_tien_huong_bao_hiem = 0.0
        max_row = table.rowCount()
        if (max_row > 0 and
                table.verticalHeaderItem(max_row - 1) and
                table.verticalHeaderItem(max_row - 1).text() == "TỔNG"):
            max_row -= 1

        for row in range(max_row):
            is_checked_khong_thu_tien = get_checkbox_state(table, row, COL_KHONG_THU_TIEN)
            is_checked_khong_ho_tro = get_checkbox_state(table, row, COL_KHONG_HO_TRO)
            item_thanh_tien = table.item(row, COL_THANH_TIEN_DOANH_THU)
            if is_checked_khong_thu_tien:
                item_thanh_tien.setText(format_currency_vn(0))
                continue
            item_don_gia = unformat_currency_to_float(table.item(row, COL_DON_GIA_DOANH_THU).text())
            item_so_luong = unformat_currency_to_float(table.item(row, COL_SO_LUONG).text())
            thanh_tien = item_don_gia * item_so_luong
            item_thanh_tien.setText(format_currency_vn(thanh_tien))
            total_thanh_tien += thanh_tien
            if not is_checked_khong_ho_tro:
                total_thanh_tien_huong_bao_hiem += thanh_tien

        total_bao_hiem_thanh_toan = 0.0
        total_benh_nhan_thanh_toan = 0.0
        for row in range(max_row):
            is_checked_khong_ho_tro = get_checkbox_state(table, row, COL_KHONG_HO_TRO)
            thanh_tien_dich_vu = unformat_currency_to_float(table.item(row, COL_THANH_TIEN_DOANH_THU).text())
            bao_hiem_thanh_toan = 0
            if not is_checked_khong_ho_tro:
                bao_hiem_thanh_toan = tinh_tien_mien_giam(
                    total_thanh_tien_huong_bao_hiem,
                    thanh_tien_dich_vu,
                    ma_doi_tuong
                )

            item_bh_tt = table.item(row, COL_BH_TT)
            item_bh_tt.setText(format_currency_vn(bao_hiem_thanh_toan))
            benh_nhan_thanh_toan = thanh_tien_dich_vu - bao_hiem_thanh_toan

            item_bn_tt = table.item(row, COL_BN_TT)
            item_bn_tt.setText(format_currency_vn(benh_nhan_thanh_toan))
            total_bao_hiem_thanh_toan += bao_hiem_thanh_toan
            total_benh_nhan_thanh_toan += benh_nhan_thanh_toan

        return {
            'ThanhTien': format_currency_vn(total_thanh_tien),
            'BHTong': format_currency_vn(total_bao_hiem_thanh_toan),
            'BNTong': format_currency_vn(total_benh_nhan_thanh_toan)
        }

    def _update_table_summary_row(self):
        table = self.ui_dich_vu.table_dich_vu
        summary_data = self._calculate_table_summary()
        row_count = table.rowCount()
        table.insertRow(row_count)
        new_summary_row_index = row_count
        total_header = QtWidgets.QTableWidgetItem("TỔNG")
        table.setVerticalHeaderItem(new_summary_row_index, total_header)
        table.setSpan(new_summary_row_index, 0, 1, COL_THANH_TIEN_DOANH_THU)
        item_label = QTableWidgetItem("TỔNG CỘNG:")
        item_label.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_label.setFlags(item_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(new_summary_row_index, 0, item_label)
        summary_cols = [
            (COL_THANH_TIEN_DOANH_THU, summary_data['ThanhTien']),
            (COL_BH_TT, summary_data['BHTong']),
            (COL_BN_TT, summary_data['BNTong'])
        ]
        for col_index, value in summary_cols:
            item = QTableWidgetItem(f"{value}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(new_summary_row_index, col_index, item)

    def update_table_dich_vu_row_number(self):
        table = self.ui_dich_vu.table_dich_vu

        row_count = table.rowCount()
        for row in range(table.rowCount() - 1, -1, -1):
            header_item = table.verticalHeaderItem(row)
            if header_item and header_item.text() == "TỔNG":
                table.removeRow(row)
                row_count -= 1  # Giảm số dòng
                break

        for i in range(row_count):
            item = QtWidgets.QTableWidgetItem(str(i + 1))
            table.setVerticalHeaderItem(i, item)

        self._update_table_summary_row()

    # </editor-fold>

    def update_don_gia_dich_vu(self):
        input_code = self.ui_dich_vu.ma_dich_vu.text()
        doi_tuong_id = self.ui_dich_vu.cb_doi_tuong.currentData()
        ma_loai_gia = self.ui_dich_vu.cb_loai_gia.currentData()
        if not input_code:
            return

        dich_vu = get_dich_vu_by_input_code(doi_tuong_id, input_code)
        gia_dv = self.search_gia_dich_vu(dich_vu[0], ma_loai_gia)
        self.ui_dich_vu.don_gia.setText(str(gia_dv))
        self.calculate_thanh_tien()

    def btn_them_handle(self):
        self.add_service_row(mode=ADD_FROM_SEARCHBOX)

    def reset_all(self):
        self.reset_thong_tin_bn()
        ui = self.ui_dich_vu
        ui.bac_si_chi_dinh.clear()
        ui.chan_doan.clear()
        ui.ghi_chu.clear()
        self.delete_all_rows()

    # <editor-fold desc="Handle nut in phieu">
    def get_thong_tin_dang_ky(self):
        ui = self.ui_dich_vu

        # Lấy dữ liệu thô từ UI/Table
        data_raw = dict()
        data_raw['ThongTinBenhNhan'] = {
            'ma_y_te': self.thong_tin_benh_nhan.get('MaYTe', ''),
            'so_bhyt': self.thong_tin_benh_nhan.get('SoBHYT', ''),
            'ma_doi_tuong': ui.cb_doi_tuong.currentData(),
            'doi_tuong': ui.cb_doi_tuong.currentText(),
            'ho_ten': ui.ho_ten_bn.text().strip(),
            'tuoi': ui.tuoi.text().strip(),
            'gioi_tinh': ui.gioi_tinh.text().strip(),
            'dia_chi': ui.dia_chi.text().strip(),
            'sdt': self.thong_tin_benh_nhan.get('SDT', ''),
        }
        data_raw['ThongTinPhongKham'] = {
            'noi_yeu_cau': ui.cb_noi_yeu_cau.currentText(),
            'bac_si': ui.bac_si_chi_dinh.text().strip(),
            'chan_doan': ui.chan_doan.text().strip(),
            'ghi_chu': ui.ghi_chu.text().strip(),
            'so_tien': '',
        }
        dich_vu_dang_ky = []
        tt_thanhtoan = {}
        table = ui.table_dich_vu

        # ------------------ PHẦN XỬ LÝ LẤY DỮ LIỆU BẢNG ------------------
        for row in range(0, table.rowCount()):
            dich_vu_row_data = {}
            v_header = table.verticalHeaderItem(row)
            if v_header and v_header.text() == "TỔNG":
                # Lấy dữ liệu từ dòng TỔNG
                tt_thanhtoan['TongThanhTienDV'] = table.item(row, COL_THANH_TIEN_DOANH_THU).text()
                tt_thanhtoan['TongBaoHiemTT'] = table.item(row, COL_BH_TT).text()
                tt_thanhtoan['TongBenhNhanTT'] = table.item(row, COL_BN_TT).text()
                continue

            for col, header in enumerate(HEADER_DICH_VU):
                if col == COL_HUY:
                    continue
                field_name = FIELD_MAPPING.get(header, header)
                if col in [COL_KHONG_THU_TIEN, COL_KHONG_HO_TRO, COL_CHON_IN]:
                    is_checked = get_checkbox_state(table, row, col)
                    dich_vu_row_data[field_name] = 1 if is_checked else 0
                    continue

                if col == COL_MA_LOAI_GIA:
                    item = table.item(row, col)
                    # Get the hidden ID we stored earlier
                    loai_gia_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
                    dich_vu_row_data['MaLoaiGia'] = str(loai_gia_id) if loai_gia_id is not None else ''

                item = table.item(row, col)
                dich_vu_row_data[field_name] = item.text().strip() if item else ''

            if dich_vu_row_data.get('ChonIn') == 1:
                dich_vu_dang_ky.append(dich_vu_row_data)

        # ------------------ PHẦN CHUYỂN ĐỔI DỮ LIỆU CHO IN PHIẾU ------------------

        # 1. Khai báo các giá trị mặc định/giả định
        default_info = {
            'PhongKham': data_raw['ThongTinPhongKham'].get('noi_yeu_cau', 'Phòng 112'),
            'CSKH': '0123',
            'MaDoiTuong': f"{data_raw['ThongTinBenhNhan'].get('ma_doi_tuong', 'Không rõ')}",
            'DoiTuong': f"{data_raw['ThongTinBenhNhan'].get('doi_tuong', 'Không rõ')}",
            'NgayTao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'TenBacSi': data_raw['ThongTinPhongKham'].get('bac_si', 'N/A'),
        }

        # Lấy thông tin tra cứu tên nhóm DV
        try:
            all_nhom_dv = get_all_nhom_dich_vu()
            lookup_dict = {}
            if all_nhom_dv:
                lookup_dict = {str(item[0]): item[1] for item in all_nhom_dv}
        except Exception as e:
            print(f"Lỗi khi tra cứu NhomDichVuService: {e}")
            lookup_dict = {}

        # 2. Xử lý phần Dịch Vụ và Gom nhóm
        grouped_services = {}
        for service in dich_vu_dang_ky:
            ma_nhom = str(service.get('MaNhomDichVu', 'KhongNhom'))
            ten_nhom = lookup_dict.get(ma_nhom, f"NHÓM CHƯA XÁC ĐỊNH ({ma_nhom})")

            if ma_nhom not in grouped_services:
                grouped_services[ma_nhom] = {
                    'MaNhomDichVu': ma_nhom,
                    'TenNhomDichVu': ten_nhom,
                    'DSDichVu': []
                }

            grouped_services[ma_nhom]['DSDichVu'].append({
                "STT": str(len(grouped_services[ma_nhom]['DSDichVu']) + 1),
                'DichVuId': service.get('DichVuId'),
                "MaDichVu": service.get("MaDichVu", ""),
                "MaLoaiGia": service.get("MaLoaiGia", ""),
                "TenLoaiGia": service.get("LoaiGia", ""),
                "TenDichVu": service.get("TenDichVu", ""),
                "SoLuong": service.get("SoLuong", "1"),
                "NoiThucHien": service.get("NoiThucHien", ""),
                "KhongHoTro": service.get("KhongHoTro", 0),
                "KhongThuTien": service.get("KhongThuTien", 0)
            })

        dich_vu_output = list(grouped_services.values())

        # 3. Xây dựng cấu trúc dữ liệu đầu ra (converted_data)
        converted_data = {
            'PhongKham': default_info['PhongKham'],
            'CSKH': default_info['CSKH'],

            'MaYTe': data_raw['ThongTinBenhNhan'].get('ma_y_te', ''),
            'BHYT': data_raw['ThongTinBenhNhan'].get('so_bhyt', ''),
            'MaDoiTuong': default_info['MaDoiTuong'],
            'DoiTuong': default_info['DoiTuong'],
            'HoTen': data_raw['ThongTinBenhNhan'].get('ho_ten', ''),
            'Tuoi': data_raw['ThongTinBenhNhan'].get('tuoi', ''),
            'GioiTinh': data_raw['ThongTinBenhNhan'].get('gioi_tinh', ''),
            'DiaChi': data_raw['ThongTinBenhNhan'].get('dia_chi', ''),
            'SDT': data_raw['ThongTinBenhNhan'].get('sdt', ''),

            'ChanDoan': data_raw['ThongTinPhongKham'].get('chan_doan', ''),
            'GhiChu': data_raw['ThongTinPhongKham'].get('ghi_chu', ''),
            'SoTien': tt_thanhtoan.get('TongThanhTienDV', '0'),
            'TongBenhNhanTra': tt_thanhtoan.get('TongBenhNhanTT', '0'),

            'NgayTao': default_info['NgayTao'],
            'TenBacSi': default_info['TenBacSi'],

            'DichVu': dich_vu_output
        }

        return converted_data

    def btn_in_phieu_handle(self):
        if not self.thong_tin_benh_nhan:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa chọn bệnh nhân chỉ định!")
            return
        data = self.get_thong_tin_dang_ky()
        if len(data.get('DichVu', [])) < 1:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa chọn dịch vụ chỉ định!")
            return

        # data_json = json.dumps(data, indent=4, ensure_ascii=False)
        write_json_lines(data, MODE_JSON.PHIEU_CHI_DINH_MODE)

        create_and_open_pdf_for_printing(data)

        # --- THÔNG BÁO HỎI RESET MÀN HÌNH ---
        # reply = QMessageBox.question(self, "Xác nhận",
        #                              f"Quay lại màn hình khám bệnh và reset bệnh nhân?",
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        # if reply == QMessageBox.StandardButton.Yes:
        #     self.reset_all()
        #     self.dich_vu_completed.emit()
    # </editor-fold>

    # <editor-fold desc="Load dữ liệu từ Service Bill (JSON)">
    def load_data_from_service_bill(self, data: dict):
        """
        Nhận dữ liệu service_bill (JSON) và đổ dữ liệu vào màn hình Đăng ký dịch vụ.
        Sử dụng lại logic load_thong_tin_benh_nhan và add_service_row để đảm bảo tính nhất quán.
        """
        if not data:
            return

        ui = self.ui_dich_vu

        # 1. Map dữ liệu JSON sang cấu trúc chuẩn mà load_thong_tin_benh_nhan mong đợi
        # JSON keys (bên trái) có thể khác với keys màn hình dịch vụ cần (bên phải)
        mapped_data = {
            'HoTenBN': data.get('HoTen', ''),
            'MaYTe': data.get('MaYTe', ''),
            'NgaySinh': data.get('NgaySinh', ''),
            'Tuoi': data.get('Tuoi', ''),
            'GioiTinh': data.get('GioiTinh', ''),
            'DiaChi': data.get('DiaChi', ''),
            'SoBHYT': data.get('BHYT', ''),  # Map từ BHYT -> SoBHYT
            'MaDoiTuong': data.get('MaDoiTuong', ''),
            'TenDoiTuong': data.get('DoiTuong', ''),
            'SDT': data.get('SDT', ''),

            # Thông tin chỉ định
            'TenBacSi': data.get('TenBacSi', ''),
            'PhongKham': data.get('PhongKham', ''),
            'ChanDoan': data.get('ChanDoan', ''),
            'GhiChu': data.get('GhiChu', ''),
            'NgayGioKham': datetime.now().strftime("%d/%m/%Y %H:%M:%S")  # Lấy giờ hiện tại hoặc từ data nếu có
        }

        # 2. Gọi hàm load thông tin chung (như AppController làm)
        # Hàm này sẽ set text các ô hành chính, set combobox đối tượng, phòng khám...
        self.load_thong_tin_benh_nhan(mapped_data)

        # 3. Load danh sách dịch vụ
        self.delete_all_rows()  # Xóa bảng cũ

        service_groups = data.get('DichVu', [])

        # Duyệt qua từng nhóm dịch vụ
        for group in service_groups:
            services = group.get('DSDichVu', [])

            # Duyệt qua từng dịch vụ trong nhóm
            for svc in services:
                # Lấy dữ liệu từ JSON
                ma_dv = str(svc.get('MaDichVu', ''))
                ma_loai_gia = str(svc.get('MaLoaiGia', ''))
                so_luong = str(svc.get('SoLuong', '1'))

                # Checkbox states (JSON lưu 0/1 hoặc true/false -> convert sang bool)
                is_khong_thu = True if str(svc.get('KhongThuTien', '0')) == '1' else False
                is_khong_ho_tro = True if str(svc.get('KhongHoTro', '0')) == '1' else False

                # --- GIẢ LẬP QUY TRÌNH NHẬP LIỆU CỦA NGƯỜI DÙNG ---

                # B1: Điền mã dịch vụ vào ô input
                ui.ma_dich_vu.setText(ma_dv)

                # B2: Gọi hàm search để load thông tin dịch vụ (Tên, DS Loại giá tương ứng)
                # Việc này quan trọng để Combobox Loại giá có dữ liệu đúng cho dịch vụ này
                self.search_dich_vu_by_id(mode=SEARCH_BY_INPUT_CODE)

                # B3: Chọn lại Loại giá theo đúng dữ liệu trong JSON
                # (Vì hàm search ở trên mặc định chọn loại giá đầu tiên)
                index_lg = ui.cb_loai_gia.findData(ma_loai_gia)
                if index_lg != -1:
                    ui.cb_loai_gia.setCurrentIndex(index_lg)
                    # Cập nhật lại đơn giá trên UI theo loại giá vừa chọn
                    self.update_don_gia_dich_vu()

                    # B4: Điền số lượng
                ui.so_luong.setText(so_luong)

                # B5: Set trạng thái các checkbox trên UI
                ui.is_khong_thu_tien.setChecked(is_khong_thu)
                ui.is_khong_ho_tro.setChecked(is_khong_ho_tro)

                # B6: Tính toán lại thành tiền trên UI (để add_service_row lấy đúng giá trị)
                self.calculate_thanh_tien()

                # B7: Gọi hàm thêm dòng (sẽ tự động validate, tính toán BHYT, format tiền tệ và reset input)
                # Sử dụng mode ADD_FROM_SEARCHBOX hoặc ADD_FROM_TREE_ITEM đều được,
                # ở đây dùng SEARCHBOX để tận dụng logic validate đầy đủ.
                self.add_service_row(mode=ADD_FROM_SEARCHBOX)

    # </editor-fold>