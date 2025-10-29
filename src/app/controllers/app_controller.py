import sys
from PyQt6 import QtWidgets, QtCore

# Import UI cha
from app.ui.MainWindow import Ui_mainWidget
# Import Controller con
from app.controllers.kham_benh_controller import KhamBenhTabController


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

        # Áp dụng Stylesheet cho QTabWidget
        self._apply_tab_stylesheet()

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
        """
        self.ui_main.tabWidget.setStyleSheet(stylesheet)
