from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QMessageBox, QLineEdit

from app.core.in_phieu_toa_thuoc import create_and_open_pdf_for_printing
from app.ui.TabKhamBenh import Ui_formKhamBenh
from app.utils.config_manager import ConfigManager
from app.utils.constants import MA_Y_TE_LENGTH
from app.utils.utils import populate_combobox, load_data_from_csv, filter_data_by_foreign_key, get_first_row_data, \
    calculate_age

from app.configs.drug_table_configs import *


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

    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        self.ma_y_te = None
        self.input_drug_name = None
        self.input_drug_so_luong = None
        self.ds_thuoc_df = None

        # self.ma_y_te = None
        self.ngay_sinh = None
        self.dia_chi = None
        self.so_dien_thoai = ''

        # KHỞI TẠO MODEL VÀ COMPLETER
        self.drug_model = QtCore.QStringListModel()
        self.drug_completer = QtWidgets.QCompleter(self.drug_model, self)
        self.drug_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.drug_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

        # BỘ ĐẾM THỜI GIAN DEBOUNCE
        self.search_timer = QtCore.QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_autocomplete_search)

        self._current_search_text = ""

        # Khởi tạo UI
        self.ui_kham = Ui_formKhamBenh()
        self.ui_kham.setupUi(tab_widget_container)

        # Load data va combobox, thiết lập đồng hồ và bảng toa thuốc
        self.init()
        self.setup_ngay_gio_kham_realtime_clock()
        self.setup_prescription_table()

        # Load thông tin cũ phòng khám
        self.config_manager = ConfigManager()
        self._load_saved_settings()

        self._connect_signals()


    # --- CÁC HÀM XỬ LÝ KHỞI TẠO DỮ LIỆU BAN ĐẦU ---

    def reset_data(self):
        self.ui_kham.ma_y_te.clear()
        self.ui_kham.ho_ten_bn.clear()
        self.ui_kham.noi_dung.clear()
        self.ui_kham.so_bhyt.clear()
        self.ui_kham.tuoi.clear()

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
        self.ui_kham.cb_ma_icd.setCurrentIndex(0)
        self.ui_kham.ma_icd_phu.clear()
        self.ui_kham.cb_cach_giai_quyet.setCurrentIndex(0)

        self.ui_kham.is_hen_kham.setChecked(False)
        self.ui_kham.so_ngay_hen.clear()
        self.ui_kham.ngay_hen_kham.setDate(QtCore.QDate.currentDate())

    def init(self):
        """Đổ dữ liệu ban đầu vào các combo_box."""
        populate_combobox(self.ui_kham.cb_phong_kham, 'TenPhong', 'MaPhong', PHONG_KHAM_FILE_PATH)
        populate_combobox(self.ui_kham.cb_doi_tuong, 'TenDT', 'MaDT', DOI_TUONG_FILE_PATH)
        populate_combobox(self.ui_kham.cb_cach_giai_quyet, 'TenGiaiQuyet', 'MaGiaiQuyet', GIAI_QUYET_FILE_PATH)
        populate_combobox(self.ui_kham.cb_ma_icd, 'MaICD', 'MaICD', ICD_FILE_PATH)

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

        self.ds_thuoc_df = load_data_from_csv(THUOC_FILE_PATH)

        self.reset_data()

    def _connect_signals(self):
        """Kết nối tất cả các tín hiệu và slot."""
        self.ui_kham.ma_y_te.textEdited.connect(self.load_thong_tin_benh_nhan)
        self.ui_kham.cb_phong_kham.currentIndexChanged.connect(self._save_settings)
        self.ui_kham.ten_bac_si.textEdited.connect(self._save_settings)
        self.ui_kham.is_hen_kham.clicked.connect(self.update_ngay_hen)
        self.ui_kham.so_ngay_hen.textEdited.connect(self.update_ngay_hen_kham_date)
        self.ui_kham.btn_in_phieu.clicked.connect(self.print_drug_bill)


    # --- SAVE VÀ LOAD THÔNG TIN PHÒNG KHÁM VÀ BÁC SĨ ---

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


    # --- CÁC HÀM XỬ LÝ THÔNG TIN BỆNH NHÂN ---

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
            patient_data = get_first_row_data(filtered_df)

            if patient_data:
                self.ui_kham.ho_ten_bn.setText(str(patient_data.get('HoTen', '')))
                so_bhyt = str(patient_data.get('SoBHYT', ''))
                if so_bhyt == 'nan':
                    so_bhyt = 'Không có'
                self.ui_kham.so_bhyt.setText(so_bhyt)

                ma_doi_tuong = str(patient_data.get('MaDoiTuong', ''))
                index = self.ui_kham.cb_doi_tuong.findData(ma_doi_tuong)
                if index != -1:
                    self.ui_kham.cb_doi_tuong.setCurrentIndex(index)
                else:
                    self.ui_kham.cb_doi_tuong.setCurrentIndex(0)

                self.ui_kham.cb_gioi_tinh.setCurrentText(str(patient_data.get('GioiTinh', '')))

                date_format = "dd/MM/yyyy"
                bhyt_from_date = QtCore.QDate.fromString(str(patient_data.get('BHTuNgay', '')), date_format)
                bhyt_to_date = QtCore.QDate.fromString(str(patient_data.get('BHDenNgay', '')), date_format)

                if bhyt_from_date.isValid():
                    self.ui_kham.bhyt_from.setDate(bhyt_from_date)
                if bhyt_to_date.isValid():
                    self.ui_kham.bhyt_to.setDate(bhyt_to_date)

                self.ma_y_te = str(patient_data.get('MaYTe')).upper()
                self.ngay_sinh = str(patient_data.get('NgaySinh'))
                self.ui_kham.tuoi.setStyleSheet('font-weight: 700; font-size: 20px;')
                self.ui_kham.tuoi.setText(str(calculate_age(self.ngay_sinh)))
                self.dia_chi = str(patient_data.get('DiaChi'))
                self.so_dien_thoai = '0' + str(patient_data.get('SoDienThoai'))
            else:
                print(f"Không tìm thấy bệnh nhân với Mã Y Tế: {ma_y_te}")

        except Exception as e:
            print(f"Lỗi xảy ra trong quá trình cập nhật thông tin bệnh nhân: {e}")


    # --- SETUP ĐỒNG HỒ CHO ngày giờ khám ---

    def setup_ngay_gio_kham_realtime_clock(self):
        """Thiết lập QTimer để cập nhật ngay_gio_kham mỗi giây."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_ngay_gio_kham_datetime_edit)
        self.timer.start(1000)
        self.update_ngay_gio_kham_datetime_edit()

    def update_ngay_gio_kham_datetime_edit(self):
        """Hàm cập nhật QDateTimeEdit với thời gian hệ thống."""
        self.ui_kham.ngay_gio_kham.setDateTime(QtCore.QDateTime.currentDateTime())


    # --- LOGIC CODE CHO ngày hẹn khám ---

    def update_ngay_hen(self):
        """Xử lý logic khi checkbox hẹn khám được click."""
        is_checked = self.ui_kham.is_hen_kham.isChecked()
        self.ui_kham.so_ngay_hen.setReadOnly(not is_checked)
        if not is_checked:
            self.ui_kham.so_ngay_hen.setText('')
            self.ui_kham.ngay_hen_kham.setDate(QtCore.QDate.currentDate())
        else:
            # Kích hoạt lại việc tính toán ngày hẹn nếu đã có số ngày
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


    # --- SETUP BẢNG TOA THUỐC ---

    def setup_prescription_table(self):
        """Thiết lập cấu trúc cột và khởi tạo dòng nhập liệu."""
        self.ui_kham.ds_thuoc.setColumnCount(DRUG_COL_COUNT)
        self.ui_kham.ds_thuoc.setHorizontalHeaderLabels(HEADER_THUOC)

        # ẨN CỘT MÃ THUỐC (Chỉ dùng cho dữ liệu, không hiển thị cho người dùng)
        self.ui_kham.ds_thuoc.setColumnHidden(COL_MA_THUOC, True)

        # Thiết lập chiều rộng
        self.ui_kham.ds_thuoc.setColumnWidth(COL_TEN_THUOC, COL_TEN_THUOC_WIDTH)

        self.add_input_row()


    # --- CÁC HÀM XỬ LÝ BẢNG THUỐC (QUAN TRỌNG) ---

    def load_drug_details(self, drug_name: str, row_index: int):
        """Tra cứu đơn vị tính, đơn giá, và MÃ THUỐC rồi cập nhật các ô."""
        if not drug_name:
            return

        table = self.ui_kham.ds_thuoc
        cleaned_drug_name = drug_name.lower().strip()

        # 1. Tra cứu dữ liệu
        filtered_df = self.ds_thuoc_df[self.ds_thuoc_df['TenThuoc'].str.lower() == cleaned_drug_name]

        if filtered_df.empty:
            return

        drug_data = filtered_df.iloc[0]

        ma_thuoc = drug_data.get('MaThuoc', '')
        don_vi_tinh = drug_data.get('DonVi', '')
        don_gia = drug_data.get('Gia', '')

        # 2. Cập nhật giao diện
        # Cột MÃ THUỐC (COL_MA_THUOC)
        ma_thuoc_widget = table.cellWidget(row_index, COL_MA_THUOC)
        if ma_thuoc_widget and isinstance(ma_thuoc_widget, QLineEdit):
            ma_thuoc_widget.setText(str(ma_thuoc))

        # Cột Đơn vị tính (COL_DON_VI_TINH)
        unit_widget = table.cellWidget(row_index, COL_DON_VI_TINH)
        if unit_widget and isinstance(unit_widget, QLineEdit):
            unit_widget.setText(str(don_vi_tinh))

        # Cột Đơn giá (COL_DON_GIA)
        price_widget = table.cellWidget(row_index, COL_DON_GIA)
        if price_widget and isinstance(price_widget, QLineEdit):
            price_widget.setText(str(don_gia))

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

    def validate_drug_entry(self, input_row_index: int) -> bool:
        """Xác thực dữ liệu nhập vào trước khi thêm vào bảng tĩnh."""
        table = self.ui_kham.ds_thuoc

        drug_name_widget = table.cellWidget(input_row_index, COL_TEN_THUOC)

        # 1. Kiểm tra Tên Thuốc
        if not drug_name_widget or not drug_name_widget.text().strip():
            QMessageBox.warning(self, "Lỗi nhập liệu", "Vui lòng nhập và chọn Tên Thuốc.")
            drug_name_widget.setFocus()
            return False

        entered_drug_name = drug_name_widget.text().strip()

        # Lấy danh sách tên thuốc chuẩn để so sánh
        # Chuyển về chữ thường để so sánh không phân biệt chữ hoa/thường
        valid_drug_names_lower = self.ds_thuoc_df['TenThuoc'].str.lower().tolist()

        if entered_drug_name.lower() not in valid_drug_names_lower:
            QMessageBox.warning(self, "Lỗi xác thực",
                                 f"Tên thuốc '{entered_drug_name}' không hợp lệ hoặc không có trong danh mục thuốc.")
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
        delete_btn.setStyleSheet("background-color: #F44336; color: white;")
        delete_btn.clicked.connect(self.handle_delete_row)

        widget_container = QWidget()
        layout = QHBoxLayout(widget_container)
        layout.addWidget(delete_btn)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        table.setCellWidget(data_row_index, COL_HUY, widget_container)

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
        self._update_completer_model()

        # ********** CHÈN STYLESHEET TRỰC TIẾP VÀO POPUP **********
        completer_style = """
                QListView {
                    /* Viền bao quanh cửa sổ popup */
                    border: 1px solid #0078D4; 
                    border-radius: 5px; 
                    background-color: #ebebeb;
                    font-size: 14px;
                    selection-background-color: #ADD8E6; 
                    selection-color: black;
                    padding: 4px;
                }
                QListView::item {
                    /* Tùy chỉnh mỗi mục trong danh sách gợi ý */
                    padding: 4px;
                    min-height: 25px; 
                }
                QListView::item:selected {
                    /* Giao diện khi mục được chọn */
                    background-color: #0078D4; 
                    color: white;
                    border: none; /* Đảm bảo loại bỏ viền focus */
                    outline: none;
                }
        """
        # Áp dụng Stylesheet trực tiếp lên popup (là QListView)
        self.drug_completer.popup().setStyleSheet(completer_style)

        # Gán QCompleter cho QLineEdit
        input_drug_name.setCompleter(self.drug_completer)

        # Kết nối sự kiện Gõ phím
        input_drug_name.textEdited.connect(self._start_autocomplete_search)

        # Kết nối load details (cần load cả Mã thuốc ở load_drug_details)
        self.drug_completer.activated.connect(lambda text: self.load_drug_details(text, 0))
        input_drug_name.editingFinished.connect(lambda: self.load_drug_details(self.input_drug_name.text(), 0))

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

            if col >= COL_SO_NGAY:
                line_edit.returnPressed.connect(lambda: self.finalize_drug_entry(0))

            if col == COL_SO_LUONG:
                self.input_drug_so_luong = line_edit

        # Cột Hủy ở dòng nhập liệu (dòng nhập liệu không cần nút Hủy)
        table.setCellWidget(0, COL_HUY, QWidget())

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

        self._update_completer_model()
        self.update_row_numbers()

    def update_row_numbers(self):
        """Đánh số lại các dòng dữ liệu sau khi thêm hoặc xóa."""
        table = self.ui_kham.ds_thuoc
        # Bắt đầu từ dòng 1 (vì dòng 0 là dòng nhập liệu)
        for i in range(1, table.rowCount()):
            item = QtWidgets.QTableWidgetItem(str(i))
            table.setVerticalHeaderItem(i, item)


    # --- LỌC CÁC THUỐC ĐÃ CHỌN TRONG TOA KHỎI DANH SÁCH THUỐC TÌM KIẾM ---

    def _get_available_drug_names(self) -> list:
        """Hàm tiện ích: Lấy danh sách tên thuốc khả dụng (chưa thêm vào bảng)."""
        table = self.ui_kham.ds_thuoc
        added_drugs = set()
        for row in range(1, table.rowCount()):
            item = table.item(row, COL_TEN_THUOC)
            if item:
                added_drugs.add(item.text().strip())

        all_drug_names = self.ds_thuoc_df['TenThuoc'].tolist()

        available_drugs = [name for name in all_drug_names if name not in added_drugs]
        return available_drugs

    def _update_completer_model(self):
        """Cập nhật Model với TẤT CẢ thuốc khả dụng."""
        available_drugs = self._get_available_drug_names()
        self.drug_model.setStringList(available_drugs)


    # --- HÀM DEBOUNCE VÀ TÌM KIẾM ---

    def _start_autocomplete_search(self, text: str):
        """
        Bắt đầu đếm ngược cho Debounce, chỉ thực hiện tìm kiếm nếu người dùng ngừng gõ
        và đã nhập TỪ HAI ký tự trở lên.
        """
        self._current_search_text = text.strip()
        search_len = len(self._current_search_text)

        # Luôn dừng timer cũ để reset debounce
        self.search_timer.stop()

        if search_len == 0:
            # Nếu rỗng, hiển thị lại toàn bộ danh sách có sẵn (hoặc 50 mục đầu)
            self._perform_autocomplete_search()
            return

        if search_len == 1:
            # Nếu chỉ có 1 ký tự, dừng tìm kiếm và ẩn popup
            self.drug_model.setStringList([])  # Xóa model để không có kết quả
            self.drug_completer.popup().hide()  # Ẩn popup ngay lập tức
            return

        if search_len > 1:
            # Nếu có 2 ký tự trở lên, bắt đầu debounce 200ms
            self.search_timer.start(200)

    def _perform_autocomplete_search(self):
        """Thực hiện tìm kiếm thủ công, cập nhật model và hiển thị popup."""
        text = self._current_search_text
        available_drugs_all = self._get_available_drug_names()

        if not text:
            # Hiển thị tất cả thuốc khả dụng (khi ô nhập liệu rỗng)
            filtered_drugs = available_drugs_all
        else:
            text_lower = text.lower()

            # Lọc thủ công (MatchContains logic) và GIỚI HẠN KẾT QUẢ ĐẦU TIÊN
            filtered_drugs = [
                                 name for name in available_drugs_all
                                 if text_lower in name.lower()
                             ][:50]  # Chỉ lấy tối đa 50 kết quả

        self.drug_model.setStringList(filtered_drugs)

        # Cập nhật và tự động chọn dòng đầu tiên
        if self.drug_model.rowCount() > 0:
            self.drug_completer.complete()
        else:
            self.drug_completer.popup().hide()  # Ẩn nếu không có kết quả


    # --- HÀM XỬ LÝ IN TOA THUỐC ---

    def print_drug_bill(self):
        """
                Thu thập tất cả dữ liệu từ form Khám bệnh và bảng thuốc
                để chuẩn bị cho việc in ấn hoặc lưu trữ.
                """
        data = {}

        # 1. Thu thập Thông tin Bệnh nhân và Hành chính
        data['HanhChinh'] = {
            'PhongKham': self.ui_kham.cb_phong_kham.currentText(),
            'TenBacSi': self.ui_kham.ten_bac_si.text().strip(),
            'MaYTe': self.ui_kham.ma_y_te.text().strip(),
            'HoTenBN': self.ui_kham.ho_ten_bn.text().strip(),
            'DoiTuong': self.ui_kham.cb_doi_tuong.currentText(),
            'Tuoi': self.ui_kham.tuoi.text().strip(),
            'GioiTinh': self.ui_kham.cb_gioi_tinh.currentText(),
            'SoBHYT': self.ui_kham.so_bhyt.text().strip(),
            'BHYT_Tu': self.ui_kham.bhyt_from.date().toString("dd/MM/yyyy"),
            'BHYT_Den': self.ui_kham.bhyt_to.date().toString("dd/MM/yyyy"),
            'NgayGioKham': self.ui_kham.ngay_gio_kham.dateTime().toString("dd/MM/yyyy HH:mm:ss"),
            'DiaChi': self.dia_chi,
            'SDT': self.so_dien_thoai,
        }

        # 2. Thu thập Thông tin Khám bệnh
        data['KhamBenh'] = {
            'Mach': self.ui_kham.mach.text().strip(),
            'NhietDo': self.ui_kham.nhiet_do.text().strip(),
            'HuyetAp1': self.ui_kham.huyet_ap_1.text().strip(),
            'HuyetAp2': self.ui_kham.huyet_ap_2.text().strip(),
            'NhipTho': self.ui_kham.nhip_tho.text().strip(),
            'CanNang': self.ui_kham.can_nang.text().strip(),
            'ChanDoan': self.ui_kham.chan_doan.text().strip(),
            'MaICD': self.ui_kham.cb_ma_icd.currentData(),
            'ICDPhu': self.ui_kham.ma_icd_phu.text(),
            'CachGiaiQuyet': self.ui_kham.cb_cach_giai_quyet.currentData(),
        }

        # 3. Thu thập Thông tin Hẹn khám
        data['HenKham'] = {
            'IsHenKham': self.ui_kham.is_hen_kham.isChecked(),
            'SoNgayHen': self.ui_kham.so_ngay_hen.text().strip(),
            'NgayHenKham': self.ui_kham.ngay_hen_kham.date().toString("dd/MM/yyyy"),
        }

        # 4. Thu thập Danh sách Thuốc đã thêm vào bảng
        table = self.ui_kham.ds_thuoc

        # kiểm tra có thuốc trong ds toa thuốc hay không
        if table.rowCount() < 2:
            QMessageBox.warning(self,
                                "Thông báo",
                                f"Chưa có thuốc nào trong toa thuốc.")
            return

        drug_list = []

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

        data['DanhSachThuoc'] = drug_list

        # --- HIỂN THỊ DỮ LIỆU THU THẬP ĐƯỢC (ĐỂ TEST) ---
        # print("--- DỮ LIỆU FORM ĐÃ THU THẬP ---")
        # import json
        # print(json.dumps(data, indent=4, ensure_ascii=False))
        # print("-----------------------------------")

        # Bổ sung logic in hoặc lưu trữ ở đây
        # QMessageBox.information(self, "Thông báo", "Đã thu thập dữ liệu form thành công. Sẵn sàng cho việc in/lưu.")

        # Format và gọi hàm in phiếu
        data_for_print = self.map_data_for_print(data)
        create_and_open_pdf_for_printing(data_for_print)


    # --- FORMAT DATA CHO VIỆC IN TOA THUỐC ---

    def map_data_for_print(self, raw_data: dict) -> dict:
        """
        Ánh xạ dữ liệu thu thập từ form Khám bệnh (raw_data)
        sang cấu trúc dữ liệu chuẩn bị cho ReportLab (in_phieu_toa_thuoc).
        """

        hanh_chinh = raw_data.get('HanhChinh', {})
        kham_benh = raw_data.get('KhamBenh', {})
        hen_kham = raw_data.get('HenKham', {})
        ds_thuoc = raw_data.get('DanhSachThuoc', [])

        # Giả định các thông tin cố định hoặc được lấy từ cấu hình hệ thống
        SO_Y_TE = "SỞ Y TẾ TP.HCM"
        TEN_BENH_VIEN = "BỆNH VIỆN NHÂN DÂN GIA ĐÌNH"  # Cần được lấy từ config

        # -------------------------------------------------------------
        # 1. Ánh xạ Danh sách Thuốc
        # -------------------------------------------------------------

        mapped_drugs = []
        # Khai báo lại FIELD_MAPPING từ kham_benh_controller để dễ truy cập
        local_field_mapping = {v: k for k, v in FIELD_MAPPING.items()}

        for idx, drug in enumerate(ds_thuoc):
            # Lấy Tên thuốc phụ/ghi chú. Hiện tại không có trường TenThuocPhu rõ ràng,
            # nên tạm thời dùng cột 'Ghi chú' và giả định nó có tên thuốc kèm liều lượng
            ghi_chu = drug.get('GhiChu', '')
            ten_thuoc_phu = ghi_chu if ghi_chu else f"({drug.get('TenThuoc', '')}), {drug.get('DonGia', '')}đ"

            mapped_drugs.append({
                'stt': str(idx + 1),  # Đánh số lại
                'ten_thuoc': drug.get('TenThuoc', ''),
                'ten_thuoc_phu': ghi_chu,  # Sử dụng cột GhiChu cho mục đích này
                'don_vi_tinh': drug.get('DonViTinh', ''),
                'sang': drug.get('Sang', '0'),
                'trua': drug.get('Trua', '0'),
                'chieu': drug.get('Chieu', '0'),
                'toi': drug.get('Toi', '0'),
                'so_ngay': drug.get('SoNgay', '0'),
                'so_luong': drug.get('SoLuong', '0')
            })

        # -------------------------------------------------------------
        # 2. Ánh xạ Thông tin Hành chính/Khám bệnh
        # -------------------------------------------------------------

        # Note: Trong code mẫu của bạn, Mã đối tượng (DoiTuong) là code, cần tìm tên hiển thị.
        # Tuy nhiên, print_drug_bill lấy code (key), nên ta sẽ tạm dùng key ở đây.
        # Lý tưởng là lưu cả tên và key. Ở đây ta giả sử Mã Đối tượng là code hiển thị.

        # Xử lý Huyết áp
        huyet_ap = f"{kham_benh.get('HuyetAp1', '')}/{kham_benh.get('HuyetAp2', '')}"
        if huyet_ap == '/': huyet_ap = ''

        # Xử lý Ngày hẹn khám
        so_ngay_hen = hen_kham.get('SoNgayHen', '')
        ngay_hen_kham_text = f"{hen_kham.get('NgayHenKham', '')}"
        dr_note_text = f"Hẹn tái khám {so_ngay_hen} ngày ({ngay_hen_kham_text})" if self.ui_kham.is_hen_kham and so_ngay_hen else ""

        # Tên bác sĩ (được lấy từ HanhChinh)
        ten_bac_si = hanh_chinh.get('TenBacSi', '')
        if not ten_bac_si:
            ten_bac_si = "Bác sĩ điều trị"  # Tên mặc định nếu chưa nhập

        final_data = {
            'so_y_te': SO_Y_TE,
            'ten_benh_vien': TEN_BENH_VIEN,
            'phong_kham': f"{hanh_chinh.get('PhongKham', '')} ({kham_benh.get('MaICD', '')})",
            # Thêm ICD vào để mô phỏng
            'doi_tuong': f"BHYT {hanh_chinh.get('DoiTuong', '')}",  # Hiển thị Đối tượng

            'ho_ten': hanh_chinh.get('HoTenBN', ''),
            'tuoi': hanh_chinh.get('Tuoi', ''),
            'can_nang': kham_benh.get('CanNang', ''),
            'gioi_tinh': hanh_chinh.get('GioiTinh', ''),
            'ma_bhyt': hanh_chinh.get('SoBHYT', ''),

            'dia_chi': f"{self.dia_chi}",
            'sdt': str(self.so_dien_thoai),
            'ngay_tiep_nhan': hanh_chinh.get('NgayGioKham', ''),

            'chan_doan': kham_benh.get('ChanDoan', ''),
            'mach': kham_benh.get('Mach', ''),
            'HA': huyet_ap,
            'nhiet_do': kham_benh.get('NhietDo', ''),

            'so_ngay_hen_tai_kham': so_ngay_hen,
            'ngay_hen_tai_kham': ngay_hen_kham_text,
            'dr_note': dr_note_text,

            'ten_bac_si': ten_bac_si,
            'ds_thuoc': mapped_drugs,

            'ngay_kham': self.ui_kham.ngay_gio_kham.date().toString('dd'),
            'thang_kham': self.ui_kham.ngay_gio_kham.date().toString('MM'),
            'nam_kham': self.ui_kham.ngay_gio_kham.date().toString('yyyy')
        }

        return final_data


    # --- LẤY DỮ LIỆU HÀNH CHÍNH ĐỂ CHUYỂN SANG TAB ĐĂNG KÝ DỊCH VỤ ---

    def get_hanh_chinh_data(self) -> dict:
        """
        Thu thập các thông tin hành chính cơ bản của bệnh nhân
        để chuyển sang tab/màn hình khác.
        """
        ma_dt = self.ui_kham.cb_doi_tuong.currentData()

        data = {
            'MaYTe': self.ui_kham.ma_y_te.text().strip(),
            'HoTenBN': self.ui_kham.ho_ten_bn.text().strip(),
            'Tuoi': self.ui_kham.tuoi.text().strip(),
            'GioiTinh': self.ui_kham.cb_gioi_tinh.currentText(),
            'SoBHYT': self.ui_kham.so_bhyt.text().strip(),
            'BHYT_Tu': self.ui_kham.bhyt_from.date().toString("dd/MM/yyyy"),
            'BHYT_Den': self.ui_kham.bhyt_to.date().toString("dd/MM/yyyy"),
            'NgayGioKham': self.ui_kham.ngay_gio_kham.dateTime().toString("dd/MM/yyyy HH:mm:ss"),
            'MaDoiTuong': ma_dt,
            'TenDoiTuong': self.ui_kham.cb_doi_tuong.currentText(),
            'PhongKham': self.ui_kham.cb_phong_kham.currentText(),
            'MaPhongKham': self.ui_kham.cb_phong_kham.currentData(),
            'TenBacSi': self.ui_kham.ten_bac_si.text().strip(),
            'MaGiaiQuyet': self.ui_kham.cb_cach_giai_quyet.currentData(),
            'ChanDoan': self.ui_kham.chan_doan.text(),
            'DiaChi': self.dia_chi,
            'NgaySinh': self.ngay_sinh,
        }

        return data
