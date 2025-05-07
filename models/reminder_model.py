import sqlite3
import os
import sys


def get_app_dir():
    if getattr(sys, 'frozen', False):  # PyInstaller ile derlendiyse
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(get_app_dir(), "reminders.db")

class ReminderDB:
    def __init__(self):
        # Veritabanı bağlantısı kur
        self.conn = sqlite3.connect(DB_NAME)
        # Uygulama başlatıldığında tabloyu oluştur (varsa geç)
        self.create_table()

    def create_table(self):
        # Veritabanı tablosunu oluştur (yoksa)
        query = """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Otomatik artan ID
            title TEXT NOT NULL,                    -- Görev başlığı
            description TEXT,                       -- Açıklama (opsiyonel)
            date TEXT NOT NULL,                     -- Tarih (YYYY-MM-DD)
            time TEXT NOT NULL                     -- Saat (HH:MM)

        )
        """
        # SQL komutunu çalıştır ve kaydet
        self.conn.execute(query)
        self.conn.commit()

    def get_reminders_by_date(self, date_str):
        # Verilen tarihe göre hatırlatıcıları getir (saat sırasına göre)
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, time FROM reminders WHERE date = ? ORDER BY time", (date_str,))
        return cursor.fetchall()

    def get_all_reminder_dates(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT date FROM reminders")
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        # Veritabanı bağlantısını kapat
        self.conn.close()
