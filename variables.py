from PyQt5.QtCore import (
    QMargins,
)

window_width = 0
font = 0
nw = 0

USER_ME = 0
USER_THEM = 1
STATUS_UNDELIVERED = 0
STATUS_UNREAD = 1
STATUS_READ = 2
BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#a5d6a7"}
STATUS_COLOR = "#0d7edb"
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
TIMEOUT = 500
