from main_ui import Ui_MainWindow
from addEditCoffeeForm import Ui_Form
import sqlite3
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem


class MainWindow(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.pushButton.clicked.connect(self.add_notes)
        self.pushButton_2.clicked.connect(self.update_notes)

    def initUI(self):
        con = sqlite3.connect("../data/coffee.db")
        cur = con.cursor()
        result = cur.execute("""SELECT id, 
                name_of_sort as [Сорт],
                degree_of_roasting as [Степень обжарки],
                ground_or_grain as [Молотый/Зерновой],
                description_taste as [Описание вкуса],
                cost as [Цена],
                volume as [Объем] FROM list_coffee
                """).fetchall()
        self.tableWidget.setRowCount(len(result))

        self.titles = [description[0] for description in cur.description]
        self.tableWidget.setColumnCount(len(self.titles))
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
        self.tableWidget.resizeColumnsToContents()
        con.close()

    def add_notes(self):
        self.second_form = AddCoffeeWindow(self)
        self.second_form.show()

    def update_notes(self):
        count_selected_items = len(list(set([i.row() for i in self.tableWidget.selectedItems()])))
        if count_selected_items:
            self.statusBar().clearMessage()
            # Получаем список элементов без повторов и их id
            rows = list(set([i.row() for i in self.tableWidget.selectedItems()]))
            id = [self.tableWidget.item(i, 0).text() for i in rows][0]
            self.second_form = CorrectCoffeeWindow(self, id)
            self.second_form.show()
        else:
            self.statusBar().showMessage("Вы не выделили ни одного элемента для редактирования")


class AddCoffeeWindow(QMainWindow, Ui_Form):
    # Форма для добавления новых записей
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.comboBox.addItems(["Молотый", "Зерновой"])
        self.pushButton.clicked.connect(self.add_notes)
        self.spinBox.setMaximum(10000)
        self.spinBox_2.setMaximum(10000)

    def add_notes(self):
        con = sqlite3.connect("../data/coffee.db")
        cur = con.cursor()
        # Данные для создания новой записи
        sort = self.lineEdit.text()
        degree = self.lineEdit_2.text()
        ground_or_grain = self.comboBox.currentText()
        description = self.lineEdit_3.text()
        cost = str(self.spinBox.value())
        volume = str(self.spinBox_2.value())
        if self.check_good_data(sort, degree, description, cost, volume):
            self.statusBar().clearMessage()
            cur.execute(f"""INSERT INTO list_coffee(name_of_sort, degree_of_roasting,
            ground_or_grain, description_taste, cost, Volume) 
            VALUES('{sort}', '{degree}', '{ground_or_grain}', '{description}', '{cost}', '{volume}')""")
            con.commit()

            # Получаем данные по db
            con = sqlite3.connect("../data/coffee.db")
            cur = con.cursor()
            result = cur.execute("""SELECT id, 
                            name_of_sort as [Сорт],
                            degree_of_roasting as [Степень обжарки],
                            ground_or_grain as [Молотый/Зерновой],
                            description_taste as [Описание вкуса],
                            cost as [Цена],
                            volume as [Объем] FROM list_coffee
                            """).fetchall()
            self.parent.tableWidget.setRowCount(len(result))

            self.parent.tableWidget.setColumnCount(len(result[0]))
            self.parent.titles = [description[0] for description in cur.description]
            self.parent.tableWidget.setHorizontalHeaderLabels(self.parent.titles)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.parent.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.parent.tableWidget.resizeColumnsToContents()
            con.close()
            self.hide()
        else:
            self.statusBar().showMessage("Данные введены некоректно")

    def check_good_data(self, sort, degree, description, cost, volume):
        correct = 1
        if not sort or not degree or not description or not cost or not volume:
            correct = 0
        return correct


class CorrectCoffeeWindow(QMainWindow, Ui_Form):
    # Форма для корректирования записей по id ряда
    def __init__(self, parent, id):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.id = id
        self.initUI()

    def initUI(self):
        self.comboBox.addItems(["Молотый", "Зерновой"])
        self.pushButton.clicked.connect(self.update_notes)
        self.spinBox.setMaximum(10000)
        self.spinBox_2.setMaximum(10000)
        # Получаем данные для заполнения полей
        con = sqlite3.connect("../data/coffee.db")
        cur = con.cursor()
        result = list(cur.execute(f"""SELECT * FROM list_coffee WHERE id = {self.id}""").fetchall())[0]
        self.lineEdit.setText(result[1])
        self.lineEdit_2.setText(str(result[2]))
        self.comboBox.setCurrentText(result[3])
        self.lineEdit_3.setText(str(result[4]))
        self.spinBox.setValue(int(result[5]))
        self.spinBox_2.setValue(int(result[6]))

    def update_notes(self):
        con = sqlite3.connect("../data/coffee.db")
        cur = con.cursor()
        # Данные для создания новой записи
        sort = self.lineEdit.text()
        degree = self.lineEdit_2.text()
        ground_or_grain = self.comboBox.currentText()
        description = self.lineEdit_3.text()
        cost = str(self.spinBox.value())
        volume = str(self.spinBox_2.value())
        if self.check_good_data(sort, degree, description, cost, volume):
            self.statusBar().clearMessage()
            cur.execute(f"""UPDATE list_coffee
             SET name_of_sort = '{sort}', degree_of_roasting = '{degree}',
             ground_or_grain = '{ground_or_grain}', description_taste = '{description}',
             cost = '{cost}', Volume = '{volume}'
             WHERE id = {self.id}""")
            con.commit()

            # Получаем данные по db
            con = sqlite3.connect("../data/coffee.db")
            cur = con.cursor()
            result = cur.execute("""SELECT id, 
                                        name_of_sort as [Сорт],
                                        degree_of_roasting as [Степень обжарки],
                                        ground_or_grain as [Молотый/Зерновой],
                                        description_taste as [Описание вкуса],
                                        cost as [Цена],
                                        volume as [Объем] FROM list_coffee
                                        """).fetchall()
            self.parent.tableWidget.setRowCount(len(result))

            self.parent.tableWidget.setColumnCount(len(result[0]))
            self.parent.titles = [description[0] for description in cur.description]
            self.parent.tableWidget.setHorizontalHeaderLabels(self.parent.titles)
            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.parent.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.parent.tableWidget.resizeColumnsToContents()
            con.close()
            self.hide()
        else:
            self.statusBar().showMessage("Данные введены некоректно")

    def check_good_data(self, sort, degree, description, cost, volume):
        correct = 1
        if not sort or not degree or not description or not cost or not volume:
            correct = 0
        return correct


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
