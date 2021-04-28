import sys
from dialog import Dialog
from dialog_list import DialogList
import variables
import network
from PyQt5.QtGui import (
    QIcon,
    QFont,
    QFontDatabase,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStackedWidget,
)

import ctypes
myappid = u'LanaDigging.Lobster.Messenger.1'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(int(QApplication.primaryScreen().size().width() * 0.1), int(QApplication.primaryScreen().size().height() * 0.2))
        self.resize(int(QApplication.primaryScreen().size().width() * 0.3), int(QApplication.primaryScreen().size().height() * 0.5))
        window_width = int(QApplication.primaryScreen().size().width() * 0.3)
        id = QFontDatabase.addApplicationFont(variables.FONT_FILE)
        family = QFontDatabase.applicationFontFamilies(id)[0]
        variables.font = QFont(family, variables.FONT_SIZE)
        variables.font_small = QFont(family, variables.FONT_SIZE_SMALL)
        variables.nw = network.network()
        variables.signals = variables.DialogSignals()
        variables.signals.create_dialog.connect(self.createDialog)
        variables.signals.open_dialog.connect(self.openDialog)
        variables.signals.close_dialog.connect(self.closeDialog)
        variables.nw.received.connect(self.receiveMessage)
        self.dialogs = []
        self.dialog_menu = DialogList()
        self.main_widget = QStackedWidget()
        self.main_widget.addWidget(self.dialog_menu)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(variables.APP_NAME)
        self.setWindowIcon(QIcon(variables.LOGO_IMG))

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        variables.window_width = self.size().width()

    def createDialog(self, ip):
        self.dialogs.append(Dialog(ip))

    def openDialog(self, id):
        self.main_widget.addWidget(self.dialogs[id])
        self.main_widget.setCurrentIndex(1)
        self.dialogs[id].send_input.setFocus()

    def closeDialog(self):
        self.main_widget.setCurrentIndex(0)
        self.main_widget.removeWidget(self.main_widget.widget(1))

    def receiveMessage(self, msg, ip):
        for i in range(len(self.dialogs)):
            if self.dialogs[i].ip == ip:
                self.dialogs[i].message_from(msg)
                if self.main_widget.currentIndex() == 1 and self.main_widget.currentWidget().ip == ip:
                    break
                else:
                    self.dialog_menu.model.new_msg(i)
                self.dialog_menu.model.last_msg(i, msg)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
