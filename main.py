from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication,QBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit,\
     QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox,\
     QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)
        # Create File menu
        file_menu_item = self.menuBar().addMenu("&File")
        # Create Help menu
        help_menu_item = self.menuBar().addMenu("&Help")
        # Create Edit menu
        edit_menu_item = self.menuBar().addMenu("&Edit")

        # Add menu item to File menu
        add_student_action = QAction(QIcon("icons/add.png"),"Add Student", self) # Menu item created
        file_menu_item.addAction(add_student_action)  # Menu item added to menu list
        add_student_action.triggered.connect(self.insert) # Inserts a dialogue box to add student menu item.

        # Add menu item to Help menu
        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole) # This line of code is for Mac users
        about_action.triggered.connect(self.about)


        # Add menu item to Edit menu
        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)
        # about_action.setMenuRole(QAction.MenuRole.NoRole) # if hel menu is not visible

        # Create a table widget/structure
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)

        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)

        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        self.addToolBar(toolbar)

        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        # self.statusbar.addWidget(self.statusbar)

        # hello = QLabel("Hello There!")
        # statusbar.addWidget(hello)
        #
        # hello = QLabel("Hello World!")
        # statusbar.addWidget(hello)

        # Detect a cell click and add status bar elements - Edit Record, and Delete Record buttons
        self.table.cellClicked.connect(self.cell_clicked)

    # status bar elements - edit button, and delete button added. These button become visible upon a cell clicked
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit) # Once edit button is clicked, edit method is executed-which is linked to EditDialog class

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete) # Once delete button is clicked, delete method is executed-which is linked to DeleteDialog class

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)
        # Edit button and delete button widgets are added to the status bar defined in the main window
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    # Loading data from database table and populate the table that was created in the above stage
    def load_data(self):
        connection = sqlite3.connect("database.db")
        data = connection.execute("SELECT * FROM students")
        # print(list(data))
        self.table.setRowCount(0) # It resets the table and load data as fresh to avoid duplicate data.
        for row_number, row_data in enumerate(data):
            # print(row_number)
            # print(row_data)
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                # print(column_number)
                # print(cell_data)
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(cell_data)))
        connection.close()

    # Create methods for main menus in the menu bar:-
    # Create a insert dialogue box to insert new student registration data in the table through\
    # file menu item-Add Student
    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    # Create a insert dialogue box to insert new student registration data in the table through edit menu item-Search
    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    # Method for help menu bar item - About
    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    # Create methods for status bar buttons:-
    # Method for edit record at status bar
    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    # Method for delete record at status bar
    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the training. Please feel free to modify it.
        """
        self.setText(content)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = main_window.table.item(index, 2).text()
        self.courses_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.courses_name.addItems(courses)
        self.courses_name.setCurrentText(course_name)

        layout.addWidget(self.courses_name)

        # Add mobile widget
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add an update button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.courses_name.itemText(self.courses_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")
        # self.setFixedWidth(300)
        # self.setFixedHeight(300)

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row index and student id
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        main_window.load_data()

        # Closing the window
        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()

# Class to add new student registration data to the database through file menu
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    # Method to add new student data to database table
    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()

        # Retrieves updated data from database to show in the online table
        main_window.load_data()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        # Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        ## Database connection for illustration-possibly.
        # connection = sqlite3.connect("database.db")
        # cursor = connection.cursor()
        # data = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        # rows = list(data)
        # print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)  # This returns list of mathing names
        print("items: ", items)  # These are name objects
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)  # This highlights all matched names greyed out

        # cursor.close()
        # connection.close()


# Programme main loop/running loop of app:-
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())