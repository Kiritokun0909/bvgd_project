from PyQt6 import QtWidgets, QtCore

from app.ui.TabKhamBenh import Ui_formKhamBenh
from app.utils.config_manager import ConfigManager
from app.utils.utils import populate_combobox, load_data_from_csv, filter_data_by_foreign_key, get_first_row_data

PHONG_KHAM_FILE_PATH ='data/kham_benh/phong_kham.csv'
DOI_TUONG_FILE_PATH ='data/kham_benh/doi_tuong.csv'
GIAI_QUYET_FILE_PATH ='data/kham_benh/cach_giai_quyet.csv'
ICD_FILE_PATH ='data/kham_benh/icd.csv'
ICD_PHU_FILE_PATH ='data/kham_benh/icd_phu.csv'
BENH_NHAN_FILE_PATH='data/kham_benh/benh_nhan.csv'

class KhamBenhTabController(QtWidgets.QWidget):
    """
    Controller quản lý riêng biệt logic cho tab Khám bệnh.
    """

    def __init__(self, tab_widget_container, parent=None):
        super().__init__(parent)

        # Khởi tạo UI và load nó vào container (tab_widget_container) được truyền vào
        self.timer = None
        self.ui_kham = Ui_formKhamBenh()
        self.ui_kham.setupUi(tab_widget_container)  # <--- Nạp UI vào container cha

        # Setup cập nhật đồng hồ theo thơi gian thực vào field ngay_gio_kham
        self.setup_realtime_clock()

        self.init_data()

        # Khởi tạo Config Manager
        self.config_manager = ConfigManager()  # NEW

        # Tải và áp dụng cấu hình đã lưu
        self._load_saved_settings()  # NEW

        self.ui_kham.cb_ma_icd.currentTextChanged.connect(self.update_icd_phu)
        self.ui_kham.ma_y_te.textEdited.connect(self.update_thong_tin_benh_nhan)
        self.ui_kham.cb_phong_kham.currentIndexChanged.connect(self._save_settings)
        self.ui_kham.ten_bac_si.textEdited.connect(self._save_settings)

        self.ui_kham.cb_cach_giai_quyet.installEventFilter(self)

        # Logic: Kết nối các nút và trường dữ liệu (ví dụ)
        # self.ui_kham.refreshBtn.clicked.connect(self.handle_refresh)

    def _save_settings(self):
        """Lưu Mã phòng khám và Tên bác sĩ hiện tại vào QSettings."""

        # Lấy giá trị hiện tại
        phong_kham_code = self.ui_kham.cb_phong_kham.currentText()
        ten_bac_si_hien_tai = self.ui_kham.ten_bac_si.text()

        self.config_manager.save_last_selection(phong_kham_code, ten_bac_si_hien_tai)

    def _load_saved_settings(self):
        """Tải giá trị đã lưu và áp dụng chúng cho các widget."""

        phong_kham_saved, bac_si_saved = self.config_manager.load_last_selection()

        # Áp dụng cho Combobox Phòng khám
        if phong_kham_saved:
            # Dùng setCurrentText() vì bạn đổ dữ liệu Combobox bằng text (Lầu 1 Phòng 1)
            # print(phong_kham_saved)
            index = self.ui_kham.cb_phong_kham.findText(phong_kham_saved)
            # print(self.ui_kham.cb_phong_kham.count())
            # print(index)
            if index != -1:
                self.ui_kham.cb_phong_kham.setCurrentIndex(index)

        # Áp dụng cho LineEdit Tên bác sĩ
        if bac_si_saved:
            self.ui_kham.ten_bac_si.setText(bac_si_saved)

    def calculate_age_and_update(self, patient_data: dict):
        """
        Tính toán tuổi dựa trên ngày sinh và cập nhật QLabel tuổi.
        :param patient_data: Dictionary chứa dữ liệu bệnh nhân (bao gồm 'NgaySinh').
        """
        ngay_sinh_str = str(patient_data.get('NgaySinh', ''))
        date_format = "dd/MM/yyyy"  # Định dạng ngày tháng trong dữ liệu CSV

        birth_date = QtCore.QDate.fromString(ngay_sinh_str, date_format)

        if not birth_date.isValid():
            self.ui_kham.tuoi.setText("--")
            print(f"Lỗi: Ngày sinh '{ngay_sinh_str}' không hợp lệ hoặc sai định dạng.")
            return

        current_date = QtCore.QDate.currentDate()

        # Tính tuổi cơ bản
        age = current_date.year() - birth_date.year()

        # Điều chỉnh nếu ngày sinh trong năm hiện tại chưa đến
        if current_date.month() < birth_date.month() or \
                (current_date.month() == birth_date.month() and current_date.day() < birth_date.day()):
            age -= 1

        self.ui_kham.tuoi.setText(str(age))

    def update_thong_tin_benh_nhan(self, text: str):
        """
        Lấy Mã y tế, lọc dữ liệu bệnh nhân, và cập nhật giao diện.
        Hàm này được kích hoạt bởi tín hiệu textEdited từ self.ui_kham.ma_y_te.
        """
        ma_y_te = text  # Văn bản mới từ QLineEdit

        # 1. Kiểm tra điều kiện đầu vào và gọi reset nếu không đủ
        if len(ma_y_te) != 6:
            # self.reset_patient_info()
            return

        try:
            # 2. Tải và lọc dữ liệu (Giả định BENH_NHAN_FILE_PATH đã được định nghĩa)
            benh_nhan_df = load_data_from_csv(BENH_NHAN_FILE_PATH)
            filtered_df = filter_data_by_foreign_key(
                data_frame=benh_nhan_df,
                fk_key_value=ma_y_te,
                fk_column_name='MaYTe'  # Cột khóa ngoại trong CSV
            )

            # 3. Trích xuất dữ liệu dòng đầu tiên (sử dụng hàm mới từ data_utils)
            patient_data = get_first_row_data(filtered_df)

            if patient_data:
                # 4. Cập nhật giao diện với phương thức setTươngỨng()

                # Cập nhật QLineEdit (dùng setText())
                self.ui_kham.ho_ten_bn.setText(str(patient_data.get('HoTen', '')))
                self.ui_kham.so_bhyt.setText(str(patient_data.get('SoBHYT', '')))

                # Cập nhật QComboBox (dùng setCurrentText())
                # Lưu ý: Giá trị trong CSV phải khớp với item text đã có sẵn trong Combobox
                # Cập nhật Đối tượng (Sử dụng findData để tìm index bằng Mã)
                doi_tuong_code = str(patient_data.get('MaDoiTuong', ''))
                # findData mặc định tìm kiếm trong vai trò (role) QtCore.Qt.ItemDataRole (hoặc QtCore.Qt.UserRole)
                index = self.ui_kham.cb_doi_tuong.findData(doi_tuong_code)

                if index != -1:
                    self.ui_kham.cb_doi_tuong.setCurrentIndex(index)
                else:
                    # Fallback: Nếu không tìm thấy mã, thử set bằng text (nếu CSV có tên)
                    self.ui_kham.cb_doi_tuong.setCurrentText(doi_tuong_code)

                self.ui_kham.cb_gioi_tinh.setCurrentText(str(patient_data.get('GioiTinh', '')))

                # Cập nhật QDateEdit (dùng setDate() và QDate.fromString())
                date_format = "dd/MM/yyyy"  # Thay đổi nếu định dạng ngày trong CSV khác

                bhyt_from_date = QtCore.QDate.fromString(str(patient_data.get('BHTuNgay', '')), date_format)
                bhyt_to_date = QtCore.QDate.fromString(str(patient_data.get('BHDenNgay', '')), date_format)

                if bhyt_from_date.isValid():
                    self.ui_kham.bhyt_from.setDate(bhyt_from_date)

                if bhyt_to_date.isValid():
                    self.ui_kham.bhyt_to.setDate(bhyt_to_date)

                # Cập nhật tuổi (giả sử cột 'Tuoi' tồn tại)
                self.calculate_age_and_update(patient_data)

            else:
                print(f"Không tìm thấy bệnh nhân với Mã Y Tế: {ma_y_te}")
                # self.reset_patient_info()

        except Exception as e:
            print(f"Lỗi xảy ra trong quá trình cập nhật thông tin bệnh nhân: {e}")
            # self.reset_patient_info()

    def update_icd_phu(self):
        selected_icd = self.ui_kham.cb_ma_icd.currentText()
        # print(selected_icd)

        populate_combobox(
            combobox=self.ui_kham.cb_ma_icd_phu,
            display_col='MaICDPhu',
            key_col='MaICDPhu',
            file_path=ICD_PHU_FILE_PATH,
            fk_key_value=selected_icd,
            fk_column_name='MaICDChinh'
        )

    def setup_realtime_clock(self):
        """Thiết lập QTimer để cập nhật ngay_gio_kham mỗi giây."""
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_datetime_edit)
        self.timer.start(1000)
        self.update_datetime_edit()

    def update_datetime_edit(self):
        """Hàm cập nhật QDateTimeEdit với thời gian hệ thống."""
        current_datetime = QtCore.QDateTime.currentDateTime()
        # Truy cập QDateTimeEdit qua instance của UI con
        self.ui_kham.ngay_gio_kham.setDateTime(current_datetime)

    def init_data(self):
        populate_combobox(
            combobox=self.ui_kham.cb_phong_kham,
            display_col='TenPhong',
            key_col='MaPhong',
            file_path=PHONG_KHAM_FILE_PATH)

        populate_combobox(
            combobox=self.ui_kham.cb_doi_tuong,
            display_col='TenDT',
            key_col='MaDT',
            file_path=DOI_TUONG_FILE_PATH)

        populate_combobox(
            combobox=self.ui_kham.cb_cach_giai_quyet,
            display_col='TenGiaiQuyet',
            key_col='MaGiaiQuyet',
            file_path=GIAI_QUYET_FILE_PATH)

        populate_combobox(
            combobox=self.ui_kham.cb_ma_icd,
            display_col='MaICD',
            key_col='MaICD',
            file_path=ICD_FILE_PATH)

        self.ui_kham.cb_ma_icd_phu.clear()
        self.ui_kham.tuoi.setText('')
