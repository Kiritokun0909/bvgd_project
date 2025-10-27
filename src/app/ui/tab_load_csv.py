# ten_ung_dung/ui/tab_load_csv.py

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from app.core.data_manager import load_csv_data  # Nhập logic nghiệp vụ


class TabLoadCSV(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.status_label = QLabel("Chờ tải dữ liệu...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.status_label)

        self.data_loaded_once = False
        self.csv_path = "data/danh_muc.csv"  # Đường dẫn tệp CSV

    def auto_load_data(self):
        """Tự động tải dữ liệu khi tab được chọn lần đầu."""
        if not self.data_loaded_once:
            self.status_label.setText(f"Đang tải {self.csv_path}...")

            # 1. Gọi hàm nghiệp vụ để lấy dữ liệu
            headers, rows = load_csv_data(self.csv_path)

            if headers:
                # 2. Điền dữ liệu vào bảng (Logic UI)
                self.populate_table(headers, rows)
                self.data_loaded_once = True
                self.status_label.setText(f"Đã tải thành công {len(rows)} dòng.")
            elif rows == []:
                self.status_label.setText("Tệp CSV trống hoặc không tìm thấy.")
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể tải dữ liệu danh mục.")
                self.status_label.setText("Lỗi khi tải dữ liệu.")

    def populate_table(self, headers: list[str], rows: list[list[str]]):
        """Thiết lập header và điền dữ liệu vào QTableWidget."""

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):
            for col_index, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table.setItem(row_index, col_index, item)

        # Tự động điều chỉnh độ rộng cột
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)