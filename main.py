import sys
import sqlite3
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QStackedWidget, QFormLayout, QInputDialog, QDateEdit, QSpinBox, QComboBox
from PyQt5.QtCore import pyqtSlot, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giriş Yap")
        self.setGeometry(100, 100, 280, 150)
        
        layout = QVBoxLayout()
        self.username = QLineEdit(self)
        self.username.setPlaceholderText('Kullanıcı Adı')
        self.password = QLineEdit(self)
        self.password.setPlaceholderText('Şifre')
        self.password.setEchoMode(QLineEdit.Password)
        
        self.button_login = QPushButton('Giriş Yap', self)
        self.button_login.clicked.connect(self.check_password)
        self.button_create = QPushButton('Hesap Oluştur', self)
        self.button_create.clicked.connect(self.create_account)
        
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.button_login)
        layout.addWidget(self.button_create)
        
        self.setLayout(layout)
    
    @pyqtSlot()
    def check_password(self):
        username = self.username.text()
        password = self.password.text()
        
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        query = "SELECT * FROM users WHERE username=? AND password=?"
        c.execute(query, (username, password))
        result = c.fetchone()
        conn.close()
        
        if result:
            self.main_window = MainWindow(result[0])
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, 'Hata', 'Yanlış kullanıcı adı veya şifre!', QMessageBox.Ok)

    def create_account(self):
        username = self.username.text()
        password = self.password.text()
        
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        query = "INSERT INTO users (username, password) VALUES (?, ?)"
        try:
            c.execute(query, (username, password))
            conn.commit()
            QMessageBox.information(self, 'Başarılı', 'Hesap başarıyla oluşturuldu!', QMessageBox.Ok)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, 'Hata', 'Bu kullanıcı adı zaten kullanımda!', QMessageBox.Ok)
        conn.close()


class MainWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Sağlıklı Yaşam Takip Uygulaması")
        self.setGeometry(100, 100, 400, 600)
        
        # Ana widget ve layout
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.layout = QVBoxLayout()
        
        self.stacked_widget = QStackedWidget()
        self.dashboard = Dashboard(self.user_id)
        self.stacked_widget.addWidget(self.dashboard)
        self.nutrition_tracker = NutritionTracker(self.user_id)
        self.stacked_widget.addWidget(self.nutrition_tracker)
        self.exercise_tracker = ExerciseTracker(self.user_id)
        self.stacked_widget.addWidget(self.exercise_tracker)
        self.finance_tracker = FinanceTracker(self.user_id)
        self.stacked_widget.addWidget(self.finance_tracker)
        self.health_goals = HealthGoals(self.user_id)
        self.stacked_widget.addWidget(self.health_goals)

        self.layout.addWidget(self.stacked_widget)
        self.widget.setLayout(self.layout)


