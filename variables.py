from PyQt5.QtCore import (
    QMargins,
    QObject,
    pyqtSignal,
)

class DialogSignals(QObject):
    open_dialog = pyqtSignal(int)
    create_dialog = pyqtSignal(str)
    close_dialog = pyqtSignal()

    def __init__(self):
        super(DialogSignals, self).__init__()

signals = 0
window_width = 0
font = 0
font_small = 0
nw = 0
dialog_height = 0

USER_ME = 0
USER_THEM = 1
STATUS_UNDELIVERED = 0
STATUS_UNREAD = 1
STATUS_READ = 2
STATUS_NEW = 3
BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#a5d6a7"}
STATUS_COLOR = "#98b9d3"
STATUS_NEW_COLOR = "#328cff"
HIGHLIGHT_COLOR = "#c1eafd"
BUBBLE_PADDING = QMargins(15, 5, 15, 5)
TEXT_PADDING = QMargins(25, 15, 25, 15)
IP_PADDING = QMargins(25, 15, 25, 10)
MSG_PADDING = QMargins(50, 5, 65, 15)
WINDOW_PADDING = 30
MAX_ROWS = 8
APP_NAME = "LobsterMessage"
FONT_SIZE = 14
FONT_SIZE_SMALL = 12
FONT_FILE = ":/fonts/lobster.ttf"
PLACEHOLDER_TEXT = "Enter message"
LOGO_IMG = ":/img/logo.png"
SEND_IDLE_IMG = ":/img/send1.png"
SEND_HOVER_IMG = ":/img/send2.png"
SEND_PRESS_IMG = ":/img/send3.png"
BACK_IDLE_IMG = ":/img/back1.png"
BACK_HOVER_IMG = ":/img/back2.png"
BACK_PRESS_IMG = ":/img/back3.png"
TIMEOUT = 500
