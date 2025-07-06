import os
import json
import sys
import time
import subprocess
import psutil
import logging
import webbrowser
import requests
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton,
    QStackedWidget, QTabWidget, QMessageBox, QProgressBar,
    QGridLayout, QDialog, QFileDialog, QLabel
)
from PyQt6.QtGui import QPalette, QBrush, QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from core.settings import SettingsDialog
from core.browser import BrowserTab
from core.draggable_widgets import DraggableWidget
from core.tablet_calculator import TabletAreaCalculator
from core.translations import translations
from core.discord_rpc import DiscordRPC
from config import GITHUB_TOKEN, REPO, CURRENT_VERSION

logging.basicConfig(filename='launcher.log', level=logging.DEBUG)

class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_language = 'en'
        self.rpc = DiscordRPC()
        self.init_components()
        self.setup_ui()
        self.apply_settings()
        self.calculator = None

    def showEvent(self, event):
        """Wird beim Start des Launchers aufgerufen"""
        super().showEvent(event)
        self.rpc.connect()
        self.update_discord_status()
        QTimer.singleShot(2000, self.check_for_updates)  # Update-Check nach 2 Sekunden

    def check_for_updates(self):
        """Prüft auf Updates im Hintergrund"""
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            url = f"https://api.github.com/repos/{REPO}/releases/latest"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data["tag_name"] != CURRENT_VERSION:
                self.show_update_dialog(data["assets"][0]["browser_download_url"])
        except Exception as e:
            logging.error(f"Update-Check fehlgeschlagen: {str(e)}")

    def show_update_dialog(self, download_url: str):
        """Zeigt den Update-Dialog an"""
        msg = QMessageBox(self)
        msg.setWindowTitle(translations[self.current_language].get('update_available', 'Update verfügbar'))
        msg.setText(f"{translations[self.current_language].get('new_version', 'Neue Version')} {CURRENT_VERSION} {translations[self.current_language].get('available', 'verfügbar')}!")
        msg.setInformativeText(translations[self.current_language].get('download_question', 'Möchten Sie jetzt aktualisieren?'))

        download_btn = msg.addButton(translations[self.current_language].get('download', 'Herunterladen'), QMessageBox.ButtonRole.AcceptRole)
        later_btn = msg.addButton(translations[self.current_language].get('later', 'Später'), QMessageBox.ButtonRole.RejectRole)
        
        # Style-Anpassung
        download_btn.setStyleSheet("""
            background: #ff66aa;
            color: white;
            border-radius: 8px;
            padding: 8px 15px;
            min-width: 100px;
            font-weight: bold;
        """)
        later_btn.setStyleSheet("""
            background: rgba(0,0,0,180);
            color: white;
            border: 2px solid #ff66aa;
            border-radius: 8px;
            padding: 8px 15px;
            min-width: 100px;
        """)

        msg.exec()
        
        if msg.clickedButton() == download_btn:
            webbrowser.open(download_url)
            self.close()

    def update_discord_status(self, status="In Launcher"):
        """Aktualisiert den Discord Status"""
        details = {
            'bancho': 'On Bancho Server',
            'eternityglow': 'On EternityGlow Server'
        }.get(self.selected_server, 'Custom Server')
        self.rpc.update_presence(state=status, details=details)

    def init_components(self):
        self.settings = self.load_settings()
        self.current_language = self.settings.get('language', 'en')
        self.selected_server = self.settings.get('osu', {}).get('server', 'bancho').lower()
        self.main_container = QStackedWidget()
        self.main_page = None
        self.sidebar = None
        self.play_btn = None
        self.browser_tabs = None
        self.progress = None
        self.osu_process = None
        self.osu_pid = None
        self.osu_check_timer = None

    def load_settings(self):
        try:
            with open('launcher_settings.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                'language': 'en',
                'launcher': {'fullscreen': True},
                'osu': {'server': 'EternityGlow', 'force_fullscreen': True},
                'background': {'enabled': False, 'path': ''},
                'widget_positions': {'side_buttons': {'x': 1080, 'y': 650}}
            }

    def setup_ui(self):
        self.setWindowTitle("EternityGlow Launcher")
        self.setWindowIcon(QIcon("resources/eternityglow.ico"))
        self.main_container = QStackedWidget()
        self.setCentralWidget(self.main_container)
        self.create_main_page()
        self.setup_browser_interface()
        self.load_widget_positions()

    def create_main_page(self):
        self.main_page = QWidget()
        self.main_page.setObjectName("MainPage")
        self.main_layout = QGridLayout(self.main_page)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_play_button()
        self.setup_sidebar()
        self.main_container.addWidget(self.main_page)

    def setup_play_button(self):
        self.play_btn = QPushButton("Play osu!")
        self.play_btn.setFixedSize(325, 100)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,180);
                color: white;
                border: 3px solid #ff66aa;
                border-radius: 20px;
                font-size: 42px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,102,170,150);
                border-color: white;
            }
            QPushButton:disabled {
                background: rgba(100,100,100,180);
                border-color: #888;
            }
        """)
        self.play_btn.clicked.connect(self.start_osu)
        self.main_layout.addWidget(self.play_btn, 0, 0, alignment=Qt.AlignmentFlag.AlignCenter)

    def start_osu(self):
        self.play_btn.setEnabled(False)
        self.show_loading_bar()
        self.update_discord_status("Starting osu!")
        
        try:
            osu_path = self.find_osu_executable()
            if osu_path:
                self.launch_osu(osu_path)
                self.update_discord_status("Playing osu!")
            else:
                raise FileNotFoundError("osu!.exe not found")
        except Exception as e:
            self.update_discord_status("Launcher Error")
            self.handle_osu_start_error(e)

    def find_osu_executable(self):
        standard_paths = [
            os.path.expanduser("~/AppData/Local/osu!/osu!.exe"),
            "C:/Program Files/osu!/osu!.exe",
            "C:/Program Files (x86)/osu!/osu!.exe"
        ]
        
        for path in standard_paths:
            if os.path.exists(path):
                return path
        
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Locate osu!.exe",
            "",
            "osu! Executable (osu!.exe)"
        )
        return path if path else None

    def launch_osu(self, osu_path):
        params = [osu_path]
        if self.selected_server == "eternityglow":
            params.extend(["-devserver", "eternityglow.de"])
        
        if self.settings.get('osu', {}).get('nomusic', False):
            params.append("-nomusic")
        if self.settings.get('osu', {}).get('novideo', False):
            params.append("-novideo")
        
        params.append("-legacytablet")
        if self.settings.get('osu', {}).get('force_fullscreen', True):
            params.append("-fullscreen")
        else:
            params.append("-window")
        
        try:
            self.osu_process = subprocess.Popen(params, shell=True)
            self.osu_pid = self.osu_process.pid
            self.osu_check_timer = QTimer(self)
            self.osu_check_timer.timeout.connect(self.check_osu_process)
            self.osu_check_timer.start(3000)
            
            QTimer.singleShot(2500, lambda: [
                self.progress.setValue(100),
                QTimer.singleShot(500, self.hide)
            ])
        except Exception as e:
            self.handle_osu_start_error(e)

    def check_osu_process(self):
        if not hasattr(self, 'osu_pid'):
            return
        
        try:
            process = psutil.Process(self.osu_pid)
            if process.status() == psutil.STATUS_ZOMBIE or not process.is_running():
                self.restart_launcher()
        except psutil.NoSuchProcess:
            self.restart_launcher()

    def restart_launcher(self):
        if hasattr(self, 'osu_check_timer') and self.osu_check_timer:
            self.osu_check_timer.stop()
        
        try:
            if sys.executable:
                subprocess.Popen([sys.executable, *sys.argv])
        except Exception as e:
            print(f"Error restarting launcher: {e}")
        finally:
            self.close()

    def handle_osu_start_error(self, error):
        if self.progress:
            self.progress.hide()
        self.play_btn.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "Error",
            f"Failed to start osu!:\n{str(error)}",
            QMessageBox.StandardButton.Ok
        )

    def show_loading_bar(self):
        self.progress = QProgressBar(self)
        self.progress.setFixedSize(400, 20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ff66aa;
                border-radius: 5px;
                background: rgba(0,0,0,150);
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff66aa, stop:1 #ff0066
                );
            }
        """)
        self.progress.move(self.width()//2 - 200, self.height()//2 + 50)
        self.progress.show()
    
        self.progress.setValue(0)
        self.loading_timer = QTimer(self)
        self.loading_timer.timeout.connect(
            lambda: self.progress.setValue(min(self.progress.value() + 2, 90)))
        self.loading_timer.start(50)

    def setup_sidebar(self):
        self.sidebar = DraggableWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedSize(200, 350)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)
        
        buttons = [
            ("Leaderboard", "https://eternityglow.de/leaderboard.php?id=100&mode=0"),
            ("Wiki", "https://wiki.eternityglow.de/de/home"),
            ("Tablet Tool", None),
            ("Settings", None),
            ("Exit", None)
        ]
        
        for text, url in buttons:
            btn = self.create_button(text, url)
            if text == "Tablet Tool":
                btn.clicked.connect(self.show_tablet_calculator)
            elif text == "Settings":
                btn.clicked.connect(self.show_settings)
            elif text == "Exit":
                btn.clicked.connect(self.close)
            else:
                btn.clicked.connect(lambda _, u=url: self.open_web_tab(u))
            
            sidebar_layout.addWidget(btn)
        
        self.main_layout.addWidget(self.sidebar, 0, 0, 
                                alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

    def show_tablet_calculator(self):
        try:
            if hasattr(self, 'calculator') and self.calculator:
                self.calculator.close()
            
            self.calculator = TabletAreaCalculator()
            self.calculator.setWindowTitle("Tablet Area Tool")
            self.calculator.setStyleSheet(self.styleSheet())
            self.calculator.setWindowModality(Qt.WindowModality.ApplicationModal)
        
            self.calculator.destroyed.connect(lambda: setattr(self, 'calculator', None))
        
            self.calculator.show()
            self.calculator.raise_()
            self.calculator.activateWindow()
        
        except Exception as e:
            logging.error(f"Tablet Tool Error: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                "Could not open tablet tool:\n" + str(e),
                QMessageBox.StandardButton.Ok
            )

    def show_settings(self):
        self.update_discord_status("Settings")
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
            self.apply_settings()

    def create_button(self, text, url=None):
        btn = QPushButton(text)
        btn.setFixedHeight(40)
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,180);
                color: white;
                border: 2px solid #ff66aa;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background: rgba(255,102,170,150);
                border-color: white;
            }
        """)
        return btn

    def setup_browser_interface(self):
        self.browser_tabs = QTabWidget()
        self.browser_tabs.setTabsClosable(True)
        self.browser_tabs.tabCloseRequested.connect(self.close_tab)
        
        back_btn = QPushButton("Back to Launcher")
        back_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,180);
                color: white;
                border: 2px solid #ff66aa;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background: rgba(255,102,170,150);
                border-color: white;
            }
        """)
        back_btn.clicked.connect(self.show_main_page)
        
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(back_btn)
        browser_layout.addWidget(self.browser_tabs)
    
        browser_container = QWidget()
        browser_container.setLayout(browser_layout)
        self.main_container.addWidget(browser_container)
        browser_container.hide()

    def open_web_tab(self, url):
        site_name = url.split('//')[-1].split('/')[0]
        self.update_discord_status(f"Viewing {site_name}")
        for i in range(self.browser_tabs.count()):
            if self.browser_tabs.widget(i).browser.url().toString() == url:
                self.browser_tabs.setCurrentIndex(i)
                self.show_browser_page()
                return
        
        tab = BrowserTab(url)
        title = url.split('//')[-1].split('/')[0]
        self.browser_tabs.addTab(tab, title)
        self.show_browser_page()

    def close_tab(self, index):
        self.browser_tabs.removeTab(index)
        if self.browser_tabs.count() == 0:
            self.main_container.setCurrentIndex(0)
            self.main_page.show()
            self.main_container.widget(1).hide()

    def show_main_page(self):
        self.main_container.setCurrentIndex(0)
        self.main_page.show()
        self.main_container.widget(1).hide()

    def show_browser_page(self):
        self.main_container.setCurrentIndex(1)

    def apply_settings(self):
        if self.settings.get('launcher', {}).get('fullscreen', True):
            self.showFullScreen()
        else:
            self.showNormal()
        
        self.selected_server = self.settings.get('osu', {}).get('server', 'bancho').lower()
        self.set_background()

    def set_background(self):
        bg_config = self.settings.get('background', {})
        if bg_config.get('enabled', False) and os.path.exists(bg_config.get('path', '')):
            bg_path = bg_config['path']
        else:
            bg_path = "resources/menu-background2x.jpg"
        
        try:
            palette = QPalette()
            palette.setBrush(
                QPalette.ColorRole.Window,
                QBrush(QPixmap(bg_path).scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )))
            self.setPalette(palette)
        except Exception:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
            self.setPalette(palette)

    def save_widget_positions(self):
        if hasattr(self, 'sidebar'):
            self.settings['widget_positions'] = {
                'side_buttons': {
                    'x': self.sidebar.x(),
                    'y': self.sidebar.y()
                }
            }
            self.save_settings()

    def load_widget_positions(self):
        positions = self.settings.get('widget_positions', {})
        if 'side_buttons' in positions and hasattr(self, 'sidebar'):
            pos = positions['side_buttons']
            self.sidebar.move(pos['x'], pos['y'])

    def save_settings(self):
        with open('launcher_settings.json', 'w') as f:
            json.dump(self.settings, f, indent=4)

    def closeEvent(self, event):
        try:
            if hasattr(self, 'osu_check_timer') and self.osu_check_timer:
                self.osu_check_timer.stop()
            
            if hasattr(self, 'calculator') and self.calculator:
                self.calculator.close()
            
            self.save_widget_positions()
            self.rpc.close()
        except Exception as e:
            logging.error(f"Error during close: {str(e)}")
        finally:
            super().closeEvent(event)