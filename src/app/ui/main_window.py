# BVGD_Project/src/app/ui/main_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.ui.tab_kham_benh_nhanh import TabKhamBenhNhanh
from app.ui.tab_khoa_duoc import TabKhoaDuoc
from app.ui.tab_tiep_nhan_benh_nhan import TabTiepNhanBenhNhan
from app.ui.tab_vien_phi import TabVienPhi

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Khởi tạo màn hình ứng dụng với tiêu đề và kích thước ban đầu
        self.setWindowTitle("BVGD_Project")
        self.setGeometry(0, 0, 1366, 768)

        # 1. Khởi tạo QWidget chứa các tabs
        self.tabs = QTabWidget()

        # 2. Thêm các tab con vào QWidget ở bước 1
        self.tabs.addTab(TabKhamBenhNhanh(), "Khám sức khoẻ")
        self.tabs.addTab(TabTiepNhanBenhNhan(), "Tiếp nhận bệnh nhân")
        self.tabs.addTab(TabVienPhi(), "Viện phí")
        self.tabs.addTab(TabKhoaDuoc(), "Khoa dược")

        # 3. Tạo layout chính và thêm QWidget chứa các tabs vào layout đó
        layout_chinh = QVBoxLayout(self)
        layout_chinh.addWidget(self.tabs)

        # 4. Set layout chính vào màn hình chính
        self.setLayout(layout_chinh)

# BVGD_Project/src/main.py
import sys
from PyQt6.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()   # Init main window
    window.show()   # Show the window
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

