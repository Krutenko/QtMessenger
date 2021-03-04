import sys

from PyQt5.QtCore import QAbstractListModel, QMargins, QPoint, Qt, QSize
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPainter, QFont, QFontDatabase
from PyQt5.QtWidgets import (
    QApplication,
    QLineEdit,
    QListView,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QAbstractButton,
)

import resources

USER_ME = 0
USER_THEM = 1
BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#a5d6a7"}
BUBBLE_PADDING = QMargins(15, 5, 15, 5)
TEXT_PADDING = QMargins(25, 15, 25, 15)


class MessageDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        user, text = index.model().data(index, Qt.DisplayRole)
        bubblerect = option.rect.marginsRemoved(BUBBLE_PADDING)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)
        painter.setPen(Qt.NoPen)
        color = QColor(BUBBLE_COLORS[user])
        painter.setBrush(color)
        painter.drawRoundedRect(bubblerect, 10, 10)
        if user == USER_ME:
            p1 = bubblerect.topRight()
        else:
            p1 = bubblerect.topLeft()
        painter.drawPolygon(p1 + QPoint(-20, 0), p1 + QPoint(20, 0), p1 + QPoint(0, 15))
        painter.setPen(Qt.black)
        id = QFontDatabase.addApplicationFont(":/fonts/lobster.ttf");
        family = QFontDatabase.applicationFontFamilies(id)[0];
        painter.setFont(QFont(family, 14))
        painter.drawText(textrect, Qt.TextWordWrap, text)

    def sizeHint(self, option, index):
        _, text = index.model().data(index, Qt.DisplayRole)
        metrics = QApplication.fontMetrics()
        rect = option.rect.marginsRemoved(TEXT_PADDING)
        rect = metrics.boundingRect(rect, Qt.TextWordWrap, text)
        rect = rect.marginsAdded(TEXT_PADDING)
        return rect.size()


class MessageModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self.messages = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.messages[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def add_message(self, who, text):
        if text:
            self.messages.append((who, text))
            self.layoutChanged.emit()


class PicButton(QAbstractButton):
    def __init__(self, pixmap, pixmap_hover, pixmap_pressed, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap_hover = pixmap_hover
        self.pixmap_pressed = pixmap_pressed

        self.pressed.connect(self.update)
        self.released.connect(self.update)

    def paintEvent(self, event):
        pix = self.pixmap_hover if self.underMouse() else self.pixmap
        if self.isDown():
            pix = self.pixmap_pressed

        painter = QPainter(self)
        painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(int(0.1 * self.pixmap.size().width()), int(0.1 * self.pixmap.size().width()))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(int(QApplication.primaryScreen().size().width() * 0.1), int(QApplication.primaryScreen().size().height() * 0.2))
        self.resize(int(QApplication.primaryScreen().size().width() * 0.3), int(QApplication.primaryScreen().size().height() * 0.5))
        main_layout = QVBoxLayout()
        send_layout = QHBoxLayout()
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("Enter message")
        id = QFontDatabase.addApplicationFont(":/fonts/lobster.ttf");
        family = QFontDatabase.applicationFontFamilies(id)[0];
        self.send_input.setFont(QFont(family, 14))
        #self.send_btn = QPushButton()
        #pm = QPixmap(":/img/send1.png")
        #self.send_btn.setIcon(QIcon(pm))
        #self.send_btn.setIconSize(pm.rect().size())
        self.send_btn = PicButton(QPixmap(":/img/send1.png"), QPixmap(":/img/send2.png"), QPixmap(":/img/send3.png"))
        self.messages = QListView()
        self.messages.setItemDelegate(MessageDelegate())
        self.messages.setStyleSheet("background-image: url(:/img/back.jpg);");
        self.model = MessageModel()
        self.messages.setModel(self.model)
        self.send_btn.pressed.connect(self.message_to)
        main_layout.addWidget(self.messages)
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_btn)
        main_layout.addLayout(send_layout)
        self.w = QWidget()
        self.w.setLayout(main_layout)
        self.setCentralWidget(self.w)

    def message_to(self):
        self.model.add_message(USER_ME, self.send_input.text())
        self.messages.scrollToBottom()

    def message_from(self):
        self.model.add_message(USER_THEM, self.send_input.text())


app = QApplication(sys.argv)
window = MainWindow()
window.show()
window.send_input.setFocus()
app.exec_()
