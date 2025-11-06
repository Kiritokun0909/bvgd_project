from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QTableWidgetItem, QTreeWidgetItem, QMessageBox, QPushButton, QHBoxLayout, QWidget, QCheckBox
from PyQt6.QtCore import Qt, QPoint

from app.ui.TabDichVu import Ui_formDichVu
from app.utils.utils import populate_combobox, load_data_from_csv, filter_data_by_foreign_key, get_first_row_data, \
    convert_to_unsigned

from app.configs.table_dich_vu_configs import *


class DangKyDichVuTabController(QtWidgets.QWidget):

    # <editor-fold desc="Khoi tao man hinh dang ky dich vu">
    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        # <editor-fold desc="Load data dich vu, danh muc">
        self.ds_dich_vu_df = load_data_from_csv(DICH_VU_FILE_PATH)
        self.ds_danh_muc_df = load_data_from_csv(DANH_MUC_FILE_PATH)
        self._create_combined_search_column()
        # </editor-fold>

        self.ma_nhom_dv = None
        self.added_dich_vu_ids = set()    # list services_id add to table

        # <editor-fold desc="Init UI">
        # Khởi tạo UI
        self.ui_dich_vu = Ui_formDichVu()
        self.ui_dich_vu.setupUi(tab_widget_container)
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

        # Thiết lập QTreeWidget (Chỉ setColumnCount ở đây)
        self.ui_dich_vu.list_danh_muc.setColumnCount(2)
        self.update_cay_dich_vu()  # Lần gọi đầu tiên sẽ set header label
        # </editor-fold>
    # </editor-fold>


    # <editor-fold desc="Reset & Load thong tin lan dau khi khoi tao man hinh">
    def reset_thong_tin_bn(self):
        self.ui_dich_vu.ho_ten_bn.clear()
        self.ui_dich_vu.dia_chi.clear()
        self.ui_dich_vu.tuoi.clear()
        self.ui_dich_vu.nam_sinh.clear()
        self.ui_dich_vu.nghe_nghiep.clear()

    def first_load_data(self):
        ui = self.ui_dich_vu

        populate_combobox(ui.cb_noi_yeu_cau, 'TenPhong', 'MaPhong', PHONG_KHAM_FILE_PATH)
        populate_combobox(ui.cb_noi_thuc_hien, 'TenPhong', 'MaPhong', PHONG_KHAM_FILE_PATH)
        populate_combobox(ui.cb_nhom_dich_vu, 'TenDanhMuc', 'MaDanhMuc', DANH_MUC_FILE_PATH)
        populate_combobox(ui.cb_doi_tuong, 'TenDT', 'MaDT', DOI_TUONG_FILE_PATH)

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
        ui.nam_sinh.setText(benh_nhan.get('NgaySinh', 'N/A'))
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

    def load_thong_tin_benh_nhan(self, data: dict):
        if not data:
            print("--- dk_dich_vu_controller: load_thong_tin_benh_nhan() ---")
            print("Lỗi: Không có dữ liệu bệnh nhân từ màn hình khám bệnh.")
            return

        self.set_thong_tin_benh_nhan(data)
        self.set_thong_tin_chi_dinh(data)

        # Đặt focus vào nơi cần nhập liệu tiếp theo
        self.ui_dich_vu.ma_dich_vu.setFocus()

    # </editor-fold>


    # <editor-fold desc="Setup table dich vu">

    def setup_table_dich_vu(self):
        # Thiet lap so cot va labels
        self.ui_dich_vu.table_dich_vu.setColumnCount(DICH_VU_COL_COUNT)
        self.ui_dich_vu.table_dich_vu.setHorizontalHeaderLabels(HEADER_DICH_VU)
        self.ui_dich_vu.table_dich_vu.setColumnHidden(COL_MA_NHOM_DV, False)

        # Thiet lap chieu rong cho cac cot
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_DON_GIA_DOANH_THU, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_THANH_TIEN_DOANH_THU, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_BH_TT, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_BN_TT, COL_SERVICE_TABLE_DEFAULT_WIDTH)
        self.ui_dich_vu.table_dich_vu.setColumnWidth(COL_TEN_DV, COL_SERVICE_TABLE_DEFAULT_WIDTH * 2)

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
        ui.list_danh_muc.itemClicked.connect(self.handle_tree_item_one_clicked)
        ui.list_danh_muc.itemDoubleClicked.connect(self._add_service_row)
        ui.list_danh_muc.itemChanged.connect(self._handle_tree_item_check_state_changed)

        self.service_completer.activated.connect(self._load_service_details_from_completer)

        ui.so_luong.textEdited.connect(self.calculate_thanh_tien)
        ui.don_gia.textEdited.connect(self.calculate_thanh_tien)

        ui.table_dich_vu.cellClicked.connect(self._handle_table_cell_clicked)

        ui.btn_them.clicked.connect(self.btn_them_handler)
        ui.btn_huy.clicked.connect(self._clear_input_fields)

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

    # </editor-fold>


    # <editor-fold desc="Calculate thanh_tien">

    def calculate_thanh_tien(self):
        """Tính toán thành tiền: Đơn giá x Số lượng."""
        ui = self.ui_dich_vu
        try:
            don_gia = float(ui.don_gia.text().replace(',', ''))
            so_luong = int(ui.so_luong.text())
            thanh_tien = don_gia * so_luong
            ui.thanh_tien.setText(f"{thanh_tien:.3f}")  # Format không dấu phẩy, không thập phân
        except ValueError:
            ui.thanh_tien.setText("0")

    # </editor-fold>


    # <editor-fold desc="Search dich vu by id ">

    def set_thong_tin_dich_vu(self, dich_vu: dict):
        if dich_vu:
            self.ma_nhom_dv = str(dich_vu.get('MaDanhMuc'))
            self.ui_dich_vu.ten_dich_vu.setText(str(dich_vu.get('TenDichVu')))
            self.ui_dich_vu.ma_dich_vu.setText(str(dich_vu.get('MaDichVu')))
            self.ui_dich_vu.don_gia.setText(str(dich_vu.get('DonGia')))
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
            self.service_completer.popup().show()
        else:
            self.service_completer.popup().hide()

    # </editor-fold>


    # <editor-fold desc="Update cay dich vu theo ma nhom dich vu">
    def update_cay_dich_vu(self):
        """Cập nhật QTreeWidget khi thay đổi nhóm dịch vụ và thay đổi tiêu đề cột."""
        ui = self.ui_dich_vu
        ui.list_danh_muc.clear()

        # 1. Lấy TÊN và MÃ danh mục
        ten_danh_muc = ui.cb_nhom_dich_vu.currentText()
        ma_danh_muc = ui.cb_nhom_dich_vu.currentData()

        # 2. CẬP NHẬT TIÊU ĐỀ QTreeWidget
        new_header = ["Chọn", f"{ten_danh_muc}"]
        ui.list_danh_muc.setHeaderLabels(new_header)
        ui.list_danh_muc.setColumnWidth(TREE_COL_DICH_VU_CHECKBOX, 45)
        ui.list_danh_muc.setColumnWidth(TREE_COL_DICH_VU, 250)

        if ma_danh_muc:
            # 3. Lọc dịch vụ theo Mã danh mục
            filtered_df = self.ds_dich_vu_df[
                self.ds_dich_vu_df[SERVICE_CAT_COLUMN].astype(str) == str(ma_danh_muc)
            ]

            # 4. Đổ dữ liệu vào QTreeWidget
            for index, row in filtered_df.iterrows():
                ten_dich_vu = str(row[DICH_VU_NAME_COLUMN])
                ma_dich_vu = str(row[DICH_VU_ID_COLUMN])

                item = QTreeWidgetItem(ui.list_danh_muc)    # Khoi tao item them vao cay dich vu

                # Cot 0: checkbox dich vu
                is_checked = ma_dich_vu in self.added_dich_vu_ids
                item.setCheckState(TREE_COL_DICH_VU_CHECKBOX, Qt.CheckState.Checked if is_checked else Qt.CheckState.Unchecked)

                # Cot 1: ten dich vu
                item.setText(TREE_COL_DICH_VU, ten_dich_vu)

                # Luu ma dich vu cua dong item vao UserRole
                item.setData(TREE_COL_DICH_VU, QtCore.Qt.ItemDataRole.UserRole, ma_dich_vu)

            ui.list_danh_muc.expandAll()

    # </editor-fold>


    # <editor-fold desc="Xu ly nguoi dung one-click vao dich vu trong cay danh muc">
    def handle_tree_item_one_clicked(self, item: QTreeWidgetItem, column: int):
        """Xử lý khi người dùng click vào một dịch vụ trong QTreeWidget."""
        ma_dich_vu = item.data(TREE_COL_DICH_VU, QtCore.Qt.ItemDataRole.UserRole)

        if ma_dich_vu:
            self.search_dich_vu_by_id(ma_dich_vu)
    # </editor-fold>


    # <editor-fold desc="Validate data truoc khi add vao table dich vu">
    def validate_service_row(self, mode = None):
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


    # <editor-fold desc="Them dich vu moi vao table dich vu">
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
            COL_DON_GIA_DOANH_THU: ui.don_gia.text().strip(),
            COL_SO_LUONG: ui.so_luong.text().strip(),
            COL_THANH_TIEN_DOANH_THU: ui.thanh_tien.text().strip(),
            COL_TY_LE_TT: ui.cb_ty_le.currentText(),
            COL_LOAI_GIA: 'DVTT',
            COL_NOI_THUC_HIEN: ui.cb_noi_yeu_cau.currentText(),
            COL_BH_TT: bao_hiem_thanh_toan,
            COL_BN_TT: benh_nhan_thanh_toan,
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
                if col in [COL_MA_DV, COL_DON_GIA_DOANH_THU, COL_THANH_TIEN_DOANH_THU]:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(current_row_count, col, item)

        # 6. Thêm Checkbox và Nút Xóa (Widgets)
        table.setCellWidget(current_row_count, COL_KHONG_THU_TIEN, self._create_checkbox_widget(is_khong_thu_tien))
        table.setCellWidget(current_row_count, COL_KHONG_HO_TRO, self._create_checkbox_widget(is_khong_ho_tro))
        table.setCellWidget(current_row_count, COL_CHON_IN, self._create_checkbox_widget(is_chon_in))
        table.setCellWidget(current_row_count, COL_HUY, self._create_delete_button_widget(dich_vu_id))

        self.update_table_dich_vu_row_number()
        self._clear_input_fields()
        self.added_dich_vu_ids.add(dich_vu_id)
        self.update_cay_dich_vu()

        ui.ma_dich_vu.setFocus()

    # </editor-fold>


    # <editor-fold desc="Xoa dong dich vu trong bang dich vu">
    def _find_row_by_service_code(self, ma_dich_vu: str) -> int:
        table = self.ui_dich_vu.table_dich_vu

        for row in range(table.rowCount()):
            item = table.item(row, COL_MA_DV)
            if item and item.text() == ma_dich_vu:
                return row

        return -1

    def _delete_dich_vu_by_id(self, ma_dich_vu: str):
        table = self.ui_dich_vu.table_dich_vu
        row_index = self._find_row_by_service_code(ma_dich_vu)

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
                self.update_cay_dich_vu()

    # </editor-fold>


    # <editor-fold desc="Tao widget chua nut xoa dong dich vu">
    def _create_delete_button_widget(self, dich_vu_id: str):
        """Tạo widget chứa nút 'Xóa' cho QTableWidget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        btn_delete = QPushButton("Xóa")
        btn_delete.setStyleSheet("QPushButton { color: white; background-color: red }")

        # Liên kết tín hiệu clicked với hàm _delete_service_row
        # Cần truyền tham chiếu của widget container (widget) để tìm ra dòng
        btn_delete.clicked.connect(lambda: self._delete_dich_vu_by_id(dich_vu_id))

        layout.addWidget(btn_delete)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget
    # </editor-fold>


    # <editor-fold desc="Xu ly khi nguoi dung check hoac uncheck checkbox dich vu o cay dich vu ">
    def _handle_tree_item_check_state_changed(self, item: QTreeWidgetItem, column: int):
        """Xử lý khi người dùng check/uncheck dịch vụ trong QTreeWidget."""
        if column == TREE_COL_DICH_VU_CHECKBOX:
            ma_dich_vu = item.data(TREE_COL_DICH_VU, QtCore.Qt.ItemDataRole.UserRole)

            if not ma_dich_vu:
                return

            if item.checkState(TREE_COL_DICH_VU_CHECKBOX) == Qt.CheckState.Checked:
                if ma_dich_vu not in self.added_dich_vu_ids:
                    self.search_dich_vu_by_id(ma_dich_vu)
                    self._add_service_row(ADD_FROM_TREE_ITEM)
                    self.ui_dich_vu.ma_dich_vu.setFocus()
            elif item.checkState(TREE_COL_DICH_VU_CHECKBOX) == Qt.CheckState.Unchecked:
                if ma_dich_vu in self.added_dich_vu_ids:
                    # self._delete_dich_vu_by_id(ma_dich_vu)
                    pass
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


    def _create_checkbox_widget(self, is_checked: bool):
        """Tạo QCheckBox widget cho các cột Boolean (Không thu tiền, Không hỗ trợ, Chọn in)."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        checkbox = QCheckBox()
        checkbox.setChecked(is_checked)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget


    def update_table_dich_vu_row_number(self):
        """Đánh số lại các dòng dữ liệu (Vertical Header) sau khi thêm hoặc xóa."""
        table = self.ui_dich_vu.table_dich_vu

        for i in range(table.rowCount()):
            item = QtWidgets.QTableWidgetItem(str(i + 1))  # Bắt đầu từ 1
            table.setVerticalHeaderItem(i, item)


    def _handle_table_cell_clicked(self, row, col):
        """Xử lý sự kiện click vào cell trong bảng (để bắt lỗi click ngoài nút Xóa)."""
        # Nếu cột là cột Huỷ, sự kiện đã được _delete_service_row xử lý
        if col == COL_HUY:
            return

        # Các logic khác khi click vào cell (ví dụ: chỉnh sửa, focus) có thể thêm tại đây
        pass


    def btn_them_handler(self):
        self._add_service_row(mode=ADD_FROM_SEARCHBOX)
