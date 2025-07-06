from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGroupBox, QCheckBox, 
    QLineEdit, QPushButton, QFileDialog, QComboBox,
    QMessageBox, QFrame, QFormLayout, QHBoxLayout, 
    QLabel, QWidget, QTabWidget, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.translations import translations

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.launcher = parent
        self.current_language = self.launcher.settings.get('language', 'en')
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle(translations[self.current_language]['settings_title'])
        self.setMinimumSize(600, 500)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        self.tabs = QTabWidget()
        
        self.setup_general_tab()
        self.setup_osu_tab()
        self.setup_appearance_tab()
        
        main_layout.addWidget(self.tabs)
        self.setup_dialog_buttons(main_layout)
        
        self.load_current_settings()
        self.apply_styles()

    def setup_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Launcher settings
        launcher_group = QGroupBox(translations[self.current_language]['launcher_settings'])
        launcher_layout = QVBoxLayout()
        
        self.fullscreen_cb = QCheckBox(translations[self.current_language]['fullscreen_checkbox'])
        self.save_positions_cb = QCheckBox(translations[self.current_language]['save_positions_checkbox'])
        self.save_positions_cb.setChecked(True)
        
        # Language selection
        language_group = QGroupBox(translations[self.current_language]['language_label'])
        language_layout = QHBoxLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Deutsch", "de")
        self.language_combo.setCurrentText("English" if self.current_language == "en" else "Deutsch")
        
        language_layout.addWidget(self.language_combo)
        language_group.setLayout(language_layout)
        
        # Widget positions
        pos_group = QGroupBox(translations[self.current_language]['reset_positions_button'])
        pos_layout = QVBoxLayout()
        
        reset_btn = QPushButton(translations[self.current_language]['reset_positions_button'])
        reset_btn.clicked.connect(self.reset_widget_positions)
        
        pos_layout.addWidget(reset_btn)
        pos_group.setLayout(pos_layout)
        
        launcher_layout.addWidget(self.fullscreen_cb)
        launcher_layout.addWidget(self.save_positions_cb)
        launcher_layout.addWidget(language_group)
        launcher_group.setLayout(launcher_layout)
        
        layout.addWidget(launcher_group)
        layout.addWidget(pos_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, translations[self.current_language]['general_tab'])

    def setup_osu_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Server settings
        server_group = QGroupBox(translations[self.current_language]['server_settings'])
        server_layout = QVBoxLayout()
        
        server_container = QWidget()
        server_hbox = QHBoxLayout(server_container)
        server_hbox.setContentsMargins(0, 0, 0, 0)
        
        server_hbox.addWidget(QLabel(translations[self.current_language]['server_label']))
        self.server_combo = QComboBox()
        self.server_combo.addItems(["Bancho", "EternityGlow"])
        server_hbox.addWidget(self.server_combo)
        
        server_layout.addWidget(server_container)
        server_group.setLayout(server_layout)
        
        # Start options
        options_group = QGroupBox(translations[self.current_language]['start_options'])
        options_layout = QVBoxLayout()
        
        self.force_fullscreen_cb = QCheckBox(translations[self.current_language]['force_fullscreen'])
        self.nomusic_cb = QCheckBox(translations[self.current_language]['disable_music'])
        self.novideo_cb = QCheckBox(translations[self.current_language]['disable_videos'])
        
        options_layout.addWidget(self.force_fullscreen_cb)
        options_layout.addWidget(self.nomusic_cb)
        options_layout.addWidget(self.novideo_cb)
        options_group.setLayout(options_layout)
        
        # Osu! path
        path_group = QGroupBox(translations[self.current_language]['osu_installation'])
        path_layout = QVBoxLayout()
        
        self.osu_path = QLineEdit()
        self.osu_path.setPlaceholderText(translations[self.current_language]['select_image'])
        path_btn = QPushButton(translations[self.current_language]['select_image'])
        path_btn.clicked.connect(self.browse_osu_path)
        
        path_hbox = QHBoxLayout()
        path_hbox.addWidget(self.osu_path)
        path_hbox.addWidget(path_btn)
        
        path_layout.addLayout(path_hbox)
        path_group.setLayout(path_layout)
        
        layout.addWidget(server_group)
        layout.addWidget(options_group)
        layout.addWidget(path_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, translations[self.current_language]['osu_tab'])

    def setup_appearance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Background
        bg_group = QGroupBox(translations[self.current_language]['background_settings'])
        bg_layout = QVBoxLayout()
        
        self.bg_cb = QCheckBox(translations[self.current_language]['custom_background'])
        self.bg_path = QLineEdit()
        self.bg_path.setPlaceholderText(translations[self.current_language]['select_image'])
        self.bg_path.setReadOnly(True)
        
        browse_btn = QPushButton(translations[self.current_language]['select_image'])
        browse_btn.clicked.connect(self.browse_bg)
        
        bg_hbox = QHBoxLayout()
        bg_hbox.addWidget(self.bg_path)
        bg_hbox.addWidget(browse_btn)
        
        bg_layout.addWidget(self.bg_cb)
        bg_layout.addLayout(bg_hbox)
        bg_group.setLayout(bg_layout)
        
        # Opacity
        opacity_group = QGroupBox(translations[self.current_language]['window_appearance'])
        opacity_layout = QVBoxLayout()
        
        opacity_container = QWidget()
        opacity_hbox = QHBoxLayout(opacity_container)
        opacity_hbox.setContentsMargins(0, 0, 0, 0)
        
        opacity_hbox.addWidget(QLabel(translations[self.current_language]['widget_opacity']))
        self.opacity_slider = QSpinBox()
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setSuffix("%")
        self.opacity_slider.setSingleStep(5)
        opacity_hbox.addWidget(self.opacity_slider)
        
        opacity_layout.addWidget(opacity_container)
        opacity_group.setLayout(opacity_layout)
        
        layout.addWidget(bg_group)
        layout.addWidget(opacity_group)
        layout.addStretch()
        
        self.tabs.addTab(tab, translations[self.current_language]['appearance_tab'])

    def setup_dialog_buttons(self, layout):
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.reset_btn = QPushButton(translations[self.current_language]['default_values'])
        self.reset_btn.clicked.connect(self.reset_defaults)
        
        self.cancel_btn = QPushButton(translations[self.current_language]['cancel'])
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton(translations[self.current_language]['save'])
        self.save_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        
        layout.addWidget(btn_container)

    def browse_bg(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            translations[self.current_language]['select_image'], 
            "", 
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.bg_path.setText(path)
            self.bg_cb.setChecked(True)

    def browse_osu_path(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            translations[self.current_language]['select_image'],
            "",
            "osu! Executable (osu!.exe)"
        )
        if path:
            self.osu_path.setText(path)

    def reset_widget_positions(self):
        reply = QMessageBox.question(
            self, 
            translations[self.current_language]['reset_positions_button'],
            translations[self.current_language]['reset_positions_confirm'],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            default_pos = {'side_buttons': {'x': 1080, 'y': 650}}
            self.launcher.settings['widget_positions'] = default_pos
            self.launcher.load_widget_positions()
            QMessageBox.information(
                self, 
                translations[self.current_language]['success'], 
                translations[self.current_language]['positions_reset'],
                QMessageBox.StandardButton.Ok
            )

    def reset_defaults(self):
        reply = QMessageBox.question(
            self,
            translations[self.current_language]['default_values'],
            translations[self.current_language]['reset_defaults_confirm'],
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.launcher.settings = {
                'language': 'en',
                'launcher': {
                    'fullscreen': True,
                    'save_positions': True
                },
                'osu': {
                    'server': 'EternityGlow',
                    'force_fullscreen': True,
                    'nomusic': False,
                    'novideo': False,
                    'path': ''
                },
                'background': {
                    'enabled': False,
                    'path': ''
                },
                'widget_positions': {'side_buttons': {'x': 1080, 'y': 650}},
                'opacity': 80
            }
            self.load_current_settings()

    def load_current_settings(self):
        settings = self.launcher.settings
        
        # General
        self.fullscreen_cb.setChecked(settings.get('launcher', {}).get('fullscreen', True))
        self.save_positions_cb.setChecked(settings.get('launcher', {}).get('save_positions', True))
        
        # osu!
        self.server_combo.setCurrentText(settings.get('osu', {}).get('server', 'EternityGlow'))
        self.force_fullscreen_cb.setChecked(settings.get('osu', {}).get('force_fullscreen', True))
        self.nomusic_cb.setChecked(settings.get('osu', {}).get('nomusic', False))
        self.novideo_cb.setChecked(settings.get('osu', {}).get('novideo', False))
        self.osu_path.setText(settings.get('osu', {}).get('path', ''))
        
        # Appearance
        bg_settings = settings.get('background', {})
        self.bg_cb.setChecked(bg_settings.get('enabled', False))
        self.bg_path.setText(bg_settings.get('path', ''))
        self.opacity_slider.setValue(settings.get('opacity', 80))
        
        # Language
        self.current_language = settings.get('language', 'en')
        self.language_combo.setCurrentText("English" if self.current_language == "en" else "Deutsch")

    def get_settings(self):
        return {
            'language': self.language_combo.currentData(),
            'launcher': {
                'fullscreen': self.fullscreen_cb.isChecked(),
                'save_positions': self.save_positions_cb.isChecked()
            },
            'osu': {
                'server': self.server_combo.currentText(),
                'force_fullscreen': self.force_fullscreen_cb.isChecked(),
                'nomusic': self.nomusic_cb.isChecked(),
                'novideo': self.novideo_cb.isChecked(),
                'path': self.osu_path.text()
            },
            'background': {
                'enabled': self.bg_cb.isChecked(),
                'path': self.bg_path.text()
            },
            'widget_positions': self.launcher.settings.get('widget_positions', {}),
            'opacity': self.opacity_slider.value()
        }

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: rgba(35, 35, 45, 230);
                border: 2px solid #ff66aa;
                border-radius: 8px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 102, 170, 50);
                border-radius: 5px;
                margin-top: 5px;
            }
            QTabBar::tab {
                background: rgba(0, 0, 0, 120);
                color: white;
                padding: 8px 15px;
                border: 1px solid rgba(255, 102, 170, 80);
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(255, 102, 170, 150);
                border-color: #ff66aa;
            }
            QGroupBox {
                color: #ff66aa;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid rgba(255, 102, 170, 80);
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QCheckBox, QLabel {
                color: white;
                font-size: 13px;
            }
            QLineEdit, QComboBox, QSpinBox {
                background: rgba(0, 0, 0, 120);
                color: white;
                border: 1px solid rgba(255, 102, 170, 80);
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton {
                background: rgba(0, 0, 0, 150);
                color: white;
                border: 1px solid rgba(255, 102, 170, 80);
                border-radius: 5px;
                padding: 7px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: rgba(255, 102, 170, 120);
                border-color: white;
            }
            QPushButton:pressed {
                background: rgba(255, 102, 170, 180);
            }
        """)

    def accept(self):
        new_language = self.language_combo.currentData()
        if new_language != self.current_language:
            self.current_language = new_language
            # Aktualisiere die UI sofort
            self.retranslate_ui()
    
        self.launcher.settings = self.get_settings()
        self.launcher.save_settings()
        self.launcher.apply_settings()  # Wichtig: Launcher muss die Änderung übernehmen
        super().accept()

    def retranslate_ui(self):
        """Update all UI elements with current language"""
        self.setWindowTitle(translations[self.current_language]['settings_title'])
        
        # General tab
        self.tabs.setTabText(0, translations[self.current_language]['general_tab'])
        self.tabs.setTabText(1, translations[self.current_language]['osu_tab'])
        self.tabs.setTabText(2, translations[self.current_language]['appearance_tab'])
        
        # Buttons
        self.reset_btn.setText(translations[self.current_language]['default_values'])
        self.cancel_btn.setText(translations[self.current_language]['cancel'])
        self.save_btn.setText(translations[self.current_language]['save'])