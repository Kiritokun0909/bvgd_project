# ten_ung_dung/ui/tab_save_csv.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from app.core.data_manager import save_csv_data  # Nhập logic nghiệp vụ
from typing import List


class TabSaveCSV(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.csv_path = "data/data_ca_nhan.csv"  # Đường dẫn tệp lưu

        self.fields = {
            "Họ và Tên": QLineEdit(),
            "Tuổi": QLineEdit(),
            "Email": QLineEdit(),
            "Số Điện Thoại": QLineEdit()
        }
        self.headers = list(self.fields.keys())  # Dùng làm header cho CSV

        # Tạo layout lưới cho các trường nhập liệu
        grid = QGridLayout()
        row = 0
        for label_text, line_edit in self.fields.items():
            grid.addWidget(QLabel(f"{label_text}:"), row, 0)
            grid.addWidget(line_edit, row, 1)
            row += 1

        nut_luu = QPushButton("Lưu Thông Tin")
        nut_luu.setStyleSheet("background-color: #2ECC71; color: white; padding: 10px;")
        nut_luu.clicked.connect(self.save_data)

        self.layout.addLayout(grid)
        self.layout.addWidget(nut_luu)
        self.layout.addStretch(1)

    def save_data(self):
        """Lấy dữ liệu từ UI và gọi hàm lưu nghiệp vụ."""

        data_row: List[str] = [field.text() for field in self.fields.values()]

        if any(not d for d in data_row):
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng điền đầy đủ thông tin.")
            return

        # 1. Gọi hàm nghiệp vụ để lưu
        success = save_csv_data(self.csv_path, data_row, headers=self.headers)

        if success:
            QMessageBox.information(self, "Thành công", f"Đã lưu thông tin vào tệp {self.csv_path}.")
            # Xóa các trường sau khi lưu
            for field in self.fields.values():
                field.clear()
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu dữ liệu.")