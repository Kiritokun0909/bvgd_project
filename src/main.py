import sys
from PyQt6 import QtWidgets

from app.controllers.app_controller import AppController

def main(argv):
    app = QtWidgets.QApplication(argv)
    window = AppController()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
