import sys

from PyQt5.QtCore import (
    QAbstractListModel,
    QMargins,
    Qt,
    QSize,
    QRect,
    QPoint,
    QRectF,
    QEvent,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPixmap,
    QIcon,
    QFont,
    QFontMetrics,
    QFontDatabase,
    QKeyEvent,
    QTextDocument,
    QTextOption,
)
from PyQt5.QtWidgets import (
    QApplication,
    QListView,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QStyledItemDelegate,
    QAbstractButton,
    QTextEdit,
)

import resources
import ctypes
myappid = u'LanaDigging.Lobster.Messenger.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class Defines():
    USER_ME = 0
    USER_THEM = 1
    BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#a5d6a7"}
    BUBBLE_PADDING = QMargins(15, 5, 15, 5)
    TEXT_PADDING = QMargins(25, 15, 25, 15)
    MAX_ROWS = 8
    APP_NAME = "LobsterMessage"
    FONT_SIZE = 14
    FONT_FILE = ":/fonts/lobster.ttf"
    PLACEHOLDER_TEXT = "Enter message"
    LOGO_IMG = ":/img/logo.png"
    SEND_IDLE_IMG = ":/img/send1.png"
    SEND_HOVER_IMG = ":/img/send2.png"
    SEND_PRESS_IMG = ":/img/send3.png"

window_width = 0

class Message:
    def __init__(self, text, Y, user):
        self.text = text
        self.size = 0
        self.Y = Y
        self.user = user

