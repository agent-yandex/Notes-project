from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtPrintSupport import *

from data import db_session
from data.notes import Notes

import datetime


class Window(QMainWindow):
    def __init__(self):
        super().__init__(windowTitle='Заметки')
        self.setMinimumSize(QSize(675, 480))
        self.initUI()

    def initUI(self):
        self.current_choice = ''
        self.f = False

        widget = QWidget()
        self.scroll_widget = QWidget()
        self.status = QStatusBar()
        toolbar_notes = QToolBar('File')
        toolbar_notes.setIconSize(QSize(16, 16))
        toolbar_edit = QToolBar('Edit')
        toolbar_notes.setIconSize(QSize(16, 16))

        self.main_layout = QHBoxLayout()
        self.notes_layout = QVBoxLayout()
        self.work_layout = QVBoxLayout()
        date_filter_layout = QHBoxLayout()
        date_filter_layout.setAlignment(Qt.AlignLeft)
        self.title = QLineEdit()
        self.content = QPlainTextEdit()
        self.scroll = QScrollArea()

        self.main_layout.addLayout(self.notes_layout)
        self.main_layout.addLayout(self.work_layout)
        button = QPushButton('Фильтр', clicked=self.filter)
        button.setIcon(QIcon('setting/filter.png'))
        self.notes_layout.addWidget(button)
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)

        self.add_note_action = QAction(
            QIcon('setting/add.png'), 'Добавить заметку', self)
        self.add_note_action.triggered.connect(self.add_note)
        self.add_note_action.setStatusTip('Добавить заметку')

        self.delete_note_action = QAction(
            QIcon('setting/remove.png'), 'Удалить заметку', self)
        self.delete_note_action.setStatusTip('Удалить заметку')
        self.delete_note_action.triggered.connect(self.delete_note)
        self.delete_note_action.setEnabled(False)

        self.save_note_action = QAction(
            QIcon('setting/disk.png'), 'Сохранить', self)
        self.save_note_action.setStatusTip('Сохранить')
        self.save_note_action.triggered.connect(self.save_note)
        self.save_note_action.setEnabled(False)
        self.delete_note_action.setShortcut(QKeySequence("Ctrl+Space"))

        self.undo_action = QAction(
            QIcon('setting/arrow-curve-180-left.png'), 'Отменить', self)
        self.undo_action.setStatusTip('Отменить последнее действие')
        self.undo_action.triggered.connect(self.content.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = QAction(
            QIcon('setting/arrow-curve.png'), 'Вернуть', self)
        self.redo_action.setStatusTip('Вернуть последнее действие')
        self.redo_action.triggered.connect(self.content.redo)
        self.redo_action.setEnabled(False)

        self.print_action = QAction(
            QIcon('setting/printer.png'), 'Печать', self)
        self.print_action.setStatusTip('Распечатать заметку')
        self.print_action.triggered.connect(self.note_print)
        self.print_action.setEnabled(False)

        toolbar_notes.addAction(self.add_note_action)
        toolbar_notes.addAction(self.delete_note_action)
        toolbar_edit.addAction(self.save_note_action)
        toolbar_edit.addAction(self.undo_action)
        toolbar_edit.addAction(self.redo_action)
        toolbar_edit.addAction(self.print_action)

        self.setStatusBar(self.status)
        self.addToolBar(toolbar_notes)
        self.addToolBar(toolbar_edit)

        self.draw_scrool_bar()
        self.draw_work_part('none')

    def draw_work_part(self, flag):
        # выводит окно просмотра заметки
        for i in reversed(range(self.work_layout.count())):
            self.work_layout.itemAt(i).widget().setParent(None)

        if flag == 'new':
            self.title.clear()
            self.content.clear()
            self.work_layout.addWidget(QLabel('Название'))
            self.work_layout.addWidget(self.title)
            self.work_layout.addWidget(QLabel('Содержание'))
            self.work_layout.addWidget(self.content)
        elif flag == 'choose':
            db_sess = db_session.create_session()
            note = db_sess.query(Notes).filter(
                Notes.id == self.current_choice).first()
            self.title.setText(note.title)
            self.content.clear()
            self.content.insertPlainText(note.content)
            self.work_layout.addWidget(QLabel('Название'))
            self.work_layout.addWidget(self.title)
            self.work_layout.addWidget(QLabel('Содержание'))
            self.work_layout.addWidget(self.content)
        elif flag == 'none':
            self.save_note_action.setEnabled(False)
            self.undo_action.setEnabled(False)
            self.redo_action.setEnabled(False)
            self.delete_note_action.setEnabled(False)
            self.print_action.setEnabled(False)
            self.work_layout.addWidget(
                QLabel('Выберите заметку или создайте новую'))
        elif flag == 'filter':
            self.save_note_action.setEnabled(False)
            self.undo_action.setEnabled(False)
            self.redo_action.setEnabled(False)
            self.delete_note_action.setEnabled(False)
            self.print_action.setEnabled(False)
            self.add_note_action.setEnabled(False)
            self.work_layout.addWidget(
                QLabel('Для добавления заметок выключите фильтр'))

    def draw_scrool_bar(self, action=False):
        # выводит окно со всеми заметками
        self.scroll_widget.deleteLater()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget = QWidget()
        self.scroll.setWidget(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.notes_layout.addWidget(self.scroll)

        db_sess = db_session.create_session()
        if not action:
            notes = db_sess.query(Notes).all()[::-1]
            self.indexes = []
            for i, note in enumerate(notes):
                self.indexes.append(note.id)
                row = QVBoxLayout()
                title = note.title
                if len(title) > 14:
                    title = title[:15] + '...'
                button = QPushButton(f'{i + 1}. {title} | {note.date}',
                                     clicked=self.choose_note)
                button.setIcon(QIcon('setting/document_text.png'))
                button.setIconSize(QSize(30, 30))
                button.setStyleSheet('text-align: left')
                row.addWidget(button)
                self.scroll_layout.addLayout(row)

        else:
            notes = db_sess.query(Notes).filter(Notes.id.in_(self.indexes)).all()[::-1]
            for i, note in enumerate(notes):
                self.indexes.append(note.id)
                row = QVBoxLayout()
                title = note.title
                if len(title) > 14:
                    title = title[:15] + '...'
                button = QPushButton(f'{i + 1}. {title} | {note.date}',
                                     clicked=self.choose_note)
                button.setIcon(QIcon('setting/document_text.png'))
                button.setIconSize(QSize(30, 30))
                button.setStyleSheet('text-align: left')
                row.addWidget(button)
                self.scroll_layout.addLayout(row)

        self.scroll_layout.addStretch()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

    def add_note(self):
        self.save_note_action.setEnabled(True)
        self.undo_action.setEnabled(True)
        self.redo_action.setEnabled(True)
        self.delete_note_action.setEnabled(False)
        self.print_action.setEnabled(False)
        self.current_choice = ''
        self.draw_work_part('new')

    def save_note(self):
        if self.current_choice:
            if self.title.text() and self.content.toPlainText():
                db_sess = db_session.create_session()
                note = db_sess.query(Notes).filter(
                    Notes.id == self.current_choice).first()
                note.title = self.title.text()
                note.content = self.content.toPlainText()
                note.date = datetime.datetime.now().date()
                db_sess.commit()
            else:
                self.status.showMessage('Заполните поля!')
        else:
            db_sess = db_session.create_session()
            if self.title.text() and self.content.toPlainText():
                note = Notes(
                    title=self.title.text(),
                    content=self.content.toPlainText())
                db_sess.add(note)
                db_sess.commit()
                self.current_choice = note.id
                self.delete_note_action.setEnabled(True)
                self.print_action.setEnabled(True)
            else:
                self.status.showMessage('Заполните поля!')
        if self.f:
            self.draw_scrool_bar(True)
        else:
            self.draw_scrool_bar()

    def choose_note(self):
        n = int(self.sender().text().split('.')[0])
        id = self.indexes[n - 1]
        db_sess = db_session.create_session()
        note = db_sess.query(Notes).filter(Notes.id == id).first()
        self.delete_note_action.setEnabled(True)
        self.save_note_action.setEnabled(True)
        self.undo_action.setEnabled(True)
        self.redo_action.setEnabled(True)
        self.print_action.setEnabled(True)
        self.current_choice = note.id
        self.draw_work_part('choose')

    def delete_note(self):
        db_sess = db_session.create_session()
        note = db_sess.query(Notes).filter(
            Notes.id == self.current_choice).first()
        db_sess.delete(note)
        db_sess.commit()
        if self.f:
            self.indexes.pop(self.indexes.index(note.id))
            self.draw_scrool_bar(True)
            self.draw_work_part('filter')
        else:
            self.draw_scrool_bar()
            self.draw_work_part('none')

    def note_print(self):
        dialog = QPrintDialog()
        if dialog.exec():
            self.content.print_(dialog.printer())

    def filter(self):
        self.dialog = QDialog()
        self.dialog.setWindowTitle('Фильтр')
        dialog_layout = QVBoxLayout()
        date_filter_layout = QHBoxLayout()
        self.date1 = QDateTimeEdit(QDate.currentDate(),
                                   calendarPopup=True)
        self.date2 = QDateTimeEdit(QDate.currentDate(),
                                   calendarPopup=True)

        date_filter_layout.addWidget(QLabel('Дата'))
        date_filter_layout.addWidget(self.date1)
        date_filter_layout.addWidget(QLabel('по'))
        date_filter_layout.addWidget(self.date2)
        dialog_layout.addLayout(date_filter_layout)
        self.dialog.setLayout(dialog_layout)
        dialog_layout.addWidget(QPushButton(
            'Активировать', clicked=self.activate_filter))
        if self.f:
            dialog_layout.addWidget(QPushButton(
                'Отменить фильтр', clicked=self.disable_filter))

        self.dialog.exec()

    def activate_filter(self):
        db_sess = db_session.create_session()
        day1, month1, year1 = map(
            int, self.date1.dateTime().toString('dd.MM.yyyy').split('.'))
        day2, month2, year2 = map(
            int, self.date2.dateTime().toString('dd.MM.yyyy').split('.'))
        d1 = datetime.date(year1, month1, day1)
        d2 = datetime.date(year2, month2, day2)
        days = [i for i in [d1 + datetime.timedelta(days=x)
                            for x in range((d2-d1).days + 1)]]
        notes = db_sess.query(Notes).filter(Notes.date.in_(days)).all()
        self.indexes = [note.id for note in notes]
        self.dialog.close()
        self.f = True
        self.draw_scrool_bar(True)
        self.draw_work_part('filter')

    def disable_filter(self):
        self.f = False
        self.dialog.close()
        self.add_note_action.setEnabled(True)
        self.draw_scrool_bar()
        self.draw_work_part('none')


db_session.global_init("database.db")

app = QApplication()
window = Window()
window.show()
app.exec()
