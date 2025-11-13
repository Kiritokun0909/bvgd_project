import json

import pandas as pd
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
from app.styles.styles import ADD_BTN_STYLE, DELETE_BTN_STYLE, COMPLETER_THUOC_STYLE
from app.ui.TabDichVu import Ui_formDichVu
from app.utils.cong_thuc_tinh_bhyt import tinh_tien_mien_giam
from app.utils.convert_data import convert_benhnhan_data
from app.utils.utils import (
    convert_to_unsigned,
    filter_data_by_foreign_key,
    format_currency_vn,
    get_first_row_data,
    load_data_from_csv,
    populate_combobox,
    populate_df_to_combobox,
    unformat_currency_to_float,
)


class DangKyDichVuTabController(QtWidgets.QWidget):
    dich_vu_completed = QtCore.pyqtSignal()

    # <editor-fold desc="Khoi tao man hinh dang ky dich vu">
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.thong_tin_benh_nhan = None
        self.ma_nhom_dv = None
        self.added_dich_vu_ids = set()  # list services_id add to table

        # <editor-fold desc="Load data dich vu, danh muc">
        self.ds_dich_vu_df = load_data_from_csv(DICH_VU_FILE_PATH)
        self.ds_danh_muc_df = load_data_from_csv(DANH_MUC_FILE_PATH)
        self._create_combined_search_column()

        self.ds_doi_tuong_loai_gia_df = load_data_from_csv(DOI_TUONG_LOAI_GIA_FILE_PATH)
        self.don_gia_df = load_data_from_csv(DON_GIA_FILE_PATH)
        self.loai_gia_df = load_data_from_csv(LOAI_GIA_FILE_PATH)
        # </editor-fold>

        # <editor-fold desc="Init UI">
        # Khởi tạo UI
        self.ui_dich_vu = Ui_formDichVu()
        self.ui_dich_vu.setupUi(tab_widget_container)
        self.ui_dich_vu.so_luong.setValidator(QtGui.QIntValidator())
        # </editor-fold>

        # <editor-fold desc="Init model search completer">
        self.service_model = QtCore.QStringListModel()
        self.service_completer = QtWidgets.QCompleter(self.service_model, self)
        self.service_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.service_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        self.search_timer = QtCore.QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_service_search)
        self.current_search_text = ""
        self._search_mode = ""

        self.ui_dich_vu.ma_dich_vu.setCompleter(self.service_completer)
        self.ui_dich_vu.ten_dich_vu.setCompleter(self.service_completer)
        # </editor-fold>

        # <editor-fold desc="Load data, connect signals,...">
        self.first_load_data()
        self.setup_table_dich_vu()
        self.connect_signals()
        self.apply_stylesheet()

        self.update_cay_dich_vu()  # Lần gọi đầu tiên sẽ set header label
        # </editor-fold>

    # </editor-fold>

    # <editor-fold desc="Reset & Load thong tin lan dau khi khoi tao man hinh">
    def reset_thong_tin_bn(self):
        self.ui_dich_vu.ho_ten_bn.clear()
        self.ui_dich_vu.dia_chi.clear()
        self.ui_dich_vu.gioi_tinh.clear()
        self.ui_dich_vu.tuoi.clear()
        self.ui_dich_vu.nam_sinh.clear()
        self.ui_dich_vu.nghe_nghiep.clear()
        self.thong_tin_benh_nhan = None

    def first_load_data(self):
        ui = self.ui_dich_vu

        populate_combobox(ui.cb_noi_yeu_cau, 'TenPhong', 'MaPhong', PHONG_KHAM_FILE_PATH)
        populate_combobox(ui.cb_noi_thuc_hien, 'TenPhong', 'MaPhong', PHONG_KHAM_FILE_PATH)
        populate_combobox(ui.cb_nhom_dich_vu, COL_TEN_DANH_MUC_HEADER, COL_MA_DANH_MUC_HEADER, DANH_MUC_FILE_PATH)
        populate_combobox(ui.cb_doi_tuong, 'TenDT', 'MaDT', DOI_TUONG_FILE_PATH)
        self.set_loai_gia()

        self.reset_thong_tin_bn()

    # </editor-fold>

    # <editor-fold desc="Load thong tin benh nhan tu man hinh kham benh">
    def set_thong_tin_benh_nhan(self, benh_nhan: dict):
        ui = self.ui_dich_vu

        ui.ho_ten_bn.setText(benh_nhan.get('HoTenBN', 'N/A'))
        ui.nam_sinh.setText(benh_nhan.get('NgaySinh', 'N/A'))
        ui.tuoi.setText(benh_nhan.get('Tuoi', 'N/A'))
        ui.gioi_tinh.setText(benh_nhan.get('GioiTinh', 'N/A'))
        ui.dia_chi.setText(benh_nhan.get('DiaChi', 'N/A'))

        ma_dt = benh_nhan.get('MaDoiTuong', '')
        index = ui.cb_doi_tuong.findData(ma_dt)
        if index != -1:
            ui.cb_doi_tuong.setCurrentIndex(index)
        else:
            ui.cb_doi_tuong.setCurrentText(benh_nhan.get('TenDoiTuong', 'N/A'))

    def set_thong_tin_chi_dinh(self, data):
        ui = self.ui_dich_vu

        # Cập nhật Bác sĩ chỉ định
        ui.bac_si_chi_dinh.setText(data.get('TenBacSi', 'N/A'))
        phong_kham = data.get('PhongKham', '')
        if phong_kham:
            index = self.ui_dich_vu.cb_noi_yeu_cau.findText(phong_kham)
            if index != -1:
                self.ui_dich_vu.cb_noi_yeu_cau.setCurrentIndex(index)
                self.ui_dich_vu.cb_noi_thuc_hien.setCurrentIndex(index)

        chan_doan = data.get('ChanDoan', '')
        self.ui_dich_vu.chan_doan.setText(chan_doan)

        # Cập nhật Ngày giờ yêu cầu
        dt_str = data.get('NgayGioKham', '')
        dt = QtCore.QDateTime.fromString(dt_str, "dd/MM/yyyy HH:mm:ss")
        if dt.isValid():
            ui.dateTimeEdit.setDateTime(dt)

    def set_loai_gia(self):
        # Lay ma doi tuong va loc danh sach loai gia cua ma doi tuong
        ma_doi_tuong = str(self.ui_dich_vu.cb_doi_tuong.currentData())
        filtered_df = self.ds_doi_tuong_loai_gia_df[
            self.ds_doi_tuong_loai_gia_df[DOI_TUONG_LOAI_GIA.COL_MA_DOI_TUONG_HEADER]
            .astype(str).str.contains(ma_doi_tuong, na=False)
        ]

        # Sap xep lai danh sach loai gia theo thu tu uu tien
        filtered_df = filtered_df.sort_values(by=DOI_TUONG_LOAI_GIA.ThuTuUuTien, ascending=True)
        res_df = pd.merge(filtered_df, self.loai_gia_df, on=LOAI_GIA.COL_MA_LOAI_GIA_HEADER, how='left')

        self.ui_dich_vu.cb_loai_gia.clear()

        populate_df_to_combobox(
            combobox=self.ui_dich_vu.cb_loai_gia,
            df=res_df,
            display_col=LOAI_GIA.COL_TEN_LOAI_GIA_HEADER,
            key_col=LOAI_GIA.COL_MA_LOAI_GIA_HEADER
        )

    def load_thong_tin_benh_nhan(self, data: dict):
        if not data:
            print("--- dk_dich_vu_controller: load_thong_tin_benh_nhan() ---")
            print("Lỗi: Không có dữ liệu bệnh nhân từ màn hình khám bệnh.")
            return

        self.thong_tin_benh_nhan = data

        self.set_thong_tin_benh_nhan(data)
        self.set_thong_tin_chi_dinh(data)
        self.set_loai_gia()

        # Đặt focus vào nơi cần nhập liệu tiếp theo
        self.ui_dich_vu.ma_dich_vu.setFocus()

    # </editor-fold>

    # <editor-fold desc="Setup table dich vu">
    def setup_table_dich_vu(self):
        table = self.ui_dich_vu.table_dich_vu

        table.horizontalHeader().setMinimumHeight(50)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter |
                                                     Qt.TextFlag.TextWordWrap)

        # Thiet lap so cot va labels
        self.ui_dich_vu.table_dich_vu.setColumnCount(DICH_VU_COL_COUNT)
        self.ui_dich_vu.table_dich_vu.setHorizontalHeaderLabels(HEADER_DICH_VU)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_MA_NHOM_DV, True)

        # Thiet lap chieu rong cho cac cot
        for i in range(len(HEADER_DICH_VU)):
            table.setColumnWidth(i, 80)

        # self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_DON_GIA_DOANH_THU, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        # self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_THANH_TIEN_DOANH_THU, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        # self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_BH_TT, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        # self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_BN_TT, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_TEN_DV, COL_SERVICE_TABLE_DEFAULT_WIDTH * 2)

        self.update_table_dich_vu_row_number()

    # </editor-fold>

    # <editor-fold desc="Create cot ket hop ten thuong va ten khong dau de search">
    def _create_combined_search_column(self):
        """
        Tạo một cột kết hợp:
        (Tên DV có dấu) + " | " + (Tên DV không dấu, chữ thường)
        """
        df = self.ds_dich_vu_df

        df[SERVICE_SEARCH_COLUMN] = (
                df[SERVICE_NAME_COLUMN].astype(str).str.lower() +
                " | " +
                df[SERVICE_TEN_KHONG_DAU_COLUMN].astype(str)
        )
        self.ds_dich_vu_df = df

    # </editor-fold>

    # <editor-fold desc="Setup event cho cac vung nhap lieu va cac nut">
    def connect_signals(self):
        ui = self.ui_dich_vu

        ui.ten_dich_vu.textEdited.connect(lambda text: self._start_service_autocomplete(text))
        ui.ma_dich_vu.textEdited.connect(self.search_dich_vu_by_id)

        ui.cb_nhom_dich_vu.currentIndexChanged.connect(self.update_cay_dich_vu)
        ui.list_dich_vu.cellClicked.connect(self.handle_tree_item_one_clicked)
        ui.list_dich_vu.cellDoubleClicked.connect(self._add_service_row)

        self.service_completer.activated.connect(self._load_service_details_from_completer)

        ui.cb_doi_tuong.currentIndexChanged.connect(self.set_loai_gia)
        ui.cb_loai_gia.currentIndexChanged.connect(self.update_don_gia_dich_vu)
        ui.cb_loai_gia.currentIndexChanged.connect(self.calculate_thanh_tien)
        ui.so_luong.textEdited.connect(self.calculate_thanh_tien)
        ui.don_gia.textEdited.connect(self.calculate_thanh_tien)

        ui.table_dich_vu.cellClicked.connect(self._handle_table_cell_clicked)

        ui.so_luong.returnPressed.connect(self.btn_them_handle)
        ui.btn_them.clicked.connect(self.btn_them_handle)
        ui.btn_huy.clicked.connect(self._clear_input_fields)
        ui.btn_in_phieu.clicked.connect(self.btn_in_phieu_handle)
        ui.btn_reset_all.clicked.connect(self.reset_all)

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

        self.ui_dich_vu.cb_nhom_dich_vu.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_doi_tuong.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_loai_gia.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_noi_yeu_cau.setStyleSheet(COMPLETER_THUOC_STYLE)
        self.ui_dich_vu.cb_noi_thuc_hien.setStyleSheet(COMPLETER_THUOC_STYLE)

    # </editor-fold>

    # <editor-fold desc="Calculate thành tiền">
    def calculate_thanh_tien(self):
        """Tính toán thành tiền: Đơn giá x Số lượng."""
        ui = self.ui_dich_vu
        try:
            don_gia = float(ui.don_gia.text().replace(',', ''))
            so_luong = int(ui.so_luong.text())
            thanh_tien = don_gia * so_luong
            ui.thanh_tien.setText(f"{thanh_tien:.3f}")
        except ValueError:
            ui.thanh_tien.setText("0")

    # </editor-fold>

    # <editor-fold desc="Search dich vu by id ">
    def search_gia_dich_vu(self, ma_dich_vu: str, ma_loai_gia: str):
        don_gia_df = self.don_gia_df

        condition = (
            (don_gia_df[DON_GIA.COL_MA_LOAI_GIA_HEADER] == ma_loai_gia) &
            (don_gia_df[DON_GIA.COL_MA_DICH_VU_HEADER] == ma_dich_vu)
        )

        don_gia_df = don_gia_df[condition]

        if len(don_gia_df) < 1:
            return 0

        don_gia_df = get_first_row_data(don_gia_df)
        don_gia = don_gia_df.get(DON_GIA.COL_DON_GIA_HEADER, '')
        return don_gia

    def set_thong_tin_dich_vu(self, dich_vu: dict):
        if dich_vu:
            self.ma_nhom_dv = str(dich_vu.get('MaDanhMuc'))
            self.ui_dich_vu.ten_dich_vu.setText(str(dich_vu.get('TenDichVu')))
            self.ui_dich_vu.ma_dich_vu.setText(str(dich_vu.get('MaDichVu')))

            don_gia = self.search_gia_dich_vu(
                self.ui_dich_vu.ma_dich_vu.text(),
                self.ui_dich_vu.cb_loai_gia.currentData()
            )

            self.ui_dich_vu.don_gia.setText(str(don_gia))
            self.ui_dich_vu.so_luong.setText('1')
            self.calculate_thanh_tien()

    def search_dich_vu_by_id(self, dich_vu_id: str):
        filtered_df = filter_data_by_foreign_key(
            data_frame=self.ds_dich_vu_df,
            fk_key_value=dich_vu_id,
            fk_column_name=DICH_VU_ID_COLUMN
        )

        dich_vu = get_first_row_data(filtered_df)
        self.set_thong_tin_dich_vu(dich_vu)

    # </editor-fold>

    # <editor-fold desc="Search & Auto complete">
    def _start_service_autocomplete(self, text: str):
        """Bắt đầu đếm ngược Debounce cho tìm kiếm dịch vụ."""
        self.current_search_text = text.strip()
        search_len = len(self.current_search_text)
        self.search_timer.stop()

        if search_len <= SEARCHING_AFTER_NUM_OF_CHAR:
            self.service_model.setStringList([])
            self.service_completer.popup().hide()
            return

        self.search_timer.start(SEARCH_TIMEOUT)

    def _perform_service_search(self):
        """Thực hiện tìm kiếm thủ công và cập nhật model completer."""
        text = self.current_search_text
        if not text:
            return

        search_query = convert_to_unsigned(text)
        filtered_df = self.ds_dich_vu_df[
            self.ds_dich_vu_df[SERVICE_SEARCH_COLUMN]
            .astype(str).str.contains(search_query, na=False)
        ]

        display_list = filtered_df[SERVICE_SEARCH_COLUMN].head(50).astype(str).tolist()

        self.service_model.setStringList(display_list)

        if self.service_model.rowCount() > 0:
            self.service_completer.complete()
            self.service_completer.setCompletionPrefix(search_query)
            self.service_completer.popup().setStyleSheet(COMPLETER_THUOC_STYLE)
            self.service_completer.popup().show()
        else:
            self.service_completer.popup().hide()

    # </editor-fold>

    # <editor-fold desc="Update cay dich vu theo ma nhom dich vu">
    def update_cay_dich_vu(self):
        """Cập nhật QTreeWidget khi thay đổi nhóm dịch vụ và thay đổi tiêu đề cột."""
        ui = self.ui_dich_vu
        table = ui.list_dich_vu

        table.blockSignals(True)
        table.clear()
        table.setRowCount(0)


        self.ui_dich_vu.list_dich_vu.verticalHeader().setVisible(False)

        # 1. Lấy TÊN và MÃ danh mục
        ten_danh_muc = ui.cb_nhom_dich_vu.currentText()
        ma_danh_muc = ui.cb_nhom_dich_vu.currentData()

        # Tên cột (Header Label)
        new_header = ["", f"{ten_danh_muc}"]

        # 2. CẬP NHẬT TIÊU ĐỀ QTableWidget
        table.setColumnCount(len(new_header))  # Thiết lập lại số cột
        table.setHorizontalHeaderLabels(new_header)
        table.setColumnWidth(TREE_COL_DICH_VU_CHECKBOX, 45)  # Cột 0: Checkbox
        table.horizontalHeader().setSectionResizeMode(TREE_COL_DICH_VU, QtWidgets.QHeaderView.ResizeMode.Stretch) # Cột 1: Tên dịch vụ

        if ma_danh_muc:
            # 3. Lọc dịch vụ theo Mã danh mục
            filtered_df = self.ds_dich_vu_df[
                self.ds_dich_vu_df[SERVICE_CAT_COLUMN].astype(str) == str(ma_danh_muc)
            ]

            # 4. Đổ dữ liệu vào QTableWidget
            for index, row in filtered_df.iterrows():
                ten_dich_vu = str(row[DICH_VU_NAME_COLUMN])
                ma_dich_vu = str(row[DICH_VU_ID_COLUMN])

                # Thêm dòng mới vào bảng
                current_row = table.rowCount()
                table.insertRow(current_row)

                # Cột 0: checkbox dich vu
                is_checked = ma_dich_vu in self.added_dich_vu_ids

                # Tạo checkbox widget, kết nối tín hiệu changed (clicked)
                checkbox_widget = self._create_checkbox_list_danh_muc(
                    is_checked=is_checked,
                    ma_dich_vu=ma_dich_vu
                )
                table.setCellWidget(current_row, TREE_COL_DICH_VU_CHECKBOX, checkbox_widget)

                # Cột 1: ten dich vu
                item_ten_dv = QTableWidgetItem(ten_dich_vu)
                # Đặt Mã dịch vụ vào UserRole của QTableWidgetItem (để lấy khi click)
                item_ten_dv.setData(QtCore.Qt.ItemDataRole.UserRole, ma_dich_vu)
                # Chỉ cho phép chọn/click, không cho chỉnh sửa nội dung cell
                item_ten_dv.setFlags(item_ten_dv.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(current_row, TREE_COL_DICH_VU, item_ten_dv)

            # table.expandAll() # Bỏ vì không áp dụng cho QTableWidget
            table.blockSignals(False)

    # </editor-fold>

    # <editor-fold desc="Xu ly nguoi dung one-click vao dich vu trong cay danh muc">
    def handle_tree_item_one_clicked(self, row, column):
        """Xử lý khi người dùng click vào một dịch vụ trong QTableWidget (list danh mục)."""
        table = self.ui_dich_vu.list_dich_vu
        item = table.item(row, TREE_COL_DICH_VU)  # Lấy item ở cột Tên DV

        if not item:
            return

        ma_dich_vu = item.data(QtCore.Qt.ItemDataRole.UserRole)

        if ma_dich_vu:
            self.search_dich_vu_by_id(ma_dich_vu)

    def _add_service_row_from_list(self, row, column):
        """Xử lý khi người dùng double click vào dịch vụ trong QTableWidget (list danh mục)."""
        table = self.ui_dich_vu.list_dich_vu
        item = table.item(row, TREE_COL_DICH_VU)  # Lấy item ở cột Tên DV

        if not item:
            return

        ma_dich_vu = item.data(QtCore.Qt.ItemDataRole.UserRole)

        if ma_dich_vu:
            # 1. Tải thông tin DV vào ô nhập liệu
            self.search_dich_vu_by_id(ma_dich_vu)

            # 2. Add DV vào bảng chính (logic tương tự như ấn nút 'Thêm')
            self._add_service_row(ADD_FROM_TREE_ITEM)

            # 3. Cập nhật checkbox
            # Cần tìm checkbox widget và set trạng thái Checked
            checkbox_widget = table.cellWidget(row, TREE_COL_DICH_VU_CHECKBOX)
            if checkbox_widget:
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(True)

    # </editor-fold>

    # <editor-fold desc="Validate data truoc khi add vao table dich vu">
    def validate_service_row(self, mode=None):
        """
        Kiểm tra tính hợp lệ của dữ liệu dịch vụ từ các ô nhập liệu.
        """
        ui = self.ui_dich_vu

        ma_dv = ui.ma_dich_vu.text().strip()

        if ma_dv in self.added_dich_vu_ids:
            QMessageBox.warning(self, "Dịch vụ đã tồn tại",
                                f"Dịch vụ có mã {ma_dv} đã được thêm vào bảng.")
            return False

        # Neu dang add tu cay danh muc thi khong can kiem tra them
        if mode == ADD_FROM_TREE_ITEM:
            return True

        if not ma_dv:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng nhập Mã dịch vụ.")
            return False

        ten_dv = ui.ten_dich_vu.text().strip()
        don_gia_str = ui.don_gia.text().strip()
        so_luong_str = ui.so_luong.text().strip()

        if not ten_dv or not don_gia_str or not so_luong_str:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng kiểm tra đầy đủ tên dịch vụ, đơn giá và số lượng.")
            return False

        # Kiểm tra giá trị hợp lệ (Ví dụ: Số lượng phải > 0)
        if int(so_luong_str) <= 0:
            QMessageBox.warning(self, "Lỗi giá trị",
                                "Số lượng không thể bé hơn 0.")
            return False

        return True

    # </editor-fold>

    # <editor-fold desc="Them dich vu">
    def _add_service_row(self, mode=ADD_FROM_TREE_ITEM):
        """Thêm dịch vụ từ các ô nhập liệu vào table_dich_vu."""
        ui = self.ui_dich_vu
        table = ui.table_dich_vu

        if not self.validate_service_row(mode):
            return

        dich_vu_id = ui.ma_dich_vu.text().strip()
        filter_dv_df = filter_data_by_foreign_key(
            data_frame=self.ds_dich_vu_df,
            fk_key_value=dich_vu_id,
            fk_column_name=DICH_VU_ID_COLUMN
        )
        dich_vu = get_first_row_data(filter_dv_df)
        ten_dv = dich_vu.get(DICH_VU_NAME_COLUMN, '')

        thanh_tien = ui.thanh_tien.text().strip()
        bao_hiem_thanh_toan = "0"
        benh_nhan_thanh_toan = str(float(thanh_tien) - float(bao_hiem_thanh_toan))

        is_khong_thu_tien = ui.is_khong_thu_tien.isChecked()
        is_khong_ho_tro = ui.is_khong_ho_tro.isChecked()
        is_chon_in = True  # Mặc định chọn in khi thêm

        # 3. Chuẩn bị dữ liệu cho dòng mới
        new_row_data = {
            COL_MA_DV: ui.ma_dich_vu.text().strip(),
            COL_MA_NHOM_DV: ui.cb_nhom_dich_vu.currentData() if mode == ADD_FROM_TREE_ITEM else self.ma_nhom_dv,
            COL_TEN_DV: ten_dv,
            COL_DON_GIA_DOANH_THU: format_currency_vn(ui.don_gia.text().strip()),
            COL_SO_LUONG: ui.so_luong.text().strip(),
            COL_THANH_TIEN_DOANH_THU: format_currency_vn(ui.thanh_tien.text().strip()),
            COL_TY_LE_TT: ui.cb_ty_le.currentText(),
            COL_LOAI_GIA: ui.cb_loai_gia.currentText(),
            COL_NOI_THUC_HIEN: ui.cb_noi_thuc_hien.currentText(),
            COL_BH_TT: format_currency_vn(bao_hiem_thanh_toan),
            COL_BN_TT: format_currency_vn(benh_nhan_thanh_toan),
            COL_SO_PHIEU: '',
            COL_LY_DO_KHONG_THU: '',
        }

        # 4. Thêm dòng mới vào bảng (thêm vào cuối)
        current_row_count = table.rowCount()
        table.insertRow(current_row_count)

        # 5. Đổ dữ liệu vào các cột
        for col, value in new_row_data.items():
            if col not in [COL_KHONG_THU_TIEN, COL_KHONG_HO_TRO, COL_CHON_IN, COL_HUY]:
                item = QTableWidgetItem(str(value))
                # Tùy chỉnh read-only cho các cột (ví dụ: Mã, Đơn giá, Thành tiền)
                if col not in [COL_SO_PHIEU, COL_LY_DO_KHONG_THU]:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(current_row_count, col, item)

        # 6. Thêm Checkbox và Nút Xóa (Widgets)
        table.setCellWidget(
            current_row_count,
            COL_KHONG_THU_TIEN,
            self._create_checkbox_widget(is_khong_thu_tien, self.update_table_dich_vu_row_number)
        )
        table.setCellWidget(
            current_row_count,
            COL_KHONG_HO_TRO,
            self._create_checkbox_widget(is_khong_ho_tro, self.update_table_dich_vu_row_number)
        )
        table.setCellWidget(current_row_count, COL_CHON_IN, self._create_checkbox_widget(is_chon_in))
        table.setCellWidget(current_row_count, COL_HUY, self._create_delete_button_widget(dich_vu_id))

        self.update_table_dich_vu_row_number()
        self._clear_input_fields()
        self.added_dich_vu_ids.add(dich_vu_id)

        self._set_list_danh_muc_checkbox_state(dich_vu_id, True)

        ui.ma_dich_vu.setFocus()

    def _set_list_danh_muc_checkbox_state(self, ma_dich_vu: str, is_checked: bool):
        """Cập nhật trạng thái checkbox trong QTableWidget list_danh_muc."""
        table = self.ui_dich_vu.list_dich_vu

        for row in range(table.rowCount()):
            item = table.item(row, TREE_COL_DICH_VU)
            if item and item.data(QtCore.Qt.ItemDataRole.UserRole) == ma_dich_vu:
                widget = table.cellWidget(row, TREE_COL_DICH_VU_CHECKBOX)
                if widget:
                    checkbox = widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(is_checked)
                        return

    # </editor-fold>

    # <editor-fold desc="Xoa dich vu">
    def _find_row_by_ma_dich_vu(self, ma_dich_vu: str) -> int:
        table = self.ui_dich_vu.table_dich_vu

        for row in range(table.rowCount()):
            item = table.item(row, COL_MA_DV)
            if item and item.text() == ma_dich_vu:
                return row

        return -1

    def _delete_dich_vu_by_id(self, ma_dich_vu: str):
        table = self.ui_dich_vu.table_dich_vu
        row_index = self._find_row_by_ma_dich_vu(ma_dich_vu)

        if row_index == -1:
            QMessageBox.warning(self, "Lỗi",
                                f"Không tìm thấy dịch vụ có mã {ma_dich_vu} trong bảng.")
            return

        reply = QMessageBox.question(self, "Xác nhận",
                                     f"Bạn có chắc muốn hủy dịch vụ có mã {ma_dich_vu}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            table.removeRow(row_index)
            self.update_table_dich_vu_row_number()

            if ma_dich_vu in self.added_dich_vu_ids:
                self.added_dich_vu_ids.remove(ma_dich_vu)
                self._set_list_danh_muc_checkbox_state(ma_dich_vu, False)

    def _delete_all_rows(self):
        table = self.ui_dich_vu.table_dich_vu
        num_rows = table.rowCount()
        while num_rows > 1:
            table.removeRow(0)
            num_rows -= 1

        self.added_dich_vu_ids.clear()
        self.update_table_dich_vu_row_number()
        self.update_cay_dich_vu()

    # </editor-fold>

    # <editor-fold desc="Tao widget chua nut xoa dong dich vu">
    def _create_delete_button_widget(self, dich_vu_id: str):
        """Tạo widget chứa nút 'Xóa' cho QTableWidget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        btn_delete = QPushButton("Xóa")
        btn_delete.setStyleSheet(DELETE_BTN_STYLE)

        # Liên kết tín hiệu clicked với hàm _delete_service_row
        # Cần truyền tham chiếu của widget container (widget) để tìm ra dòng
        btn_delete.clicked.connect(lambda: self._delete_dich_vu_by_id(dich_vu_id))

        layout.addWidget(btn_delete)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    # </editor-fold>

    # <editor-fold desc="Xu ly khi nguoi dung check hoac uncheck checkbox dich vu o cay dich vu ">
    def _create_checkbox_list_danh_muc(self, is_checked: bool, ma_dich_vu: str):
        """Tạo QCheckBox widget cho cột 'Chọn' trong list_danh_muc QTableWidget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        checkbox = QCheckBox()
        checkbox.setChecked(is_checked)

        # Connect signal đến hàm xử lý check/uncheck
        checkbox.clicked.connect(lambda state: self._handle_list_danh_muc_check_state_changed(state, ma_dich_vu))

        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget

    def _handle_list_danh_muc_check_state_changed(self, is_checked: bool, ma_dich_vu: str):
        """Xử lý khi người dùng check/uncheck dịch vụ trong QTableWidget (list danh mục)."""
        # Lưu ý: is_checked ở đây là boolean state (True/False) của checkbox.

        if not ma_dich_vu:
            return

        if is_checked:
            if ma_dich_vu not in self.added_dich_vu_ids:
                self.search_dich_vu_by_id(ma_dich_vu)
                # Tự động add dịch vụ sau khi check, nếu cần
                self._add_service_row(ADD_FROM_TREE_ITEM)
                self.ui_dich_vu.ma_dich_vu.setFocus()
        else:
            if ma_dich_vu in self.added_dich_vu_ids:
                self._delete_dich_vu_by_id(ma_dich_vu)

    # </editor-fold>

    # <editor-fold desc="Xu ly khi nguoi dung chon dich vu trong phan tim kiem theo ten">
    def _load_service_details_from_completer(self, text: str):
        """Load chi tiết dịch vụ khi chọn từ QCompleter (Activated)."""
        search_col = SERVICE_SEARCH_COLUMN

        # Lọc DataFrame để tìm dịch vụ
        filtered_df = self.ds_dich_vu_df[
            self.ds_dich_vu_df[search_col].astype(str).str.lower() == text.lower()
        ]

        if filtered_df.empty:
            QMessageBox.warning(self, "Lỗi tìm kiếm", "Không tìm thấy dịch vụ tương ứng.")
            return

        service_data = filtered_df.iloc[0]
        self.search_dich_vu_by_id(service_data[DICH_VU_ID_COLUMN])

    # </editor-fold>

    def _clear_input_fields(self):
        """Xóa nội dung các ô nhập liệu dịch vụ."""
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

    def _create_checkbox_widget(self, is_checked: bool, func=None):
        """Tạo QCheckBox widget cho các cột Boolean (Không thu tiền, Không hỗ trợ, Chọn in)."""
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

    def _handle_table_cell_clicked(self, row, col):
        """Xử lý sự kiện click vào cell trong bảng (để bắt lỗi click ngoài nút Xóa)."""
        # Nếu cột là cột Huỷ, sự kiện đã được _delete_service_row xử lý
        if col == COL_HUY:
            return

        # Các logic khác khi click vào cell (ví dụ: chỉnh sửa, focus) có thể thêm tại đây
        pass

    def get_checkbox_state(self, table, row: int, column: int) -> bool:
        """Lấy trạng thái (True/False) của QCheckBox trong QTableWidget."""
        # Lấy QWidget được đặt tại ô (row, column)
        widget = table.cellWidget(row, column)

        if widget:
            # Giả định QWidget chứa một QHBoxLayout, và QCheckBox là widget đầu tiên
            # Phải truy cập trực tiếp vào QCheckBox bên trong QWidget
            layout = widget.layout()
            if layout and layout.count() > 0:
                checkbox = layout.itemAt(0).widget()
                return checkbox.isChecked()
        return False

    # <editor-fold desc="TÍNH THÀNH TIỀN, BẢO HIỂM THANH TOÁN, BỆNH NHÂN THANH TOÁN">
    def _calculate_table_summary(self) -> dict:
        """Tính tổng Thành tiền, Bảo hiểm thanh toán, Bệnh nhân thanh toán từ các dòng dịch vụ."""
        table = self.ui_dich_vu.table_dich_vu
        ma_doi_tuong = self.ui_dich_vu.cb_doi_tuong.currentData()
        total_thanh_tien = 0.0
        total_thanh_tien_huong_bao_hiem = 0.0

        # Xác định số dòng dịch vụ (loại trừ dòng tổng nếu đã tồn tại)
        max_row = table.rowCount()
        if (max_row > 0 and
                table.verticalHeaderItem(max_row - 1) and
                table.verticalHeaderItem(max_row - 1).text() == "TỔNG"):
            max_row -= 1

        # Tinh tong thanh tien dich vu
        for row in range(max_row):
            is_checked_khong_thu_tien = self.get_checkbox_state(table, row, COL_KHONG_THU_TIEN)
            is_checked_khong_ho_tro = self.get_checkbox_state(table, row, COL_KHONG_HO_TRO)

            item_thanh_tien = table.item(row, COL_THANH_TIEN_DOANH_THU)
            # Không thu tiền thì thành tiền doanh thu dịch vụ đó = 0
            if is_checked_khong_thu_tien:
                item_thanh_tien.setText(format_currency_vn(0))
                continue

            item_don_gia = unformat_currency_to_float(table.item(row, COL_DON_GIA_DOANH_THU).text())
            item_so_luong = unformat_currency_to_float(table.item(row, COL_SO_LUONG).text())
            thanh_tien = item_don_gia * item_so_luong
            item_thanh_tien.setText(format_currency_vn(thanh_tien))
            total_thanh_tien += thanh_tien

            # Không hỗ trợ thì không tính vào tổng tiền hưởng BHYT
            if not is_checked_khong_ho_tro:
                total_thanh_tien_huong_bao_hiem += thanh_tien

        # Tinh bao hiem thanh toan va benh nhan thanh toan
        total_bao_hiem_thanh_toan = 0.0
        total_benh_nhan_thanh_toan = 0.0

        for row in range(max_row):
            is_checked_khong_ho_tro = self.get_checkbox_state(table, row, COL_KHONG_HO_TRO)
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

    # </editor-fold>

    # <editor-fold desc="Cập nhật thứ tự dòng và dòng tính tổng cuối cùng cho table dich vu">
    def _update_table_summary_row(self):
        """Hiển thị và cập nhật dòng tổng kết cuối cùng của bảng dịch vụ."""
        table = self.ui_dich_vu.table_dich_vu
        summary_data = self._calculate_table_summary()
        row_count = table.rowCount()

        # 1. Thêm dòng mới vào cuối bảng (vị trí mới cho dòng tổng)
        table.insertRow(row_count)
        new_summary_row_index = row_count

        # 2. Thiết lập tiêu đề dòng (Vertical Header) là "TỔNG"
        total_header = QtWidgets.QTableWidgetItem("TỔNG")
        table.setVerticalHeaderItem(new_summary_row_index, total_header)

        # 3. Gộp ô cho nhãn "Tổng cộng" và định dạng label
        # Gộp từ cột 0 đến cột trước cột Thành tiền
        table.setSpan(new_summary_row_index, 0, 1, COL_THANH_TIEN_DOANH_THU)
        item_label = QTableWidgetItem("TỔNG CỘNG:")
        item_label.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        item_label.setFlags(item_label.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(new_summary_row_index, 0, item_label)

        # 4. Thiết lập dữ liệu và định dạng cho các cột tổng
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
        """Đánh số lại các dòng dữ liệu (Vertical Header) của các dịch vụ (bỏ qua dòng TỔNG)."""
        table = self.ui_dich_vu.table_dich_vu
        row_count = table.rowCount()

        for row in range(table.rowCount(), -1, -1):
            item = table.item(row, COL_MA_DV)
            if item and item.text():
                if item.text() == 'TỔNG CỘNG:':
                    table.removeRow(row)
                    break

        # Đánh số các dòng dịch vụ (bắt đầu từ 1)
        for i in range(row_count):
            item = QtWidgets.QTableWidgetItem(str(i + 1))
            table.setVerticalHeaderItem(i, item)

        self._update_table_summary_row()
    # </editor-fold>

    def update_don_gia_dich_vu(self):
        ma_dich_vu = self.ui_dich_vu.ma_dich_vu.text()
        ma_loai_gia = self.ui_dich_vu.cb_loai_gia.currentData()
        if not ma_dich_vu:
            return

        gia_dv = self.search_gia_dich_vu(ma_dich_vu, ma_loai_gia)
        self.ui_dich_vu.don_gia.setText(str(gia_dv))

    def btn_them_handle(self):
        self._add_service_row(mode=ADD_FROM_SEARCHBOX)

    # <editor-fold desc="Handle nut in phieu">
    def get_thong_tin_dang_ky(self):
        ui = self.ui_dich_vu
        data = dict()

        data['ThongTinBenhNhan'] = {
            'ma_y_te': self.thong_tin_benh_nhan.get('MaYTe', ''),
            'so_bhyt': self.thong_tin_benh_nhan.get('SoBHYT', ''),
            'doi_tuong': ui.cb_doi_tuong.currentText(),
            'ho_ten': ui.ho_ten_bn.text().strip(),
            'tuoi': ui.tuoi.text().strip(),
            'gioi_tinh': ui.gioi_tinh.text().strip(),
            'dia_chi': ui.dia_chi.text().strip(),
            'sdt': self.thong_tin_benh_nhan.get('SDT', ''),
        }

        data['ThongTinPhongKham'] = {
            'noi_yeu_cau': ui.cb_noi_yeu_cau.currentText(),
            'bac_si': '',
            'chan_doan': ui.chan_doan.text().strip(),
            'ghi_chu': ui.ghi_chu.text().strip(),
            'code_xn': ui.ma_code_xn.text().strip(),
            'so_tien': '',
        }

        dich_vu = []
        thanh_toan = {}
        table = ui.table_dich_vu
        for row in range(0, table.rowCount()):
            dich_vu_row_data = {}

            for col, header in enumerate(HEADER_DICH_VU):
                if col == COL_HUY:
                    continue

                field_name = FIELD_MAPPING.get(header, header)

                if col in [COL_KHONG_THU_TIEN, COL_KHONG_HO_TRO, COL_CHON_IN]:
                    is_checked = self.get_checkbox_state(table, row, col)
                    dich_vu_row_data[field_name] = 1 if is_checked else 0
                    continue

                item = table.item(row, col)
                dich_vu_row_data[field_name] = item.text().strip() if item else ''

            if dich_vu_row_data['MaDichVu'] == 'TỔNG CỘNG:':
                thanh_toan['TongThanhTienDV'] = dich_vu_row_data['TTDoanhThu']
                thanh_toan['TongBaoHiemTT'] = dich_vu_row_data['BaoHiemTT']
                thanh_toan['TongBenhNhanTT'] = dich_vu_row_data['BenhNhanTT']
                continue

            if dich_vu_row_data['ChonIn'] == 1:
                dich_vu.append(dich_vu_row_data)

        data['DichVuDangKy'] = dich_vu
        data['ThanhToan'] = thanh_toan

        return data

    def reset_all(self):
        self.reset_thong_tin_bn()
        ui = self.ui_dich_vu

        ui.bac_si_chi_dinh.clear()
        ui.chan_doan.clear()
        ui.ghi_chu.clear()
        ui.ma_code_xn.clear()

        self._delete_all_rows()

    def btn_in_phieu_handle(self):
        if not self.thong_tin_benh_nhan:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa chọn bệnh nhân chỉ định!")
            return

        data = self.get_thong_tin_dang_ky()
        if len(data['DichVuDangKy']) < 1:
            QMessageBox.warning(self, "Thiếu dữ liệu", "Chưa chọn dịch vụ chỉ định!")
            return

        # --- HIỂN THỊ DỮ LIỆU THU THẬP ĐƯỢC (ĐỂ TEST) ---
        # print("--- DỮ LIỆU FORM ĐÃ THU THẬP ---")
        # print(json.dumps(data, indent=4, ensure_ascii=False))
        # print("-----------------------------------")

        converted_data = convert_benhnhan_data(data, self.ds_danh_muc_df)
        print(json.dumps(converted_data, indent=4, ensure_ascii=False))

        create_and_open_pdf_for_printing(converted_data)

        reply = QMessageBox.question(self, "Xác nhận",
                                     f"Quay lại màn hình khám bệnh và reset bệnh nhân?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.reset_all()
            self.dich_vu_completed.emit()

    # </editor-fold>