class MessageDelegate(QStyledItemDelegate):
    font = 0

    def __init__(self, font, *args, **kwargs):
        super(MessageDelegate, self).__init__(*args, **kwargs)
        self.font = font

    def paint(self, painter, option, index):
        msg = index.model().data(index, Qt.DisplayRole)
        field = QRect(option.rect)
        field = field.marginsRemoved(Defines.TEXT_PADDING)
        doc = QTextDocument(msg.text)
        doc.setDocumentMargin(0)
        opt = QTextOption()
        opt.setWrapMode(opt.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(opt)
        doc.setDefaultFont(self.font)
        doc.setTextWidth(field.size().width() - 20)
        field.setHeight(int(doc.size().height()))
        field.setWidth(int(doc.idealWidth()))
        field = field.marginsAdded(Defines.TEXT_PADDING)
        if msg.user == Defines.USER_ME:
            rect = QRect(option.rect.right() - field.size().width() - 20, msg.Y, field.size().width(), field.size().height())
        else:
            rect = QRect(20, msg.Y, field.size().width(), field.size().height())
        bubblerect = rect.marginsRemoved(Defines.BUBBLE_PADDING)
        textrect = rect.marginsRemoved(Defines.TEXT_PADDING)
        painter.setPen(Qt.NoPen)
        color = QColor(Defines.BUBBLE_COLORS[msg.user])
        painter.setBrush(color)
        painter.drawRoundedRect(bubblerect, 10, 10)
        if msg.user == Defines.USER_ME:
            p1 = bubblerect.topRight()
        else:
            p1 = bubblerect.topLeft()
        painter.drawPolygon(p1 + QPoint(-20, 0), p1 + QPoint(20, 0), p1 + QPoint(0, 15))
        painter.setPen(Qt.black)
        painter.setFont(self.font)
        painter.translate(textrect.x(), textrect.y())
        textrectf = QRectF(textrect)
        textrectf.moveTo(0, 0)
        doc.drawContents(painter, textrectf)
        painter.translate(-textrect.x(), -textrect.y())

    def sizeHint(self, option, index):
        global window_width
        msg = index.model().data(index, Qt.DisplayRole)
        field = QRect(option.rect)
        field.setWidth(window_width - 30)
        field = field.marginsRemoved(Defines.TEXT_PADDING)
        doc = QTextDocument(msg.text)
        doc.setDocumentMargin(0)
        opt = QTextOption()
        opt.setWrapMode(opt.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(opt)
        doc.setDefaultFont(self.font)
        doc.setTextWidth(field.size().width() - 20)
        field.setHeight(int(doc.size().height()))
        field.setWidth(int(doc.idealWidth()))
        field = field.marginsAdded(Defines.TEXT_PADDING)
        index.model().setSize(index, field.size().height())
        return QSize(0, field.size().height())


class MessageModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self.messages = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.messages[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def setSize(self, index, size):
        if (size != self.messages[index.row()].size):
            self.messages[index.row()].size = size
            curY = self.messages[index.row()].Y + size
            for i in range(index.row() + 1, len(self.messages)):
                self.messages[i].Y = curY
                curY += self.messages[i].size

    def add_message(self, text, user):
        if text:
            length = len(self.messages)
            Y = 0
            if length != 0:
                Y = self.messages[length - 1].size + self.messages[length - 1].Y
            cur = len(self.messages)
            self.messages.append(Message(text, Y, user))
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
    font = 0

    def __init__(self):
        global window_width
        super(MainWindow, self).__init__()
        id = QFontDatabase.addApplicationFont(Defines.FONT_FILE)
        family = QFontDatabase.applicationFontFamilies(id)[0]
        self.font = QFont(family, Defines.FONT_SIZE)
        self.setMinimumSize(int(QApplication.primaryScreen().size().width() * 0.1), int(QApplication.primaryScreen().size().height() * 0.2))
        self.resize(int(QApplication.primaryScreen().size().width() * 0.3), int(QApplication.primaryScreen().size().height() * 0.5))
        window_width = int(QApplication.primaryScreen().size().width() * 0.3)
        main_layout = QVBoxLayout()
        send_layout = QHBoxLayout()
        self.send_input = QTextEdit()
        self.send_input.setPlaceholderText(Defines.PLACEHOLDER_TEXT)
        self.send_input.setFont(self.font)
        self.send_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.send_input.textChanged.connect(self.message_resize)
        self.send_input.installEventFilter(self)
        self.send_btn = PicButton(QPixmap(Defines.SEND_IDLE_IMG), QPixmap(Defines.SEND_HOVER_IMG), QPixmap(Defines.SEND_PRESS_IMG))
        self.messages = QListView()
        self.messages.setItemDelegate(MessageDelegate(self.font))
        #self.messages.setStyleSheet("background-image: url(:/img/back.jpg);");
        self.model = MessageModel()
        self.messages.setModel(self.model)
        self.send_btn.pressed.connect(self.message_from)
        main_layout.addWidget(self.messages)
        send_layout.addWidget(self.send_input)
        send_layout.addWidget(self.send_btn, 0, Qt.AlignBottom)
        main_layout.addLayout(send_layout)
        self.w = QWidget()
        self.w.setLayout(main_layout)
        self.setCentralWidget(self.w)
        self.setWindowTitle(Defines.APP_NAME)
        self.setWindowIcon(QIcon(Defines.LOGO_IMG))
        self.message_resize()

    def message_to(self):
        self.model.add_message(self.send_input.toPlainText(), Defines.USER_ME)
        self.messages.scrollToBottom()
        self.send_input.clear()

    def message_from(self):
        self.model.add_message(self.send_input.toPlainText(), Defines.USER_THEM)
        self.messages.scrollToBottom()
        self.send_input.clear()

    def message_resize(self):
        height = self.send_input.document().documentLayout().documentSize().height()
        fm = QFontMetrics(self.font)
        space = self.send_input.document().documentMargin()
        rowNum = int((height - (2 * self.send_input.document().documentMargin())) / fm.lineSpacing())
        if rowNum == 0:
            rowNum = 1
        if rowNum > Defines.MAX_ROWS:
            rowNum = Defines.MAX_ROWS
        margins = self.send_input.contentsMargins()
        height = fm.lineSpacing() * rowNum + (self.send_input.document().documentMargin() + self.send_input.frameWidth()) * 2 + margins.top() + margins.bottom()
        self.send_input.setFixedHeight(int(height))

    def resizeEvent(self, event):
        global window_width
        super(MainWindow, self).resizeEvent(event)
        window_width = self.size().width()

    def eventFilter(self, widget, event):
        if event.type() == QEvent.KeyPress:
            keyEvent = QKeyEvent(event)
            if (not (keyEvent.modifiers() & Qt.ShiftModifier)) and ((keyEvent.key() == Qt.Key_Enter) or (keyEvent.key() == Qt.Key_Return)):
                self.message_to()
                return True
        return QWidget.eventFilter(self, widget, event)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
window.send_input.setFocus()
app.exec_()
