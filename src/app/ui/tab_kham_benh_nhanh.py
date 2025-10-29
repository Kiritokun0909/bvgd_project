from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QTableWidget,
    QLabel, QGroupBox, QTextEdit, QStyle, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime


# Hàm tạo đường kẻ phân cách
def create_separator():
    line = QWidget()
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: black;")
    return line


class TabKhamBenhNhanh(QWidget):
    def __init__(self):
        super().__init__()
        # Khởi tạo layout chính cho TabKhamBenhNhanh
        self.main_layout = QVBoxLayout(self)  # Q Vertical Box layout

        # === Khởi tạo QTimer và kết nối ===
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime_field)
        self.timer.start(1000)  # Cập nhật mỗi 1000ms = 1 giây

        self.datetime_field = None  # Biến lưu trữ QLineEdit của ngày giờ

        # === 1. Header: Thông tin Hành chính ===
        self.main_layout.addLayout(self.create_header_layout())

        # === 2. Body Top: Danh sách chờ & Thông tin Khám ===
        body_top_layout = QHBoxLayout() # Q Horizontal Box layout
        body_top_layout.addWidget(self.create_waitlist_section(), 1)  # Chiếm 1 phần
        body_top_layout.addWidget(self.create_exam_info_section(), 2)  # Chiếm 2 phần
        self.main_layout.addLayout(body_top_layout)

        # === 3. Body Bottom: Toa Thuốc ===
        self.main_layout.addLayout(self.create_drug_prescription_section())

        # Thiết lập tỷ lệ co giãn cho các phần chính
        # index: vị trí của layout
        # (1: index của layout body_top), (2: index của layout body_bottom)
        # stretch: hệ số co giãn
        self.main_layout.setStretch(0, 0)
        self.main_layout.setStretch(1, 2)
        self.main_layout.setStretch(2, 2)

    # Phương thức lấy và cập nhật thời gian
    def update_datetime_field(self):
        if self.datetime_field:
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.datetime_field.setText(current_time)

    # -------------------------------------------------------------------
    # KHU VỰC 1: HEADER - THÔNG TIN HÀNH CHÍNH
    # -------------------------------------------------------------------
    def create_header_layout(self):
        header_layout = QGridLayout()

        # Hàm hỗ trợ tạo cặp Label-Widget
        def add_field(layout, label_text, widget, row, col_start, is_readonly=False):
            label = QLabel(label_text)
            if is_readonly:
                widget.setReadOnly(True)
                widget.setStyleSheet("background-color: #f0f0f0;")

            layout.addWidget(label, row, col_start)
            layout.addWidget(widget, row, col_start + 1)

        ho_ten_field = QLineEdit()
        ho_ten_field.setText("Nguyễn Văn A")

        tuoi_field = QLineEdit()
        tuoi_field.setText("20")

        ngay_gio_field = QLineEdit()
        self.datetime_field = ngay_gio_field
        self.update_datetime_field()

        # Dòng 1
        add_field(header_layout, "Phòng khám", QComboBox(), 0, 0)
        add_field(header_layout, "Mã y tế", QLineEdit(), 0, 2)
        add_field(header_layout, "Nội dung", QLineEdit(), 0, 4)

        # Dòng 2
        add_field(header_layout, "Bác sỹ khám", QLineEdit(), 1, 0)
        add_field(header_layout, "Họ tên", ho_ten_field, 1, 2, is_readonly=False)
        add_field(header_layout, "Giới tính", QComboBox(), 1, 4)
        add_field(header_layout, "Tuổi", tuoi_field, 1, 6, is_readonly=True)

        # Dòng 3
        add_field(header_layout, "Ngày giờ khám", ngay_gio_field, 2, 0, is_readonly=True)
        add_field(header_layout, "Đối tượng", QComboBox(), 2, 2)
        add_field(header_layout, "Số BHYT", QLineEdit(), 2, 4)

        # Phần ngày giờ cố định
        date_label = QLabel("28/10/2025 - 28/10/2025")
        header_layout.addWidget(date_label, 2, 6, alignment=Qt.AlignmentFlag.AlignRight)

        # Căn chỉnh các cột
        for i in range(7):
            header_layout.setColumnStretch(i, 1 if i % 2 != 0 else 0)

        # Thêm đường kẻ phân cách dưới Header
        header_layout.addWidget(create_separator(), 3, 0, 1, 7)

        return header_layout

    # -------------------------------------------------------------------
    # KHU VỰC 2A: DANH SÁCH CHỜ
    # -------------------------------------------------------------------
    def create_waitlist_section(self):
        waitlist_group = QGroupBox("DANH SÁCH CHỜ KHÁM BỆNH NHÂN")
        layout = QVBoxLayout(waitlist_group)

        # Tạo nút Reload
        reload_btn = QPushButton("Refresh")

        # 1. TẠO ICON TÁI SỬ DỤNG (RELOAD/REFRESH)
        # Sử dụng QStyle để lấy icon có sẵn (ví dụ: QStyle.StandardPixmap.SP_BrowserReload)
        reload_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
        reload_btn.setIcon(reload_icon)

        reload_btn.setMaximumWidth(150)

        h_layout = QHBoxLayout()
        h_layout.addStretch(1)  # Đẩy nút sang phải
        h_layout.addWidget(reload_btn)
        layout.addLayout(h_layout)

        # Bảng danh sách chờ
        label_data = ["Mã y tế", "Họ tên", "Tuổi", "Giới tính", "Số BHYT"]
        table = QTableWidget(5, len(label_data))  # 5 hàng, 5 cột
        table.setHorizontalHeaderLabels(label_data)

        # 2. Định nghĩa dữ liệu mẫu
        data = [
            ["12345678", "Nguyễn Văn A", "35", "Nam"],
            ["87654321", "Trần Thị C", "42", "Nữ"],
            ["87654321", "Trần Thị C", "42", "Nữ"],
            ["87654321", "Trần Thị C", "42", "Nữ"],
            ["87654321", "Trần Thị C", "42", "Nữ"],
            ["87654321", "Trần Thị C", "42", "Nữ"],
        ]

        # 3. Thiết lập số dòng dựa trên dữ liệu mẫu
        table.setRowCount(len(data))

        # 4. Thêm dữ liệu vào các ô
        for row_index, row_data in enumerate(data):
            for col_index, cell_data in enumerate(row_data):
                # Tạo QTableWidgetItem từ dữ liệu và gán vào bảng
                item = QTableWidgetItem(cell_data)
                table.setItem(row_index, col_index, item)

        layout.addWidget(table)

        # Phân trang
        page_nav_label = QLabel("PAGE NAVIGATION")
        page_nav_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_nav_label.setStyleSheet("border: 1px solid black;")
        page_nav_label.setFixedHeight(30)
        layout.addWidget(page_nav_label)

        return waitlist_group

    # -------------------------------------------------------------------
    # KHU VỰC 2B: THÔNG TIN KHÁM BỆNH
    # -------------------------------------------------------------------
    def create_exam_info_section(self):
        info_group = QGroupBox("THÔNG TIN KHÁM BỆNH")
        layout = QVBoxLayout(info_group)

        """
            LAYOUT CHỈ SỐ SINH TỒN (VITALS)
        """
        vitals_layout = QGridLayout()

        # Hàm hỗ trợ tạo input với đơn vị
        def add_vitals_field(layout, label_text, unit_text, row, col_start):
            # Label
            layout.addWidget(QLabel(label_text), row, col_start)

            # Input
            input_field = QLineEdit("")
            layout.addWidget(input_field, row, col_start + 1)

            # Đơn vị
            if unit_text:
                unit_label = QLabel(unit_text)
                layout.addWidget(unit_label, row, col_start + 2)

        # Dòng 1: Mạch, Nhịp thở, Chiều cao, Đường huyết
        add_vitals_field(vitals_layout, "Mạch", "lần", 0, 0)
        add_vitals_field(vitals_layout, "Nhịp thở", "lần", 0, 3)
        add_vitals_field(vitals_layout, "Chiều cao", "cm", 0, 6)
        add_vitals_field(vitals_layout, "Đường huyết", "lần", 0, 9)

        # Dòng 2: Nhiệt độ, Huyết áp, Cân nặng, SpO2
        add_vitals_field(vitals_layout, "Nhiệt độ", "℃", 1, 0)

        # Huyết áp đặc biệt
        vitals_layout.addWidget(QLabel("Huyết áp"), 1, 3)
        ha_layout = QHBoxLayout()
        ha_layout.addWidget(QLineEdit())
        ha_layout.addWidget(QLabel("/"))
        ha_layout.addWidget(QLineEdit())
        vitals_layout.addLayout(ha_layout, 1, 4)
        vitals_layout.addWidget(QLabel("mmHg"), 1, 5)

        add_vitals_field(vitals_layout, "Cân nặng", "kg", 1, 6)
        add_vitals_field(vitals_layout, "SpO2", "%", 1, 9)

        # Điều chỉnh co giãn cột cho Vitals
        for i in range(12):
            vitals_layout.setColumnStretch(i, 1)

        layout.addLayout(vitals_layout)

        # Thêm đường kẻ phân cách
        layout.addWidget(create_separator())

        """
            LAYOUT CHẨN ĐOÁN (Đã sửa)
        """
        diag_layout = QGridLayout()

        def add_diagnose_field(layout, label_text, widget, row, col_start):
            """Thêm một cặp QLabel và Widget vào QGridLayout."""
            layout.addWidget(QLabel(label_text), row, col_start)
            layout.addWidget(widget, row, col_start + 1)

        # --- 1. Khởi tạo Widgets ---
        chan_doan = QLineEdit()
        icd = QComboBox()
        icd_phu = QComboBox()
        cach_giai_quyet = QComboBox()

        # --- 2. Thêm Chẩn đoán Chính (Cần co giãn) ---
        # Thêm Label ("Chẩn đoán") vào (0, 0)
        diag_layout.addWidget(QLabel("Chẩn đoán"), 0, 0)

        # Thêm QLineEdit (chan_doan) vào (0, 1) và kéo dài qua nhiều cột (colspan)
        diag_layout.addWidget(chan_doan, 0, 1, 1, 5)

        # --- 3. Thêm các trường còn lại (Sử dụng Hàm Hỗ trợ) ---
        # Row 1: Mã ICD và Mã ICD Phụ
        icd.addItem("Nội khoa")
        icd.addItem("Ngoại khoa")
        icd.setEditable(True)
        add_diagnose_field(diag_layout, "Mã ICD", icd, 1, 0)  # Bắt đầu từ cột 0
        add_diagnose_field(diag_layout, "Mã ICD phụ", icd_phu, 2, 0)  # Bắt đầu từ cột 2

        # Row 2: Cách giải quyết
        add_diagnose_field(diag_layout, "Cách giải quyết", cach_giai_quyet, 3, 0)

        # Tùy chọn: Thêm spacer hoặc chỉnh stretch để căn chỉnh layout
        diag_layout.setColumnStretch(1, 1)  # Cho cột chứa input của ICD co giãn
        diag_layout.setColumnStretch(3, 1)  # Cho cột chứa input của ICD phụ co giãn

        # Cuối cùng, thêm layout chẩn đoán này vào layout cha (ví dụ: layout của info_group)
        layout.addLayout(diag_layout)

        return info_group

    # -------------------------------------------------------------------
    # KHU VỰC 3: TOA THUỐC
    # -------------------------------------------------------------------
    def create_drug_prescription_section(self):
        drug_layout = QVBoxLayout()

        # Tiêu đề
        drug_label_layout = QHBoxLayout()
        drug_label_layout.addWidget(QLabel("TOA THUỐC"))
        drug_label_layout.addStretch(1)
        drug_layout.addLayout(drug_label_layout)

        # Khu vực nhập Toa thuốc
        drug_area = QTextEdit()
        drug_area.setPlaceholderText("Nhập chi tiết thuốc, liều dùng, số lượng...")
        drug_layout.addWidget(drug_area)

        # Nút In (căn phải)
        print_btn = QPushButton("IN PHIẾU TOA THUỐC")
        print_btn.setFixedSize(150, 30)

        print_btn_layout = QHBoxLayout()
        print_btn_layout.addStretch(1)  # Đẩy nút sang phải
        print_btn_layout.addWidget(print_btn)

        drug_layout.addLayout(print_btn_layout)

        return drug_layout



