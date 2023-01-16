import sys
import os
import urllib.request
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *

class WebPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(sys.argv[2])
        self.setWindowIcon(
            QIcon(sys.argv[3])
        )

        self.web_view = QWebEngineView()
        self.web_view.load(
            QUrl(sys.argv[1])
        )

        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        self.setGeometry(200, 200, 1280, 720)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        #self.setWindowFlags(Qt.Tool | Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        self.setMinimumSize(1280, 720)

def run() -> int:
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=3"

    app = QApplication(sys.argv)
    app.setStyleSheet('QFrame { border: 0; }')

    web_page = WebPage()
    web_page.show()
    exit_code = app.exec_()

    # with open('close_app', 'wb') as file: 
    #     file.write(b'Close the damn app')

    

    url = f'{sys.argv[1]}/close'
    urllib.request.urlopen(url)

    return exit_code

if __name__ == '__main__':
    sys.exit(run())