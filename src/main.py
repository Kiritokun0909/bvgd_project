# BVGD_Project/src/main.py

import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()   # Init main window
    window.show()   # Show the window
    sys.exit(app.exec())

if __name__ == '__main__':
    main()