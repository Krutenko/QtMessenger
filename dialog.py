import resources
import variables
from PyQt5.QtCore import (
    QAbstractListModel,
    QMargins,
    Qt,
    QSize,
    QRect,
    QPoint,
    QRectF,
    QEvent,
    QModelIndex,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPixmap,
    QFontMetrics,
    QKeyEvent,
    QTextDocument,
    QTextOption,
    QPen,
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
    QLabel,
    QLineEdit
)

class Message:
    def __init__(self, text, user):
        self.text = text
        self.size = 0
        self.user = user
        self.status = variables.STATUS_UNREAD

class MessageDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        super(MessageDelegate, self).__init__(*args, **kwargs)

    def paint(self, painter, option, index):
        msg = index.model().data(index, Qt.DisplayRole)
        field = QRect(option.rect)
        field = field.marginsRemoved(variables.TEXT_PADDING)
        doc = QTextDocument(msg.text)
        doc.setDocumentMargin(0)
        opt = QTextOption()
        opt.setWrapMode(opt.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(opt)
        doc.setDefaultFont(variables.font)
        if msg.user == variables.USER_ME:
            doc.setTextWidth(field.size().width() - 20 - 50)
        else:
            doc.setTextWidth(field.size().width() - 20)
        field.setHeight(int(doc.size().height()))
        field.setWidth(int(doc.idealWidth()))
        field = field.marginsAdded(variables.TEXT_PADDING)
        line_height = QFontMetrics(variables.font).lineSpacing() + variables.TEXT_PADDING.bottom() - variables.BUBBLE_PADDING.bottom() + variables.TEXT_PADDING.top() - variables.BUBBLE_PADDING.top()
        if msg.user == variables.USER_ME:
            rect = QRect(option.rect.right() - field.size().width() - 20, option.rect.top(), field.size().width(), field.size().height())
        else:
            rect = QRect(20, option.rect.top(), field.size().width(), field.size().height())
        bubblerect = rect.marginsRemoved(variables.BUBBLE_PADDING)
        textrect = rect.marginsRemoved(variables.TEXT_PADDING)
        if msg.user == variables.USER_ME:
            p1 = bubblerect.topRight()
            p2 = bubblerect.bottomLeft() + QPoint(-36, -int(line_height / 2))
        else:
            p1 = bubblerect.topLeft()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        color = QColor(variables.BUBBLE_COLORS[msg.user])
        painter.setBrush(color)
        painter.drawRoundedRect(bubblerect, 10, 10)
        painter.drawPolygon(p1 + QPoint(-20, 0), p1 + QPoint(20, 0), p1 + QPoint(0, 15))
        if msg.user == variables.USER_ME:
            if msg.status == variables.STATUS_UNREAD:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(variables.STATUS_COLOR))
                painter.drawEllipse(p2, 7, 7)
            elif msg.status == variables.STATUS_UNDELIVERED:
                pen = QPen(QColor(variables.STATUS_COLOR))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(p2, 7, 7)
                painter.drawLine(p2, p2 + QPoint(0, -5))
                painter.drawLine(p2, p2 + QPoint(3, 0))
        painter.setPen(Qt.gray)
        painter.setFont(variables.font)
        painter.translate(textrect.x(), textrect.y())
        textrectf = QRectF(textrect)
        textrectf.moveTo(0, 0)
        doc.drawContents(painter, textrectf)
        painter.translate(-textrect.x(), -textrect.y())

    def sizeHint(self, option, index):
        msg = index.model().data(index, Qt.DisplayRole)
        field = QRect(option.rect)
        field.setWidth(variables.window_width - variables.WINDOW_PADDING)
        field = field.marginsRemoved(variables.TEXT_PADDING)
        doc = QTextDocument(msg.text)
        doc.setDocumentMargin(0)
        opt = QTextOption()
        opt.setWrapMode(opt.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(opt)
        doc.setDefaultFont(variables.font)
        if msg.user == variables.USER_ME:
            doc.setTextWidth(field.size().width() - 20 - 50)
        else:
            doc.setTextWidth(field.size().width() - 20)
        field.setHeight(int(doc.size().height()))
        field.setWidth(int(doc.idealWidth()))
        field = field.marginsAdded(variables.TEXT_PADDING)
        return QSize(0, field.size().height())


class MessageModel(QAbstractListModel):
    def __init__(self, ip, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self.ip = ip
        self.messages = []
        self.base = 0

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.messages[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def setStatus(self, id, status):
        self.messages[self.base + id].status = status
        self.layoutChanged.emit()

    def add_message(self, text, user):
        if text:
            length = len(self.messages)
            self.messages.append(Message(text, user))
            self.layoutChanged.emit()
            return length - self.base

    def send_read(self):
        for i in reversed(range(len(self.messages))):
            if self.messages[i].user == variables.USER_ME:
                break
            elif self.messages[i].status == variables.STATUS_READ:
                break
            else:
                self.messages[i].status = variables.STATUS_READ
                variables.nw.send_read(i - self.base, self.ip)

    def new_base(self):
        self.base = self.base + len(self.messages)


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


class Dialog(QWidget):
    width_changed = pyqtSignal()

    def __init__(self, ip):
        super(Dialog, self).__init__()
        self.ip = ip
        self.main_layout = QVBoxLayout()
        self.header_layout = QHBoxLayout()
        self.send_layout = QHBoxLayout()
        self.send_input = QTextEdit()
        self.send_input.setPlaceholderText(variables.PLACEHOLDER_TEXT)
        self.send_input.setFont(variables.font)
        self.send_input.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.send_input.textChanged.connect(self.message_resize)
        self.send_input.installEventFilter(self)
        self.send_btn = PicButton(QPixmap(variables.SEND_IDLE_IMG), QPixmap(variables.SEND_HOVER_IMG), QPixmap(variables.SEND_PRESS_IMG))
        self.back_btn = PicButton(QPixmap(variables.BACK_IDLE_IMG), QPixmap(variables.BACK_HOVER_IMG), QPixmap(variables.BACK_PRESS_IMG))
        self.ip_label = QLabel(ip)
        self.ip_label.setFont(variables.font)
        self.messages = QListView()
        delegate = MessageDelegate()
        self.messages.setItemDelegate(delegate)
        self.width_changed.connect(lambda: delegate.sizeHintChanged.emit(QModelIndex()))
        self.model = MessageModel(ip)
        self.messages.setModel(self.model)
        self.send_btn.released.connect(self.message_to)
        self.back_btn.released.connect(self.return_to_menu)
        self.header_layout.addWidget(self.back_btn, 0, Qt.AlignVCenter | Qt.AlignLeft)
        self.header_layout.addWidget(self.ip_label, 0, Qt.AlignVCenter | Qt.AlignLeft)
        self.header_layout.addStretch()
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.messages)
        self.send_layout.addWidget(self.send_input)
        self.send_layout.addWidget(self.send_btn, 0, Qt.AlignBottom)
        self.main_layout.addLayout(self.send_layout)
        self.setLayout(self.main_layout)
        self.message_resize()

    def return_to_menu(self):
        variables.signals.close_dialog.emit()

    def message_to(self):
        msg = self.send_input.toPlainText()
        if not msg:
            return
        id = self.model.add_message(msg, variables.USER_ME)
        variables.nw.send_message(id, msg, self.ip)
        variables.signals.message_sent.emit(msg, self.ip)
        self.messages.scrollToBottom()
        self.send_input.clear()
        self.send_input.setFocus()

    def message_from(self, msg):
        self.model.add_message(msg, variables.USER_THEM)

    def undelivered_status(self, id):
        self.model.setUndelivered(id)

    def delivered_status(self, id):
        self.model.setUnread(id)

    def read_status(self, id):
        self.model.setRead(id)

    def message_resize(self):
        height = self.send_input.document().documentLayout().documentSize().height()
        fm = QFontMetrics(variables.font)
        space = self.send_input.document().documentMargin()
        rowNum = int((height - (2 * self.send_input.document().documentMargin())) / fm.lineSpacing())
        if rowNum == 0:
            rowNum = 1
        if rowNum > variables.MAX_ROWS:
            rowNum = variables.MAX_ROWS
        margins = self.send_input.contentsMargins()
        height = fm.lineSpacing() * rowNum + (self.send_input.document().documentMargin() + self.send_input.frameWidth()) * 2 + margins.top() + margins.bottom()
        self.send_input.setFixedHeight(int(height))

    def eventFilter(self, widget, event):
        if event.type() == QEvent.KeyPress:
            keyEvent = QKeyEvent(event)
            if (not (keyEvent.modifiers() & Qt.ShiftModifier)) and ((keyEvent.key() == Qt.Key_Enter) or (keyEvent.key() == Qt.Key_Return)):
                self.message_to()
                return True
        return QWidget.eventFilter(self, widget, event)
