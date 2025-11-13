from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMessageBox
from PyQt6.uic.Compiler.qtproxies import QtGui

from app.controllers.dich_vu_controller import DangKyDichVuTabController
from app.controllers.tai_vu_controller import TaiVuTabController
# Import UI cha
from app.ui.MainWindow import Ui_mainWidget
# Import Controller con
from app.controllers.kham_benh_controller import KhamBenhTabController

from app.utils.constants import CLS_CODE


class AppController(QtWidgets.QWidget):
    """
    Controller chính của ứng dụng. Quản lý cửa sổ và các tab.
    """

    def __init__(self):
        super().__init__()

        # Set up the main window UI into this widget
        self.ui_main = Ui_mainWidget()
        self.ui_main.setupUi(self)

        # Khởi tạo Controller cho tab Khám bệnh
        # self.ui_main.tabKhamBenh là container QWidget rỗng cho tab "Khám bệnh"
        self.kham_benh_controller = KhamBenhTabController(
            tab_widget_container=self.ui_main.tab_kham_benh
        )

        self.dich_vu_controller = DangKyDichVuTabController(
            tab_widget_container=self.ui_main.tab_dkdv
        )

        self.tai_vu_controller = TaiVuTabController(
            tab_widget_container=self.ui_main.tab_tai_vu
        )

        # Áp dụng Stylesheet cho QTabWidget
        self._apply_tab_stylesheet()

        self.dich_vu_controller.dich_vu_completed.connect(self.handle_dich_vu_completed)

        self.ui_main.tabWidget.setCurrentIndex(0)
        self.showMaximized()


    def _apply_tab_stylesheet(self):
        """Áp dụng stylesheet cho QTabWidget."""
        stylesheet = """
        QTabBar::tab {
            background-color: #E0E0E0;
            color: black;
            padding: 8px;
            border: 1px solid #C4C4C3;
            border-bottom: none; 
        }
        QTabBar::tab:hover {
            background-color: #ADD8E6;
        }
        QTabBar::tab:selected {
            background-color: white;
            color: #0078D4;
            font-weight: bold;
        }
        
        QTabWidget {
            /* Đặt màu nền bằng mã hex (ví dụ: Light Blue) */
            background-color: #ADD8E6; 
        }
        
        QLineEdit, QComboBox,QDateEdit, QDateTimeEdit {
            /* Cài đặt Mặc định */
            background-color: white; /* Màu nền xanh nhạt (AliceBlue) */
            border: 2px solid #ccc; /* Viền xám nhạt */
            border-radius: 5px; /* Bo tròn góc */
            padding: 4px; /* Khoảng cách bên trong */
            font-size: 14px;
        }
        
        QLineEdit:hover, 
        QComboBox:hover {
            /* Khi con trỏ chuột di vào */
            border: 2px solid #a8a8a8; /* Viền sẫm hơn một chút */
        }
        
        QLineEdit:focus, 
        QComboBox:focus,
        QDateEdit:focus {
            /* Khi QLineEdit nhận focus (đang gõ) */
            border: 3px solid blue; /* Viền màu xanh lá đậm */
            background-color: white; /* Nền trắng để nổi bật */
        }
        
        QLineEdit:read-only, 
        QComboBox:read-only,
        QDateTimeEdit:read-only {
            /* Khi QLineEdit chỉ đọc (dùng setReadOnly(True)) */
            background-color: #f0f8ff; /* Nền xám để báo hiệu không thể chỉnh sửa */
            color: #555;
        }
        """
        self.ui_main.tabWidget.setStyleSheet(stylesheet)


    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """Xử lý sự kiện nhấn phím toàn cục."""
        if event.key() == QtCore.Qt.Key.Key_F5:
            current_index = self.ui_main.tabWidget.currentIndex()
            kham_benh_tab_index = 0

            if current_index == kham_benh_tab_index:
                self.handle_f5_shortcut()

        super().keyPressEvent(event)


    def handle_f5_shortcut(self):
        """Xử lý chuyển đổi sang Đăng ký Dịch vụ khi nhấn F5."""

        # 1. Thu thập dữ liệu hành chính
        hanh_chinh_data = self.kham_benh_controller.get_hanh_chinh_data()

        # 2. KIỂM TRA ĐIỀU KIỆN CẬN LÂM SÀNG
        if not self.kham_benh_controller.validate_patient_info():
            return


        cach_giai_quyet_code = hanh_chinh_data.get('MaGiaiQuyet')

        if cach_giai_quyet_code != CLS_CODE:
            QMessageBox.warning(self,
                                "Thông báo",
                                f"Chỉ chuyển màn hình khi Cách Giải Quyết là 'Cận Lâm Sàng'.")
            return

        # 3. Chuyển tab và truyền dữ liệu
        dich_vu_tab_index = 1

        if self.ui_main.tabWidget.count() > dich_vu_tab_index:
            self.dich_vu_controller.load_thong_tin_benh_nhan(hanh_chinh_data)
            self.ui_main.tabWidget.setCurrentIndex(dich_vu_tab_index)
        else:
            QMessageBox.critical(self, "Lỗi", "Tab Đăng ký Dịch vụ không tồn tại.")


    @QtCore.pyqtSlot()
    def handle_dich_vu_completed(self):
        """Slot được gọi khi tab Dịch vụ hoàn tất công việc."""

        kham_benh_tab_index = 0

        # 2. Quay về Tab Khám bệnh (index 0)
        if self.ui_main.tabWidget.currentIndex() != kham_benh_tab_index:
            self.ui_main.tabWidget.setCurrentIndex(kham_benh_tab_index)

        # TODO: Nếu cần, bạn có thể gọi hàm refresh_data() của kham_benh_controller ở đây
        self.kham_benh_controller.reset_all()