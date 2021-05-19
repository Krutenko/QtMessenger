import variables
from PyQt5.QtCore import (
    QAbstractListModel,
    QSize,
    Qt,
    QRect,
    QRectF,
    QEvent,
    QPoint,
)
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLineEdit,
    QLabel,
    QListView,
    QStyledItemDelegate,
    QStyle,
    QStylePainter,
)
from PyQt5.QtGui import (
    QFontMetrics,
    QPainter,
    QColor,
    QBrush,
    QPen,
    QTextDocument,
    QMouseEvent,
    QPalette,
    QLinearGradient,
    QGradient,
)

class Dialog:
    def __init__(self, ip, order, user, msg, status):
        self.ip = ip
        self.order = order
        self.user = user
        self.msg = msg
        self.status = status

class DialogDelegate(QStyledItemDelegate):

    def __init__(self, *args, **kwargs):
        super(DialogDelegate, self).__init__(*args, **kwargs)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                variables.signals.open_dialog.emit(index.row())
        return QStyledItemDelegate.editorEvent(self, event, model, option, index)

    def paint(self, painter, option, index):
        dlg = index.model().data(index, Qt.DisplayRole)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(Qt.white)
        if option.state & QStyle.State_MouseOver:
            color = QColor(variables.HIGHLIGHT_COLOR)
            painter.setPen(QPen(color))
            painter.setBrush(QBrush(color))
            painter.drawRect(option.rect)
        painter.setPen(Qt.black)
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())
        doc = QTextDocument(dlg.ip)
        doc.setDocumentMargin(0)
        doc.setDefaultFont(variables.font)
        textrect = QRect(option.rect)
        textrect = textrect.marginsRemoved(variables.IP_PADDING)
        textrect.setHeight(int(doc.size().height()))
        textrect.setWidth(int(doc.size().width()))
        offset = textrect.marginsAdded(variables.IP_PADDING).height()
        painter.setPen(Qt.black)
        painter.setFont(variables.font)
        painter.translate(textrect.x(), textrect.y())
        textrectf = QRectF(textrect)
        textrectf.moveTo(0, 0)
        doc.drawContents(painter, textrectf)
        painter.translate(-textrect.x(), -textrect.y())
        string = ""
        if dlg.user == variables.USER_ME:
            string += "You: "
        print(dlg.msg)
        string += dlg.msg
        fm = QFontMetrics(variables.font_small)
        textrect = QRect(option.rect)
        textrect.moveTop(textrect.y() + offset)
        textrect = textrect.marginsRemoved(variables.MSG_PADDING)
        textrect.setHeight(fm.lineSpacing())
        spainter = QStylePainter(painter.device(), QWidget())
        spainter.setRenderHint(QPainter.Antialiasing)
        if fm.horizontalAdvance(string) > textrect.width():
            fade = QLinearGradient(variables.MSG_PADDING.left() + textrect.width()* 0.9, 0, variables.MSG_PADDING.left() + textrect.width(), 0)
            fade.setSpread(QGradient.PadSpread)
            fade.setColorAt(0, Qt.darkGray)
            fade.setColorAt(1, color)
            pal = QPalette()
            pal.setBrush(QPalette.Text, QBrush(fade))
            spainter.setFont(variables.font_small)
            spainter.drawItemText(textrect, Qt.TextSingleLine, pal, True, string, QPalette.Text)
        else:
            spainter.setPen(Qt.darkGray)
            spainter.setFont(variables.font_small)
            spainter.drawText(textrect, Qt.TextSingleLine, string)
        p1 = textrect.bottomRight() + QPoint(36, -int(textrect.height() / 2))
        if dlg.status == variables.STATUS_UNREAD:
            spainter.setPen(Qt.NoPen)
            spainter.setBrush(QColor(variables.STATUS_COLOR))
            spainter.drawEllipse(p1, 7, 7)
        elif dlg.status == variables.STATUS_UNDELIVERED:
            pen = QPen(QColor(variables.STATUS_COLOR))
            pen.setWidth(2)
            spainter.setPen(pen)
            spainter.setBrush(Qt.NoBrush)
            spainter.drawEllipse(p1, 7, 7)
            spainter.drawLine(p1, p1 + QPoint(0, -5))
            spainter.drawLine(p1, p1 + QPoint(3, 0))
        elif dlg.status == variables.STATUS_NEW:
            pen = QPen(QColor(variables.STATUS_NEW_COLOR))
            pen.setWidth(5)
            spainter.setPen(pen)
            spainter.setBrush(Qt.NoBrush)
            spainter.drawEllipse(p1, 7, 7)
        #painter.translate(-textrect.x(), -textrect.y())

        '''doc = QTextDocument(str)
        doc.setDocumentMargin(0)
        doc.setDefaultFont(variables.font_small)
        textrect = QRect(option.rect)
        textrect.moveTop(textrect.y() + offset)
        textrect = textrect.marginsRemoved(variables.MSG_PADDING)
        textrect.setHeight(int(doc.size().height()))
        #textrect.setWidth(int(doc.size().width()))
        fade = QLinearGradient(0, 0, doc.size().width(), 0)
        fade.setSpread(QGradient.RepeatSpread)
        fade.setColorAt(0, Qt.black)
        fade.setColorAt(1, Qt.white)
        painter.setPen(Qt.blue)
        painter.setBrush(Qt.yellow)
        painter.setFont(variables.font_small)
        painter.translate(textrect.x(), textrect.y())
        textrectf = QRectF(textrect)
        textrectf.moveTo(0, 0)
        doc.drawContents(painter, textrectf)'''

    def sizeHint(self, option, index):
        return QSize(0, variables.dialog_height)


class DialogModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(DialogModel, self).__init__(*args, **kwargs)
        self.dialogs = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.dialogs[index.row()]

    def rowCount(self, index):
        return len(self.dialogs)

    def set_first(self, id):
        pass

    def add_dialog(self, ip):
        self.dialogs.append(Dialog(ip, len(self.dialogs), variables.USER_THEM, "qwerty", variables.STATUS_READ))
        self.set_first(self.dialogs[-1])
        self.layoutChanged.emit()

    def last_msg(self, id, msg, user):
        self.dialogs[id].msg = msg
        self.dialogs[id].status = variables.STATUS_UNREAD
        self.dialogs[id].user = user
        self.set_first(id)
        self.layoutChanged.emit()

    def set_status(self, id, status):
        self.dialogs[id].status = status
        self.layoutChanged.emit()


class DialogList(QWidget):
    def __init__(self):
        super(DialogList, self).__init__()
        variables.dialog_height = QFontMetrics(variables.font).height()
        variables.dialog_height += variables.IP_PADDING.top() + variables.IP_PADDING.bottom()
        variables.dialog_height += QFontMetrics(variables.font_small).height()
        variables.dialog_height += variables.MSG_PADDING.top() + variables.MSG_PADDING.bottom()
        variables.nw.client_connected.connect(self.incoming_dialog)
        variables.nw.connection_established.connect(self.connected)
        self.main_layout = QVBoxLayout()
        self.add_layout = QHBoxLayout()
        self.dialogs = QListView()
        self.dialogs.setItemDelegate(DialogDelegate())
        self.model = DialogModel()
        self.dialogs.setModel(self.model)
        self.ip_label = QLabel("IP:")
        self.ip_label.setFont(variables.font)
        self.ip_input = QLineEdit()
        self.ip_input.setFont(variables.font)
        self.ip_input.returnPressed.connect(self.add_dialog)
        self.editable = self.ip_input.palette()
        self.noneditable = QPalette(self.editable)
        self.noneditable.setColor(QPalette.Base, Qt.lightGray)
        self.noneditable.setColor(QPalette.Text, Qt.darkGray)
        self.add_btn = QPushButton("Add")
        self.add_btn.setStyleSheet("font: 14pt Lobster;")
        self.add_btn.pressed.connect(self.add_dialog)
        self.error_label = QLabel(" ")
        self.error_label.setStyleSheet("color: red; font: 12pt Lobster;")
        self.main_layout.addWidget(self.dialogs)
        self.add_layout.addWidget(self.ip_label)
        self.add_layout.addWidget(self.ip_input)
        self.add_layout.addWidget(self.add_btn)
        self.main_layout.addWidget(self.error_label)
        self.main_layout.addLayout(self.add_layout)
        self.setLayout(self.main_layout)

    def add_dialog(self):
        ip = self.ip_input.text()
        self.error_label.setStyleSheet("color: gray; font: 12pt Lobster;")
        self.error_label.setText("Connecting...")
        self.ip_input.setReadOnly(True)
        self.ip_input.setPalette(self.noneditable)
        self.add_btn.setEnabled(False)
        if variables.nw.connect_to(ip) == False:
            self.error_label.setStyleSheet("color: red; font: 12pt Lobster;")
            self.error_label.setText("Error occurred")
            self.ip_input.setReadOnly(False)
            self.ip_input.setPalette(self.editable)
            self.add_btn.setEnabled(True)

    def connected(self, success, ip):
        self.ip_input.setReadOnly(False)
        self.ip_input.setPalette(self.editable)
        self.add_btn.setEnabled(True)
        if success:
            self.error_label.setText("")
            self.ip_input.setText("")
            self.model.add_dialog(ip)
            variables.signals.create_dialog.emit(ip)
        else:
            self.error_label.setStyleSheet("color: red; font: 12pt Lobster;")
            self.error_label.setText("Error occurred")

    def incoming_dialog(self, ip):
        self.model.add_dialog(ip)
        variables.signals.create_dialog.emit(ip)
