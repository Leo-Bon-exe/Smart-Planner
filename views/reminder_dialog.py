from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QTimeEdit, QTextEdit, QComboBox, QPushButton
from PyQt5.QtCore import QTime

class ReminderDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Hatırlatıcı")
        self.setMinimumWidth(300)
        self.deleted = False
        layout = QVBoxLayout()

        # Başlık
        layout.addWidget(QLabel("Başlık:"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # Açıklama
        layout.addWidget(QLabel("Açıklama:"))
        self.desc_input = QTextEdit()
        layout.addWidget(self.desc_input)

        # Saat
        layout.addWidget(QLabel("Saat:"))
        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("HH:mm")
        self.time_input.setTime(QTime.currentTime())
        layout.addWidget(self.time_input)


        #sil butonu
        self.delete_btn = QPushButton("Sil")
        layout.addWidget(self.delete_btn)
        # Kaydet Butonu
        self.save_btn = QPushButton("Kaydet")
        layout.addWidget(self.save_btn)
        self.delete_btn.setAutoDefault(False)
        self.delete_btn.setDefault(False)

        self.save_btn.setAutoDefault(False)
        self.save_btn.setDefault(False)

        self.setLayout(layout)

        # Eğer güncelleme modundaysa, verileri doldur
        if data:
            self.title_input.setText(data["title"])
            self.desc_input.setPlainText(data["description"])
            self.time_input.setTime(QTime.fromString(data["time"], "HH:mm"))

            # ✨ Silme sinyali
        self.delete_btn.clicked.connect(self.handle_delete)

    def handle_delete(self):
        # reject normalde dialogu kapatır ama
        # buna true-false kontrolu eklersek kapanırken aynı zamanda silme işlemini de
        # gerçekleştirmiş oluruz
        self.deleted = True
        self.reject()

    def get_data(self):
        return {
            "title": self.title_input.text(),
            "description": self.desc_input.toPlainText(),
            "time": self.time_input.time().toString("HH:mm")
        }