class Dashboard(QWidget):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        
        self.layout = QVBoxLayout()
        self.label = QLabel("Sağlık Özeti ve Kontroller")
        self.layout.addWidget(self.label)
        
        self.setupUI()
        self.health_data_summary()
        
        self.setLayout(self.layout)
                # Form Erişim Butonları
        self.btn_open_nutrition_tracker = QPushButton("Besin Ekle")
        self.btn_open_exercise_tracker = QPushButton("Egzersiz Ekle")
        self.btn_open_finance_tracker = QPushButton("Mali Veri Ekle")
        self.btn_open_goals = QPushButton("Hedefler")
        
        # Buton Bağlantıları
        self.btn_open_nutrition_tracker.clicked.connect(self.openNutritionTracker)
        self.btn_open_exercise_tracker.clicked.connect(self.openExerciseTracker)
        self.btn_open_finance_tracker.clicked.connect(self.openFinanceTracker)
        self.btn_open_goals.clicked.connect(self.openGoalTracker)

        # Butonların Eklenmesi
        self.layout.addWidget(self.btn_open_nutrition_tracker)
        self.layout.addWidget(self.btn_open_exercise_tracker)
        self.layout.addWidget(self.btn_open_finance_tracker)
        self.layout.addWidget(self.btn_open_goals)

        self.setLayout(self.layout)
    
    # Buton Fonksiyonları
    def openNutritionTracker(self):
        self.dialog = NutritionTracker(self.user_id)
        self.dialog.setWindowTitle("Besin Takibi")
        self.dialog.setFixedSize(400, 300)  # Boyut ayarlaması
        self.dialog.exec_()  # Dialog olarak aç
        self.update_health_data() 
    
    def openExerciseTracker(self):
        self.dialog = ExerciseTracker(self.user_id)
        self.dialog.setWindowTitle("Egzersiz Takibi")
        self.dialog.setFixedSize(400, 300)  # Boyut ayarlaması
        self.dialog.exec_()  # Dialog olarak aç
        self.updateExerciseData() 
        self.updateHealthReports()

    def openFinanceTracker(self):
        self.dialog = FinanceTracker(self.user_id)
        self.dialog.setWindowTitle("Mali Takip")
        self.dialog.setFixedSize(400, 300)  # Boyut ayarlaması
        self.dialog.exec_()  # Dialog olarak aç
        self.updateFinanceData()

    def openGoalTracker(self):
        self.dialog = HealthGoals(self.user_id)
        self.dialog.setWindowTitle("Hedefler")
        self.dialog.setFixedSize(400, 300)  # Boyut ayarlaması
        self.dialog.exec_()  # Dialog olarak aç
        self.updateHealthReports()
        self.updateExerciseData()

    def setupUI(self):
        # Tarih Seçici
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.layout.addWidget(self.date_edit)
        
        # Adım, Su ve Kalori için Giriş Alanları
        self.step_input = QLineEdit()
        self.step_input.setPlaceholderText("Adım sayısı giriniz")
        self.water_input = QLineEdit()
        self.water_input.setPlaceholderText("İçilen su miktarını ml olarak giriniz")
        self.calory_input = QLineEdit()
        self.calory_input.setPlaceholderText("Alınan kalori miktarını giriniz")
        
        # Giriş Alanlarının Layout'a Eklenmesi
        self.layout.addWidget(self.step_input)
        self.layout.addWidget(self.water_input)
        self.layout.addWidget(self.calory_input)
        
        # Veri Ekleme Butonları
        self.add_steps_button = QPushButton("Adım Ekle")
        self.add_steps_button.clicked.connect(self.add_steps)
        self.add_water_button = QPushButton("Su Ekle")
        self.add_water_button.clicked.connect(self.add_water)
        self.add_calory_button = QPushButton("Kalori Ekle")
        self.add_calory_button.clicked.connect(self.add_calories)
        
        # Butonların Layout'a Eklenmesi
        self.layout.addWidget(self.add_steps_button)
        self.layout.addWidget(self.add_water_button)
        self.layout.addWidget(self.add_calory_button)


    def health_data_summary(self):
        self.steps_label = QLabel("Bugünün verileri yükleniyor...")
        self.layout.addWidget(self.steps_label)
        
        self.exercise_label = QLabel("Bugünkü egzersiz bilgisi yükleniyor...")
        self.layout.addWidget(self.exercise_label)
        self.finance_label = QLabel("Bugünkü finansal durum yükleniyor...")
        self.layout.addWidget(self.finance_label)

        self.health_report_label = QLabel("Aylık durum yükleniyor...")
        self.layout.addWidget(self.health_report_label)

        self.update_health_data()
        self.updateExerciseData()
        self.updateFinanceData()
        self.updateHealthReports()

    def add_steps(self):
        steps = self.step_input.text()
        if steps.isdigit():
            self.insert_data('steps', int(steps))
            self.step_input.clear()
            self.update_health_data()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen geçerli bir adım sayısı girin!', QMessageBox.Ok)

    def add_water(self):
        water = self.water_input.text()
        if water.isdigit():
            self.insert_data('water_intake', int(water))
            self.water_input.clear()
            self.update_health_data()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen geçerli bir su miktarı girin!', QMessageBox.Ok)

    def add_calories(self):
        calories = self.calory_input.text()
        if calories.isdigit():
            self.insert_data('calory_intake', int(calories))
            self.calory_input.clear()
            self.update_health_data()
        else:
            QMessageBox.warning(self, 'Hata', 'Lütfen geçerli bir kalori miktarı girin!', QMessageBox.Ok)

    def insert_data(self, field, value):
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = self.date_edit.date().toString("yyyy-MM-dd")
        
        c.execute(f"INSERT INTO health_data (user_id, date, {field}) VALUES (?, ?, ?) ON CONFLICT(user_id, date) DO UPDATE SET {field} = {field} + ?",
                  (self.user_id, today, value, value))
        conn.commit()
        conn.close()

    def update_health_data(self):
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = self.date_edit.date().toString("yyyy-MM-dd")

        c.execute("SELECT steps, water_intake, calory_intake FROM health_data WHERE user_id = ? AND date = ?", (self.user_id, today))
        record = c.fetchone()
        
        if record:
            self.steps_label.setText(f"Bugün\nAdım Sayısı: {record[0] or 0}\nSu tüketimi: {record[1] or 0} mL\nKalori alımı: {record[2] or 0} kcal")

        else:
            self.steps_label.setText("Bugün\nAdım Sayısı: Veri yok \nSu Tüketimi: Veri yok\nKalori Alımı: Veri Yok")

        
        conn.close()
    
    def updateExerciseData(self):
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")

        c.execute("""
            SELECT exercise_name, duration, calories_burned 
            FROM exercise_records 
            WHERE user_id = ? AND date = ?
        """, (self.user_id, today))

        exercises = c.fetchall()
        exercise_info = "Bugünkü egzersiz bilgisi:\n"
        if exercises:
            for exercise in exercises:
                exercise_info += f"{exercise[0]} - Süre: {exercise[1]} dakika, Yakılan kalori: {exercise[2]} kcal\n"
        else:
            exercise_info = "Bugünkü egzersiz bilgisi: Kayıt Yok"

        self.exercise_label.setText(exercise_info)
        conn.close()
    
    def updateFinanceData(self):
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")

        # Gelirler
        c.execute("""
            SELECT SUM(amount) 
            FROM financial_records 
            WHERE user_id = ? AND date = ? AND is_income = 1
        """, (self.user_id, today))
        total_income = c.fetchone()[0] or 0

        # Giderler
        c.execute("""
            SELECT SUM(amount) 
            FROM financial_records 
            WHERE user_id = ? AND date = ? AND is_income = 0
        """, (self.user_id, today))
        total_expense = c.fetchone()[0] or 0

        finance_info = f"Bugünkü finansal durum:\nGelir: {total_income} \nGider: {total_expense} \nNet: {total_income - total_expense}"
        self.finance_label.setText(finance_info)
        conn.close()


    def updateHealthReports(self):
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        month = QDate.currentDate().toString("MM")
        year = QDate.currentDate().toString("yyyy")

        # Ay boyunca yapılan egzersizler ve yakılan kaloriler için SQL sorguları...
        c.execute("""
            SELECT SUM(duration), SUM(calories_burned)
            FROM exercise_records
            WHERE user_id = ? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        """, (self.user_id, month, year))
        exercise_results = c.fetchone()

        exercise_minutes, calories_burned = exercise_results if exercise_results else (0, 0)

        # Kullanıcının ay için hedeflerini çekme
        c.execute("""SELECT calorie_goal, exercise_minutes_goal FROM health_goals
                    WHERE user_id = ?""", (self.user_id,))
        goals_results = c.fetchone()
        calorie_goal, exercise_minutes_goal = goals_results if goals_results else (0, 0)

        # Çekilen değerlerin None olup olmadığını kontrol edin ve None ise 0'a dönüştürün
        exercise_minutes = exercise_minutes if exercise_minutes is not None else 0
        calories_burned = calories_burned if calories_burned is not None else 0
        calorie_goal = calorie_goal if calorie_goal is not None else 0
        exercise_minutes_goal = exercise_minutes_goal if exercise_minutes_goal is not None else 0
        
        # Hedef karşılaştırmaları
        calories_left = calorie_goal - calories_burned
        exercise_minutes_left = exercise_minutes_goal - exercise_minutes
      
        
        msg_parts = [
            f"Bunları bu ay başardınız: {calories_burned} kcal yakıldı, {exercise_minutes} dakika egzersiz yapıldı.",
            f"Hedeflerinize kalan: {calories_left if calories_left > 0 else 0} kcal, {exercise_minutes_left if exercise_minutes_left > 0 else 0} dakika."
        ]

        self.health_report_label.setText(" ".join(msg_parts))
        conn.close()

