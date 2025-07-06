from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class BrowserTab(QWidget):
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setup_browser(url)
        
    def setup_browser(self, url):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QWebEngineView()
        self.browser.load(QUrl(url))
        layout.addWidget(self.browser)