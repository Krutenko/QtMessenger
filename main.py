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
        variables.nw = network.network()
        self.dialog_menu = DialogList()
        self.main_widget = QStackedWidget()
        self.main_widget.addWidget(self.dialog_menu)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle(variables.APP_NAME)
        self.setWindowIcon(QIcon(variables.LOGO_IMG))

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        variables.window_width = self.size().width()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