class NutritionTracker(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Besin Takibi")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout(self)
        
        formLayout = QFormLayout()
        self.food_name = QLineEdit(self)
        self.servings = QLineEdit(self)
        self.calories = QLineEdit(self)
        
        formLayout.addRow(QLabel("Besin Adı:"), self.food_name)
        formLayout.addRow(QLabel("Porsiyon Sayısı:"), self.servings)
        formLayout.addRow(QLabel("Kalori (kcal):"), self.calories)
        
        self.btnAdd = QPushButton("Ekle", self)
        self.btnAdd.clicked.connect(self.addNutritionRecord)
        
        layout.addLayout(formLayout)
        layout.addWidget(self.btnAdd)
        
    @pyqtSlot()
    def addNutritionRecord(self):
        food_name = self.food_name.text()
        try:
            servings = int(self.servings.text())
            calories = int(self.calories.text())
        except ValueError:
            QMessageBox.warning(self, "Hatalı Giriş", "Porsiyon ve kalori alanları sayısal bir değer olmalıdır.")
            return

        # Veri girişi doğrulaması
        if not food_name or servings <= 0 or calories <= 0:
            QMessageBox.warning(self, "Hatalı Giriş", "Lütfen tüm alanları doğru bir şekilde doldurun.")
            return
        
        date = QDate.currentDate().toString("yyyy-MM-dd")
        total_calories = servings * calories

        try:
            conn = sqlite3.connect('health_tracker.db')
            c = conn.cursor()
            
            # Önce nutrition_records tablosuna kayıt ekleyin
            c.execute("""INSERT INTO nutrition_records (user_id, date, food_name, servings, calories) 
                        VALUES (?, ?, ?, ?, ?)""", 
                    (self.user_id, date, food_name, servings, total_calories))
            
            # Sonra, health_data tablosunu güncelleyin
            # Aynı gün için bir kayıt var mı diye kontrol edin
            c.execute("""SELECT calory_intake FROM health_data WHERE user_id = ? AND date = ?""", (self.user_id, date))
            result = c.fetchone()
            
            if result:
                new_calory_intake = result[0] + total_calories
                c.execute("""UPDATE health_data SET calory_intake = ? WHERE user_id = ? AND date = ?""", (new_calory_intake, self.user_id, date))
            else:
                c.execute("""INSERT INTO health_data (user_id, date, calory_intake) VALUES (?, ?, ?)""", (self.user_id, date, total_calories))
            
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Başarılı", "Besin bilgisi başarıyla eklendi.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Bir hatayla karşılaşıldı: {e}")


class ExerciseTracker(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setupUi()
        

    def setupUi(self):
            self.setWindowTitle("Egzersiz Takibi")
            self.setGeometry(100, 100, 400, 200)
        
            layout = QVBoxLayout(self)
            # Egzersiz Eklemek İçin Form
            form_layout = QFormLayout()
            self.exercise_name = QLineEdit()
            self.duration = QSpinBox()
            self.duration.setRange(0, 9999)
            self.calories_burned = QSpinBox()
            self.calories_burned.setRange(0, 9999)
            self.add_button = QPushButton("Egzersiz Ekle")
            self.add_button.clicked.connect(self.add_exercise_record)
            
            form_layout.addRow("Egzersiz Adı:", self.exercise_name)
            form_layout.addRow("Süre (dakika):", self.duration)
            form_layout.addRow("Yakılan Kalori:", self.calories_burned)
            form_layout.addRow(self.add_button)
            
            layout.addLayout(form_layout)
            
            self.setLayout(layout)

    @pyqtSlot()
    def add_exercise_record(self):
        exercise_name = self.exercise_name.text()
        duration = self.duration.value()
        calories_burned = self.calories_burned.value()
        
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        query = "INSERT INTO exercise_records (user_id, date, exercise_name, duration, calories_burned) VALUES (?, ?, ?, ?, ?)"
        try:
            c.execute(query, (self.user_id, today, exercise_name, duration, calories_burned))
            conn.commit()
            QMessageBox.information(self, 'Başarılı', 'Egzersiz kaydı başarıyla eklendi!', QMessageBox.Ok)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Hata', 'Egzersiz kaydı eklenirken bir hata oluştu!', QMessageBox.Ok)
        conn.close()


class FinanceTracker(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setupUi()
        
    def setupUi(self):
            self.setWindowTitle("Finansal Takip")
            self.setGeometry(100, 100, 400, 200)
            
            layout = QVBoxLayout(self)            
            # Gelir Eklemek İçin Form
            income_form_layout = QFormLayout()
            self.income_amount = QLineEdit()
            self.income_category = QLineEdit()
            self.income_button = QPushButton("Gelir Ekle")
            self.income_button.clicked.connect(self.add_income_record)
            
            income_form_layout.addRow("Miktar:", self.income_amount)
            income_form_layout.addRow("Kategori:", self.income_category)
            income_form_layout.addRow(self.income_button)
            
            # Gider Eklemek İçin Form
            expense_form_layout = QFormLayout()
            self.expense_amount = QLineEdit()
            self.expense_category = QLineEdit()
            self.expense_button = QPushButton("Gider Ekle")
            self.expense_button.clicked.connect(self.add_expense_record)
            
            expense_form_layout.addRow("Miktar:", self.expense_amount)
            expense_form_layout.addRow("Kategori:", self.expense_category)
            expense_form_layout.addRow(self.expense_button)
            
            layout.addLayout(income_form_layout)
            layout.addLayout(expense_form_layout)
            
            self.setLayout(layout)

    @pyqtSlot()
    def add_income_record(self):
        amount = self.income_amount.text()
        category = self.income_category.text()
        
        if not amount:
            QMessageBox.warning(self, 'Hata', 'Miktar bilgisi boş olamaz!', QMessageBox.Ok)
            return
        
        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, 'Hata', 'Miktar bilgisi geçersiz!', QMessageBox.Ok)
            return
        
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        query = "INSERT INTO financial_records (user_id, date, is_income, amount, category) VALUES (?, ?, ?, ?, ?)"
        try:
            c.execute(query, (self.user_id, today, True, amount, category))
            conn.commit()
            QMessageBox.information(self, 'Başarılı', 'Gelir kaydı başarıyla eklendi!', QMessageBox.Ok)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Hata', 'Gelir kaydı eklenirken bir hata oluştu!', QMessageBox.Ok)
        conn.close()

    @pyqtSlot()
    def add_expense_record(self):
        amount = self.expense_amount.text()
        category = self.expense_category.text()
        
        if not amount:
            QMessageBox.warning(self, 'Hata', 'Miktar bilgisi boş olamaz!', QMessageBox.Ok)
            return
        
        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, 'Hata', 'Miktar bilgisi geçersiz!', QMessageBox.Ok)
            return
        
        conn = sqlite3.connect('health_tracker.db')
        c = conn.cursor()
        today = QDate.currentDate().toString("yyyy-MM-dd")
        query = "INSERT INTO financial_records (user_id, date, is_income, amount, category) VALUES (?, ?, ?, ?, ?)"
        try:
            c.execute(query, (self.user_id, today, False, amount, category))
            conn.commit()
            QMessageBox.information(self, 'Başarılı', 'Gider kaydı başarıyla eklendi!', QMessageBox.Ok)
        except Exception as e:
            print(e)
            QMessageBox.warning(self, 'Hata', 'Gider kaydı eklenirken bir hata oluştu!', QMessageBox.Ok)
        conn.close()


class HealthGoals(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Sağlık Hedefleri")
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)
        formLayout = QFormLayout()

        # Hedefleri girme alanları
        self.calorie_goal = QSpinBox()
        self.calorie_goal.setMaximum(10000)
        self.exercise_minutes_goal = QSpinBox()
        self.exercise_minutes_goal.setMaximum(1440)  # Maksimum 24 saat

        formLayout.addRow(QLabel("Kalori Yakma Hedefi:"), self.calorie_goal)
        formLayout.addRow(QLabel("Egzersiz Dakikası Hedefi:"), self.exercise_minutes_goal)

        self.update_button = QPushButton("Hedefleri Güncelle")
        self.update_button.clicked.connect(self.updateGoals)

        layout.addLayout(formLayout)
        layout.addWidget(self.update_button)

    @pyqtSlot()
    def updateGoals(self):
        calories = self.calorie_goal.value()
        exercise_minutes = self.exercise_minutes_goal.value()

        try:
            conn = sqlite3.connect('health_tracker.db')
            c = conn.cursor()

            c.execute("""INSERT INTO health_goals (user_id, calorie_goal, exercise_minutes_goal) VALUES (?, ?, ?)
                         ON CONFLICT(user_id) DO UPDATE SET calorie_goal=?, exercise_minutes_goal=?""",
                      (self.user_id, calories, exercise_minutes, calories, exercise_minutes))

            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sağlık hedefleriniz güncellendi.")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Veritabanı hatası: {e}")
        finally:
            conn.close()





def initialize_db():
    conn = sqlite3.connect('health_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_data (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    date TEXT,
    steps INTEGER DEFAULT 0,
    water_intake INTEGER DEFAULT 0,
    calory_intake INTEGER DEFAULT 0,
    UNIQUE(user_id, date) ON CONFLICT REPLACE
);
''')
    c.execute('''CREATE TABLE IF NOT EXISTS exercise_records 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, exercise_name TEXT, duration INTEGER, calories_burned INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS nutrition_records
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, food_name TEXT, servings INTEGER, calories INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS financial_records
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, is_income BOOLEAN, amount REAL, category TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS health_goals (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,
    calorie_goal INTEGER,
    exercise_minutes_goal INTEGER
);''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_db()
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())