import sys
import os
import winreg
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QCalendarWidget, QLabel, QDialog, QMessageBox,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QTextCharFormat, QColor  # <-- EKLENDİ
from PyQt5.QtCore import QDate, QTime, QTimer, QSettings

from models.reminder_model import ReminderDB
from views.add_reminder_dialog import AddReminderDialog
from views.reminder_dialog import ReminderDialog


class SmartPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Planner")
        self.setWindowIcon(self.load_icon("icon.ico"))
        self.setGeometry(100, 100, 800, 500)

        self.db = ReminderDB()
        self.notified_ids = set()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.date_selected)
        main_layout.addWidget(self.calendar, 2)

        right_panel = QVBoxLayout()
        self.label = QLabel("Hatırlatıcılar")
        self.label.setStyleSheet("font-size: 18px;")
        right_panel.addWidget(self.label)

        self.reminder_list = QListWidget()
        self.reminder_list.itemDoubleClicked.connect(self.edit_selected_reminder)
        right_panel.addWidget(self.reminder_list, 8)

        self.add_btn = QPushButton("➕ Yeni Hatırlatıcı")
        self.add_btn.clicked.connect(self.open_add_reminder_dialog)


        right_panel.addWidget(self.add_btn)


        main_layout.addLayout(right_panel, 3)

        self.date_selected(self.calendar.selectedDate())
        self.highlight_reminder_days()  # <-- EKLENDİ
        self.create_tray_icon()
        self.create_settings_menu()
        self.start_reminder_checker()

    def create_settings_menu(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("⚙️ Ayarlar")

        self.startup_action = QAction("Launch on startup", self, checkable=True)
        self.startup_action.setChecked(self.is_in_startup())
        self.startup_action.triggered.connect(self.toggle_startup)
        settings_menu.addAction(self.startup_action)

        self.minimize_on_close_action = QAction("Minimize instead of closing", self, checkable=True)
        self.minimize_on_close_action.setChecked(self.get_minimize_on_close_setting())
        self.minimize_on_close_action.triggered.connect(self.toggle_minimize_on_close)
        settings_menu.addAction(self.minimize_on_close_action)

    def get_minimize_on_close_setting(self):
        settings = QSettings("SmartPlanner", "SmartPlanner")
        return settings.value("minimize_on_close", False, type=bool)

    def toggle_minimize_on_close(self):
        settings = QSettings("SmartPlanner", "SmartPlanner")
        settings.setValue("minimize_on_close", self.minimize_on_close_action.isChecked())

    def closeEvent(self, event):
        if self.get_minimize_on_close_setting():
            event.ignore()
            self.hide()
        else:
            self.exit_completely()

    def load_icon(self, icon_name):
        """Hem EXE hem de script modunda ikon yüklemek için"""
        # EXE veya script modunda doğru yolu bul
        # exe de icon.png sorunu böyle çözüldü
        # ve pyinstaller --onefile --windowed --add-data "icon.png;." --noconsole main.py
        # add data ile oluyor exe yapılırken
        if getattr(sys, 'frozen', False):
            # EXE modunda geçici klasördeki ikonu kullan
            base_path = sys._MEIPASS
        else:
            # Script modunda normal klasördeki ikonu kullan
            base_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_path, icon_name)

        # İkon yoksa uyarı ver
        if not os.path.exists(icon_path):
            print(f"Uyarı: İkon dosyası bulunamadı - {icon_path}")
            return QIcon()  # Boş ikon

        return QIcon(icon_path)

    def create_tray_icon(self):


        self.tray_icon = QSystemTrayIcon(self.load_icon("icon.ico"), self)
        self.tray_icon.setToolTip("Smart Planner")


        self.tray_menu = QMenu(self)

        restore_action = QAction("Uygulamayı Göster", self)
        restore_action.triggered.connect(self.show_main_window)
        self.tray_menu.addAction(restore_action)

        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.exit_completely)
        self.tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.icon_activated)
        self.tray_icon.show()

    def icon_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_main_window()

    def show_main_window(self):
        self.showNormal()
        self.activateWindow()

    def exit_completely(self):
        self.tray_icon.hide()
        QApplication.quit()

    def date_selected(self, date: QDate):
        selected_date = date.toString("yyyy-MM-dd")
        self.reminder_list.clear()
        reminders = self.db.get_reminders_by_date(selected_date)
        for reminder in reminders:
            item_id, title, time = reminder
            item_text = f"{time} - {title}"
            self.reminder_list.addItem(item_text)
            self.reminder_list.item(self.reminder_list.count() - 1).setData(1000, item_id)
        self.highlight_reminder_days()  # <-- EKLENDİ

    def open_add_reminder_dialog(self):
        selected_date = self.calendar.selectedDate()  # takvimdeki gün
        dialog = AddReminderDialog(selected_date=selected_date)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.reminder_data
            self.db.conn.execute(
                "INSERT INTO reminders (title, description, date, time) VALUES (?, ?, ?, ?)",
                (data["title"], data["description"], data["date"], data["time"])
            )
            self.db.conn.commit()
            self.date_selected(QDate.fromString(data["date"], "yyyy-MM-dd"))
            self.highlight_reminder_days()  # <-- EKLENDİ



    def edit_selected_reminder(self, selected_item):
        if not selected_item:
            return
        item_id = selected_item.data(1000)
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT title, description, time FROM reminders WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return
        title, description, time = row
        dialog = ReminderDialog(self, data={
            "title": title,
            "description": description,
            "time": time,
        })
        dialog.save_btn.clicked.connect(dialog.accept)
        result = dialog.exec_()

        if dialog.deleted:
            self.db.conn.execute("DELETE FROM reminders WHERE id = ?", (item_id,))
            self.db.conn.commit()

        elif result == QDialog.Accepted:
            updated_data = dialog.get_data()
            self.db.conn.execute("""
                        UPDATE reminders
                        SET title = ?, description = ?, time = ?
                        WHERE id = ?
                    """, (
                updated_data["title"],
                updated_data["description"],
                updated_data["time"],
                item_id
            ))
            self.db.conn.commit()

        self.date_selected(self.calendar.selectedDate())

    def start_reminder_checker(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_reminders)
        self.timer.start(60 * 1000)

    def check_reminders(self):
        current_date = QDate.currentDate().toString("yyyy-MM-dd")
        current_time = QTime.currentTime().toString("HH:mm")
        reminders = self.db.get_reminders_by_date(current_date)
        for reminder in reminders:
            item_id, title, time = reminder
            if time == current_time and item_id not in self.notified_ids:
                self.tray_icon.showMessage(
                    f"Hatırlatıcı: {title}",
                    f"{current_time} saatinde planladığınız etkinlik.",
                    QSystemTrayIcon.Information,
                    5000
                )
                self.notified_ids.add(item_id)

    def toggle_startup(self, checked):
        if checked:
            self.add_to_startup()
        else:
            self.remove_from_startup()

    def add_to_startup(self, app_name="SmartPlanner"):
        if not getattr(sys, 'frozen', False):
            print("EXE değil, başlangıca eklenmeyecek.")
            return

        exe_path = sys.executable  # Gerçek .exe yolu
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
        winreg.CloseKey(key)

    def remove_from_startup(self, app_name="SmartPlanner"):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        try:
            winreg.DeleteValue(key, app_name)
        except FileNotFoundError:
            pass
        winreg.CloseKey(key)

    def is_in_startup(self, app_name="SmartPlanner"):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            _, _ = winreg.QueryValueEx(key, app_name)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    # ⬇️ EKLENDİ: Takvimde hatırlatıcı olan günleri yeşile boyar
    def highlight_reminder_days(self):
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())  # Önce tüm biçimleri temizle
        reminders = self.db.get_all_reminder_dates()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#4CAF50"))  # Yeşil

        for date_str in reminders:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.calendar.setDateTextFormat(date, fmt)