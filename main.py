import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from core.launcher import Launcher

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    
    window = Launcher()  # noqa: F841
    sys.exit(app.exec())

if __name__ == "__main__":
    main()