# BVGD_Project/src/app/ui/main_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from app.ui.tab_kham_suc_khoe import TabKhamSucKhoe
from app.ui.tab_khoa_duoc import TabKhoaDuoc
from app.ui.tab_tiep_nhan_benh_nhan import TabTiepNhanBenhNhan
from app.ui.tab_vien_phi import TabVienPhi


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BVGD_Project")
        self.setGeometry(0, 0, 1366, 768)

        # 1. Init QTabWidget
        self.tabs = QTabWidget()

        # 2. Add sub tab to QTabWidget in MainWindow
        self.tabs.addTab(TabTiepNhanBenhNhan(), "Tiếp nhận bệnh nhân")
        self.tabs.addTab(TabKhamSucKhoe(), "Khám sức khoẻ")
        self.tabs.addTab(TabVienPhi(), "Viện phí")
        self.tabs.addTab(TabKhoaDuoc(), "Khoa dược")

        # 3. Thiết lập Layout chính
        layout_chinh = QVBoxLayout(self)
        layout_chinh.addWidget(self.tabs)
        self.setLayout(layout_chinh)

