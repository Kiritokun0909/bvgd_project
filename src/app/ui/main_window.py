# ten_ung_dung/ui/main_window.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

# Import tab ui (home, settings, v.v...)
from app.ui.tab_load_csv import TabLoadCSV
from app.ui.tab_save_csv import TabSaveCSV
from app.ui.tab_tiep_nhan_benh_nhan import TabTiepNhanBenhNhan


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BVGD_Project")
        self.setGeometry(0, 0, 1366, 768)

        # 1. Init QTabWidget
        self.tabs = QTabWidget()

        # 2. Add sub tab to QTabWidget in MainWindow
        self.tabs.addTab(TabTiepNhanBenhNhan(), "⭐ Tiếp nhận bệnh nhân")
        self.tabs.addTab(QWidget(), "🏠 Trang Chủ")
        self.tabs.addTab(QWidget(), "⚙️ Cài Đặt")

        # Tabs CSV
        self.tab_load = TabLoadCSV()
        self.tab_save = TabSaveCSV()

        self.index_load_csv = self.tabs.addTab(self.tab_load, "📁 Xem Danh Mục")
        self.tabs.addTab(self.tab_save, "👤 Nhập Thông Tin")

        # 3. Kết nối tín hiệu cho Lazy Loading
        self.tabs.currentChanged.connect(self.handle_tab_change)

        # 4. Thiết lập Layout chính
        layout_chinh = QVBoxLayout(self)
        layout_chinh.addWidget(self.tabs)
        self.setLayout(layout_chinh)

    def handle_tab_change(self, index: int):
        """Xử lý sự kiện khi người dùng chuyển tab."""
        if index == self.index_load_csv:
            # Gọi phương thức của lớp tab cụ thể để tự động tải
            self.tab_load.auto_load_data()