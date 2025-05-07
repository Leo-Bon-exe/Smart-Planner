import sys

from PyQt5.QtWidgets import QApplication

from app.smart_planner import SmartPlanner

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartPlanner()

    if "--minimized" in sys.argv:
        window.hide()
    else:
        window.show()

    sys.exit(app.exec_())
