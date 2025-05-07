from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QTextEdit, QDateEdit, QTimeEdit, QComboBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import QDate, QTime

class AddReminderDialog(QDialog):
    def __init__(self, selected_date=None):
        super().__init__()
        self.setWindowTitle("Yeni Hatırlatıcı Ekle")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Başlık Girişi
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Hatırlatıcı başlığı...")
        layout.addWidget(QLabel("Başlık:"))
        layout.addWidget(self.title_input)

        # Açıklama Girişi
        self.description_input = QTextEdit()
        layout.addWidget(QLabel("Açıklama:"))
        layout.addWidget(self.description_input)

        # Tarih Seçimi (sadece gösterim amaçlı, değiştirilemez)
        self.date_display = QLabel()
        layout.addWidget(QLabel("Tarih:"))
        layout.addWidget(self.date_display)

        # Saat Seçimi
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        layout.addWidget(QLabel("Saat:"))
        layout.addWidget(self.time_input)


        # Kaydet Butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save_reminder)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Gelen tarihi sakla ve göster
        self.selected_date = selected_date if selected_date else QDate.currentDate()
        self.date_display.setText(self.selected_date.toString("dd.MM.yyyy"))

        self.reminder_data = None

    def save_reminder(self):
        title = self.title_input.text()
        description = self.description_input.toPlainText()
        time = self.time_input.time().toString("HH:mm")


        # Başlık boşsa uyarı ver
        if not title:
            QMessageBox.warning(self, "Eksik bilgi", "Lütfen başlık girin.")
            return

        self.reminder_data = {
            "title": title,
            "description": description,
            "date": self.selected_date.toString("yyyy-MM-dd"),  # Tarihi stringe çevir
            "time": time
        }
        self.accept()


