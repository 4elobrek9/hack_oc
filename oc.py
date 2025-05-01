import os
import sys
import json
from bs4 import BeautifulSoup
import subprocess
import platform
import locale
import psutil
import time
import speech_recognition as sr
import threading
import requests
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QLineEdit, QLabel, QTabWidget, QPushButton, 
                            QListWidget, QFileSystemModel, QTreeView, QSplitter, 
                            QGraphicsOpacityEffect, QFrame, QScrollArea, QMenu, 
                            QAction, QComboBox, QToolButton, QDialog, QVBoxLayout, 
                            QLineEdit, QLabel, QDialogButtonBox, QStackedWidget,
                            QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem  )
from PyQt5.QtCore import Qt, QTimer, QDir, QSize, QPropertyAnimation, QEasingCurve, QPoint, QUrl, QRectF, QStandardPaths
from PyQt5.QtGui import (QFont, QColor, QPalette, QTextCursor, QIcon, QFontDatabase,
                         QCursor, QKeySequence, QPixmap, QPainter, QBrush, QPen,
                         QLinearGradient, QRadialGradient)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage

if sys.platform == 'win32':
    locale.setlocale(locale.LC_ALL, 'rus_rus')
    os.system('chcp 65001 > nul')  # UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def get_ip():
    """Получает внешний IP адрес"""
    try:
        return requests.get('https://ident.me', timeout=5).text.strip()
    except:
        return None

def get_city_by_ip(ip):
    """Определяет город по IP"""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}?fields=city')
        data = response.json()
        return data.get('city', 'неизвестно')
    except:
        return 'неизвестно'

def get_yandex_weather(city):
    """Резервный вариант через Яндекс"""
    try:
        url = f"https://yandex.ru/pogoda/{city.lower()}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Альтернативные селекторы для Яндекса
        temp = soup.select_one('.temp.fact__temp .temp__value').text
        weather = soup.select_one('.link__condition.day-anchor').text
        
        return {
            'city': city,
            'temp': temp + '°C',
            'weather': weather.lower()
        }
    except Exception as e:
        print(f"Yandex weather error: {e}")
        return None
    
def get_weather():
    """Основная функция получения погоды"""
    try:
        ip = get_ip()
        city = get_city_by_ip(ip)
        
        if not city or city == "неизвестно":
            city = "Москва"  # Значение по умолчанию
        
        # Сначала пробуем получить через Яндекс
        weather_data = get_yandex_weather(city)
        
        if not weather_data:
            # Если Яндекс не сработал, используем Open-Meteo
            url = f"https://api.open-meteo.com/v1/forecast?latitude=55.75&longitude=37.61&current_weather=true"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            temp = data['current_weather']['temperature']
            weather_code = data['current_weather']['weathercode']
            
            # Преобразуем код погоды в текстовое описание
            weather_descriptions = {
                0: 'ясно',
                1: 'преимущественно ясно',
                2: 'переменная облачность',
                3: 'пасмурно',
                45: 'туман',
                48: 'туман с инеем',
                51: 'легкая морось',
                53: 'морось',
                55: 'сильная морось',
                56: 'легкий моросящий дождь',
                57: 'моросящий дождь',
                61: 'небольшой дождь',
                63: 'дождь',
                65: 'сильный дождь',
                66: 'ледяной дождь',
                67: 'сильный ледяной дождь',
                71: 'небольшой снег',
                73: 'снег',
                75: 'сильный снег',
                77: 'снежные зерна',
                80: 'небольшие ливни',
                81: 'ливни',
                82: 'сильные ливни',
                85: 'небольшой снегопад',
                86: 'сильный снегопад',
                95: 'гроза',
                96: 'гроза с градом',
                99: 'сильная гроза с градом'
            }
            
            weather = weather_descriptions.get(weather_code, 'неизвестно')
            
            weather_data = {
                'city': city,
                'temp': f"{temp}°C",
                'weather': weather
            }
            
        return weather_data
        
    except Exception as e:
        print(f"Ошибка получения погоды: {e}")
        return None

class VoiceAssistant(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def run(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        while self.running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5)
                
                text = self.recognizer.recognize_google(audio, language="ru-RU")
                self.callback(text)
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Voice recognition error: {e}")
                time.sleep(1)
    
    def stop(self):
        self.running = False

class BrowserTab(QWidget):
    def __init__(self, profile=None):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Navigation bar
        self.nav_bar = QHBoxLayout()
        
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(30, 30)
        self.back_btn.clicked.connect(self.navigate_back)
        
        self.forward_btn = QPushButton(">")
        self.back_btn.setFixedSize(30, 30)
        self.forward_btn.clicked.connect(self.navigate_forward)
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(30, 30)
        self.refresh_btn.clicked.connect(self.refresh_page)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        self.go_btn = QPushButton("Go")
        self.go_btn.setFixedSize(50, 30)
        self.go_btn.clicked.connect(self.navigate_to_url)
        
        self.nav_bar.addWidget(self.back_btn)
        self.nav_bar.addWidget(self.forward_btn)
        self.nav_bar.addWidget(self.refresh_btn)
        self.nav_bar.addWidget(self.url_bar)
        self.nav_bar.addWidget(self.go_btn)
        
        # Web view with modern settings
        if profile:
            self.web_view = QWebEngineView()
            self.web_page = QWebEnginePage(profile, self.web_view)
            self.web_view.setPage(self.web_page)
        else:
            self.web_view = QWebEngineView()
        
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        
        # Security settings
        profile = self.web_view.page().profile()
        profile.setHttpAcceptLanguage("en-US,en;q=0.9")
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        
        # Modern CSP policy
        csp = ("default-src 'self'; "
               "script-src 'self' 'unsafe-eval'; "
               "style-src 'self' 'unsafe-inline'; "
               "img-src 'self' data:; "
               "connect-src 'self';")
        
        self.web_view.urlChanged.connect(self.update_url)
        
        self.layout.addLayout(self.nav_bar)
        self.layout.addWidget(self.web_view)
        
        # Load start page
        self.load_url("https://www.google.com")
    
    def load_url(self, url):
        self.web_view.load(QUrl(url))
        self.url_bar.setText(url)
    
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        self.load_url(url)
    
    def navigate_back(self):
        self.web_view.back()
    
    def navigate_forward(self):
        self.web_view.forward()
    
    def refresh_page(self):
        self.web_view.reload()
    
    def update_url(self, url):
        self.url_bar.setText(url.toString())

class TelegramChat(QWidget):
    def __init__(self, profile=None):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Title
        self.title = QLabel("Telegram Chat")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        # Web view for Telegram Web with fixes
        if profile:
            self.web_view = QWebEngineView()
            self.web_page = QWebEnginePage(profile, self.web_view)
            self.web_view.setPage(self.web_page)
        else:
            self.web_view = QWebEngineView()
            
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        
        self.web_view.load(QUrl("https://web.telegram.org/"))
        
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.web_view)

class HackerTerminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(False)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0a1922;
                color: #64f5d2;
                font-family: Hack, Consolas, 'Courier New', monospace;
                font-size: 14px;
                border: 1px solid #1e4a5f;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        font = QFont("Hack", 12)
        self.setFont(font)
        
    def append(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text + "\n")
        self.moveCursor(QTextCursor.End)

    def execute_command(self, command):
        try:
            # Для команд Windows используем правильную кодировку
            if sys.platform == 'win32':
                process = subprocess.Popen(
                    command, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                process = subprocess.Popen(
                    command, 
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    universal_newlines=True
                )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                self.append(stdout)
            if stderr:
                self.append(f"Error: {stderr}")
                
        except Exception as e:
            self.append(f"Command execution error: {str(e)}")

def open_in_vscode(self, path):
    try:
        if sys.platform == 'win32':
            # Для Windows используем корректный путь к VSCode
            vscode_path = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'Microsoft VS Code', 'Code.exe')
            if os.path.exists(vscode_path):
                subprocess.Popen([vscode_path, path])
            else:
                # Альтернативный способ открытия
                os.startfile(path)
        else:
            # Для Linux/Mac
            subprocess.Popen(["code", path])
    except Exception as e:
        error_msg = f"Error opening in VSCode: {str(e)}"
        current_tab = self.tab_widget.currentWidget()
        if isinstance(current_tab, HackerTerminal):
            current_tab.append(error_msg)
        else:
            print(error_msg)

def show_file_context_menu(self, position):
    index = self.file_explorer.indexAt(position)
    if not index.isValid():
        return
        
    file_path = self.model.filePath(index)
    menu = QMenu()
    
    open_action = QAction("Open", self)
    open_action.triggered.connect(lambda: self.open_file(index))
    menu.addAction(open_action)
    
    open_with_vscode = QAction("Open in VSCode", self)
    open_with_vscode.triggered.connect(lambda: self.open_in_vscode(file_path))
    menu.addAction(open_with_vscode)
    
    copy_path_action = QAction("Copy path", self)
    copy_path_action.triggered.connect(lambda: self.copy_file_path(file_path))
    menu.addAction(copy_path_action)
    
    run_as_admin_action = QAction("Run as administrator", self)
    run_as_admin_action.triggered.connect(lambda: self.run_as_admin(file_path))
    menu.addAction(run_as_admin_action)
    
    menu.exec_(self.file_explorer.viewport().mapToGlobal(position))

class DockItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, app_name, parent=None):
        super().__init__(pixmap, parent)
        self.app_name = app_name
        self.setAcceptHoverEvents(True)
        self.setTransformationMode(Qt.SmoothTransformation)
        
    def hoverEnterEvent(self, event):
        self.setScale(1.2)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        self.setScale(1.0)
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.scene().parent().launch_app(self.app_name)
        super().mousePressEvent(event)

class DockView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")
        
        # Dock background
        self.dock_bg = QGraphicsRectItem(QRectF(0, 0, 400, 80))
        gradient = QLinearGradient(0, 0, 0, 80)
        gradient.setColorAt(0, QColor(10, 25, 34, 200))
        gradient.setColorAt(1, QColor(30, 74, 95, 200))
        self.dock_bg.setBrush(QBrush(gradient))
        self.dock_bg.setPen(QPen(Qt.NoPen))
        self.scene().addItem(self.dock_bg)
        
        # Add apps to dock
        self.apps = {
            "steam": ("Steam", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/1024px-Steam_icon_logo.svg.png"),
            "terminal": ("Terminal", "https://cdn-icons-png.flaticon.com/512/906/906308.png"),
            "browser": ("Browser", "https://cdn-icons-png.flaticon.com/512/732/732220.png"),
            "telegram": ("Telegram", "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/1024px-Telegram_logo.svg.png")
        }
        
        self.load_app_icons()
        
    def load_app_icons(self):
        x_pos = 20
        for app_name, (display_name, icon_url) in self.apps.items():
            try:
                response = requests.get(icon_url)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                item = DockItem(pixmap, app_name)
                item.setPos(x_pos, 8)
                self.scene().addItem(item)
                
                # Add label
                label = self.scene().addText(display_name)
                label.setDefaultTextColor(QColor(100, 255, 210))
                label.setPos(x_pos + 32 - label.boundingRect().width()/2, 74)
                
                x_pos += 80
            except Exception as e:
                print(f"Error loading icon for {app_name}: {e}")
    
    def launch_app(self, app_name):
        if app_name == "steam":
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(["start", "steam://"], shell=True)
                elif platform.system() == "Linux":
                    subprocess.Popen(["xdg-open", "steam://"])
            except Exception as e:
                print(f"Error launching Steam: {e}")
        elif app_name == "terminal":
            self.parent().add_terminal_tab("Terminal")
        elif app_name == "browser":
            self.parent().add_browser_tab("Browser")
        elif app_name == "telegram":
            self.parent().add_telegram_tab()

class HackerOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeonOS v4.0")
        self.setWindowIcon(QIcon("hacker_icon.png"))
        self.showFullScreen()
        
        # Initialize font
        self.init_font()
        
        # Color scheme
        self.bg_color = "#0a1922"
        self.text_color = "#64f5d2"
        self.accent_color = "#1e4a5f"
        self.highlight_color = "#00ffaa"
        self.error_color = "#ff5555"
        
        # Settings
        self.language = "en"
        self.app_shortcuts = []
        self.voice_assistant = None
        self.voice_active = False
        self.dock_visible = False
        
        # Web profile for all browser instances
        self.web_profile = QWebEngineProfile("NeonOS_Browser", self)
        self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        self.web_profile.setCachePath(os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "webcache"))
        self.web_profile.setPersistentStoragePath(os.path.join(QStandardPaths.writableLocation(QStandardPaths.DataLocation), "webstorage"))
        try:
            # Для старых версий Qt
            self.web_profile.setPasswordStorageEnabled(True)
        except AttributeError:
            # Для новых версий Qt
            self.web_profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
            self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
            self.web_profile.setCachePath(os.path.join(QStandardPaths.writableLocation(QStandardPaths.CacheLocation), "webcache"))
            self.web_profile.setPersistentStoragePath(os.path.join(QStandardPaths.writableLocation(QStandardPaths.DataLocation), "webstorage"))
                
        self.setStyle()
        self.initUI()
        self.initTimers()
        self.initAnimations()
        self.init_shortcuts()
        
        # System boot simulation
        self.simulate_boot()
    
    def init_font(self):
        # Try to load Hack font
        font_dir = os.path.dirname(os.path.abspath(__file__))
        hack_font_path = os.path.join(font_dir, "hack_font.ttf")
        
        if os.path.exists(hack_font_path):
            font_id = QFontDatabase.addApplicationFont(hack_font_path)
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                self.default_font = font_families[0]
            else:
                self.default_font = "Courier New"
        else:
            self.default_font = "Courier New"
    
    def setStyle(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.bg_color};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.accent_color};
                background: {self.bg_color};
                border-radius: 8px;
                margin: 2px;
            }}
            QTabBar::tab {{
                background: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px;
                margin-right: 2px;
                min-width: 100px;
                font-family: {self.default_font};
            }}
            QTabBar::tab:selected {{
                background: #143848;
                color: {self.highlight_color};
            }}
            QLineEdit {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                font-family: {self.default_font};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                padding: 8px;
                font-family: {self.default_font};
            }}
            QPushButton:hover {{
                background-color: #143848;
                border: 1px solid {self.highlight_color};
            }}
            QPushButton:pressed {{
                background-color: #1e4a5f;
            }}
            QListWidget {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                font-family: {self.default_font};
            }}
            QTreeView {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                font-family: {self.default_font};
            }}
            QTreeView::item:hover {{
                background-color: #143848;
            }}
            QTreeView::item:selected {{
                background-color: #1e4a5f;
            }}
            QFrame {{
                background-color: {self.bg_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {self.bg_color};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.accent_color};
                min-height: 20px;
                border-radius: 4px;
            }}
            QComboBox {{
                font-family: {self.default_font};
                color: {self.text_color};
                background-color: {self.bg_color};
                border: 1px solid {self.accent_color};
                border-radius: 5px;
                padding: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                selection-background-color: #1e4a5f;
            }}
        """)
    
    def initUI(self):
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left panel (system info)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(15)
        
        # Time and date
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"color: {self.highlight_color}; font-size: 16px; font-family: {self.default_font};")
        left_layout.addWidget(self.time_label)
        
        # Weather
        self.weather_label = QLabel("Loading weather...")
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setWordWrap(True)
        self.weather_label.setStyleSheet(f"font-family: {self.default_font}; color: {self.text_color};")
        left_layout.addWidget(self.weather_label)
        
        # Voice assistant
        self.voice_btn = QPushButton("Voice Assistant: OFF")
        self.voice_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1e4a5f;
                color: {self.error_color};
                font-weight: bold;
                border: 1px solid {self.error_color};
                border-radius: 8px;
                padding: 8px;
                font-family: {self.default_font};
            }}
        """)
        self.voice_btn.clicked.connect(self.toggle_voice_assistant)
        left_layout.addWidget(self.voice_btn)
        
        # System load graphs
        sys_info_frame = QFrame()
        sys_info_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        sys_info_layout = QVBoxLayout(sys_info_frame)
        sys_info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.cpu_label = QLabel("CPU: 0%")
        self.gpu_label = QLabel("GPU: N/A")
        self.memory_label = QLabel("RAM: 0%")
        
        for label in [self.cpu_label, self.gpu_label, self.memory_label]:
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(f"font-family: {self.default_font}; color: {self.text_color};")
            sys_info_layout.addWidget(label)
        
        left_layout.addWidget(sys_info_frame)
        left_layout.addStretch()
        
        # Central area with terminals and browser
        center_panel = QFrame()
        center_panel.setFrameShape(QFrame.StyledPanel)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        
        # Tabs with terminals and browser
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Button for adding new tabs
        add_tab_btn = QPushButton("+")
        add_tab_btn.setFixedSize(30, 30)
        add_tab_btn.clicked.connect(self.show_new_tab_menu)
        add_tab_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #143848;
            }}
        """)
        self.tab_widget.setCornerWidget(add_tab_btn, Qt.TopRightCorner)
        
        # Default tabs
        self.add_terminal_tab("CMD")
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command or press F1 for command list...")
        self.command_input.returnPressed.connect(self.execute_command)
        
        center_layout.addWidget(self.tab_widget)
        center_layout.addWidget(self.command_input)
        
        # Right panel (network info and Telegram)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setMaximumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Telegram chat
        self.telegram_chat = TelegramChat(self.web_profile)
        right_layout.addWidget(self.telegram_chat)
        
        # Network info
        net_info_frame = QFrame()
        net_info_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        net_info_layout = QVBoxLayout(net_info_frame)
        net_info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.ip_label = QLabel("IP: N/A")
        self.ping_label = QLabel("Ping: N/A")
        self.speed_label = QLabel("Speed: N/A")
        self.network_status = QLabel("Status: ONLINE")
        
        for label in [self.ip_label, self.ping_label, self.speed_label, self.network_status]:
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(f"font-family: {self.default_font}; color: {self.text_color};")
            net_info_layout.addWidget(label)
        
        right_layout.addWidget(net_info_frame)
        
        # Anonymity button
        self.anon_button = QPushButton("Activate ANONYMITY mode")
        self.anon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #143848;
                color: {self.highlight_color};
                font-weight: bold;
                border: 1px solid {self.highlight_color};
                border-radius: 8px;
                padding: 12px;
                font-family: {self.default_font};
            }}
            QPushButton:hover {{
                background-color: #1e4a5f;
            }}
        """)
        self.anon_button.clicked.connect(self.toggle_anonymity)
        right_layout.addWidget(self.anon_button)
        
        self.anonymity_status = QLabel("Mode: DISABLED")
        self.anonymity_status.setAlignment(Qt.AlignCenter)
        self.anonymity_status.setStyleSheet(f"font-family: {self.default_font}; color: {self.text_color};")
        right_layout.addWidget(self.anonymity_status)
        
        right_layout.addStretch()
        
        # Bottom panel (file explorer and dock)
        bottom_panel = QFrame()
        bottom_panel.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        
        # File explorer (1/3 width)
        explorer_frame = QFrame()
        explorer_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        explorer_layout = QVBoxLayout(explorer_frame)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_explorer = QTreeView()
        self.file_explorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_explorer.customContextMenuRequested.connect(self.show_file_context_menu)
        self.file_explorer.doubleClicked.connect(self.open_file)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.file_explorer.setModel(self.model)
        self.file_explorer.setRootIndex(self.model.index(QDir.rootPath()))
        self.file_explorer.setColumnWidth(0, 250)
        self.file_explorer.setHeaderHidden(True)
        
        explorer_scroll = QScrollArea()
        explorer_scroll.setWidget(self.file_explorer)
        explorer_scroll.setWidgetResizable(True)
        
        explorer_layout.addWidget(explorer_scroll)
        
        # Dock area (2/3 width)
        dock_frame = QFrame()
        dock_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        dock_layout = QVBoxLayout(dock_frame)
        dock_layout.setContentsMargins(0, 0, 0, 0)
        
        # Dock view (hidden by default)
        self.dock_view = DockView(self)
        self.dock_view.setFixedHeight(100)
        self.dock_view.hide()
        
        dock_layout.addWidget(self.dock_view)
        
        # Add to bottom panel
        bottom_layout.addWidget(explorer_frame, stretch=1)
        bottom_layout.addWidget(dock_frame, stretch=2)
        
        # Main layout
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(5)
        main_splitter.setStyleSheet("""
            QSplitter::handle {{
                background: #1e4a5f;
            }}
        """)
        
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(5)
        top_splitter.setStyleSheet("""
            QSplitter::handle {{
                background: #1e4a5f;
            }}
        """)
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(center_panel)
        top_splitter.addWidget(right_panel)
        
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_panel)
        
        main_layout.addWidget(main_splitter)
        
        # Set sizes
        main_splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        top_splitter.setSizes([200, 800, 350])
        
        # Dock activation area
        self.dock_activation_area = QLabel(self)
        self.dock_activation_area.setGeometry(0, self.height() - 20, self.width(), 20)
        self.dock_activation_area.setStyleSheet("background: transparent;")
        self.dock_activation_area.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if obj == self.dock_activation_area:
            if event.type() == event.Enter:
                self.show_dock()
            elif event.type() == event.Leave:
                self.hide_dock()
        return super().eventFilter(obj, event)
    
    def show_dock(self):
        if not self.dock_visible:
            self.dock_visible = True
            self.dock_view.show()
            self.dock_animation = QPropertyAnimation(self.dock_view, b"pos")
            self.dock_animation.setDuration(300)
            self.dock_animation.setStartValue(QPoint(0, self.height()))
            self.dock_animation.setEndValue(QPoint(0, self.height() - 100))
            self.dock_animation.setEasingCurve(QEasingCurve.OutQuad)
            self.dock_animation.start()
    
    def hide_dock(self):
        if self.dock_visible:
            self.dock_visible = False
            self.dock_animation = QPropertyAnimation(self.dock_view, b"pos")
            self.dock_animation.setDuration(300)
            self.dock_animation.setStartValue(QPoint(0, self.height() - 100))
            self.dock_animation.setEndValue(QPoint(0, self.height()))
            self.dock_animation.setEasingCurve(QEasingCurve.InQuad)
            self.dock_animation.finished.connect(self.dock_view.hide)
            self.dock_animation.start()
    
    def initTimers(self):
        """Initialize timers for updating information"""
        # Timer for updating time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # Timer for updating system info
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(2000)
        
        # Timer for updating network info
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.start(3000)
        
        # Timer for updating weather
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(1800000)  # 30 minutes
        
        # Update data immediately
        self.update_time()
        self.update_system_info()
        self.update_network_info()
        self.update_weather()
    
    def initAnimations(self):
        """Initialize animations"""
        # Cursor blinking animation
        self.cursor_visible = True
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)
    
    def init_shortcuts(self):
        """Initialize hotkeys"""
        # Hotkeys
        self.shortcut_new_terminal = QAction(self)
        self.shortcut_new_terminal.setShortcut(QKeySequence("Ctrl+T"))
        self.shortcut_new_terminal.triggered.connect(lambda: self.add_terminal_tab("Terminal"))
        self.addAction(self.shortcut_new_terminal)
        
        self.shortcut_new_browser = QAction(self)
        self.shortcut_new_browser.setShortcut(QKeySequence("Ctrl+B"))
        self.shortcut_new_browser.triggered.connect(lambda: self.add_browser_tab("Browser"))
        self.addAction(self.shortcut_new_browser)
        
        self.shortcut_help = QAction(self)
        self.shortcut_help.setShortcut(QKeySequence("F1"))
        self.shortcut_help.triggered.connect(self.show_help)
        self.addAction(self.shortcut_help)
        
        self.shortcut_voice = QAction(self)
        self.shortcut_voice.setShortcut(QKeySequence("Ctrl+V"))
        self.shortcut_voice.triggered.connect(self.toggle_voice_assistant)
        self.addAction(self.shortcut_voice)
    
    def show_new_tab_menu(self):
        menu = QMenu(self)
        
        terminal_action = QAction("New Terminal", self)
        terminal_action.triggered.connect(lambda: self.add_terminal_tab("Terminal"))
        
        browser_action = QAction("New Browser", self)
        browser_action.triggered.connect(lambda: self.add_browser_tab("Browser"))
        
        telegram_action = QAction("New Telegram", self)
        telegram_action.triggered.connect(self.add_telegram_tab)
        
        menu.addAction(terminal_action)
        menu.addAction(browser_action)
        menu.addAction(telegram_action)
        
        menu.exec_(QCursor.pos())
    
    def add_terminal_tab(self, name):
        terminal = HackerTerminal()
        tab_index = self.tab_widget.addTab(terminal, name)
        self.tab_widget.setCurrentIndex(tab_index)
        return terminal
    
    def add_browser_tab(self, name):
        browser = BrowserTab(self.web_profile)
        tab_index = self.tab_widget.addTab(browser, name)
        self.tab_widget.setCurrentIndex(tab_index)
        return browser
    
    def add_telegram_tab(self):
        telegram = TelegramChat(self.web_profile)
        tab_index = self.tab_widget.addTab(telegram, "Telegram")
        self.tab_widget.setCurrentIndex(tab_index)
        return telegram
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
    
    def show_file_context_menu(self, position):
        index = self.file_explorer.indexAt(position)
        if not index.isValid():
            return
        
        file_path = self.model.filePath(index)
        
        menu = QMenu()
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.open_file(index))
        menu.addAction(open_action)
        
        open_with_vscode = QAction("Open in VSCode", self)
        open_with_vscode.triggered.connect(lambda: self.open_in_vscode(file_path))
        menu.addAction(open_with_vscode)
        
        copy_path_action = QAction("Copy path", self)
        copy_path_action.triggered.connect(lambda: self.copy_file_path(file_path))
        menu.addAction(copy_path_action)
        
        run_as_admin_action = QAction("Run as administrator", self)
        run_as_admin_action.triggered.connect(lambda: self.run_as_admin(file_path))
        menu.addAction(run_as_admin_action)
        
        menu.exec_(self.file_explorer.viewport().mapToGlobal(position))
    
    def open_file(self, index):
        if not index.isValid():
            return
            
        file_path = self.model.filePath(index)
        
        if os.path.isfile(file_path):
            try:
                if file_path.endswith(('.txt', '.py', '.js', '.html', '.css', '.json', '.xml')):
                    # Open in new terminal tab for editing
                    terminal = self.add_terminal_tab(os.path.basename(file_path))
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    terminal.setPlainText(content)
                else:
                    # Open file with default method
                    os.startfile(file_path)
            except Exception as e:
                self.show_error_message(f"Error opening file: {str(e)}")
    
    def open_in_vscode(self, path):
        try:
            subprocess.Popen(["code", path])
        except Exception as e:
            self.show_error_message(f"Error opening in VSCode: {str(e)}")
    
    def copy_file_path(self, path):
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
    
    def run_as_admin(self, path):
        try:
            if platform.system() == "Windows":
                params = f'"/k cd /d {os.path.dirname(path)} & start "" "{path}"'
                subprocess.Popen(f'cmd.exe {params}', shell=True)
        except Exception as e:
            self.show_error_message(f"Error running: {str(e)}")
    
    def toggle_voice_assistant(self):
        self.voice_active = not self.voice_active
        
        if self.voice_active:
            self.voice_btn.setText("Voice Assistant: ON")
            self.voice_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e4a5f;
                    color: {self.highlight_color};
                    font-weight: bold;
                    border: 1px solid {self.highlight_color};
                    border-radius: 8px;
                    padding: 8px;
                    font-family: {self.default_font};
                }}
            """)
            
            if not self.voice_assistant:
                self.voice_assistant = VoiceAssistant(self.process_voice_command)
                self.voice_assistant.start()
        else:
            self.voice_btn.setText("Voice Assistant: OFF")
            self.voice_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e4a5f;
                    color: {self.error_color};
                    font-weight: bold;
                    border: 1px solid {self.error_color};
                    border-radius: 8px;
                    padding: 8px;
                    font-family: {self.default_font};
                }}
            """)
            
            if self.voice_assistant:
                self.voice_assistant.stop()
                self.voice_assistant = None
    
    def process_voice_command(self, text):
        current_tab = self.tab_widget.currentWidget()
        
        if isinstance(current_tab, HackerTerminal):
            current_tab.append(f"Voice command: {text}")
            
            # Command processing
            if "open browser" in text.lower():
                self.add_browser_tab("Browser")
            elif "new terminal" in text.lower():
                self.add_terminal_tab("Terminal")
            elif "close tab" in text.lower():
                self.close_tab(self.tab_widget.currentIndex())
            elif "exit" in text.lower():
                self.close()
            elif "execute command" in text.lower():
                cmd = text.replace("execute command", "").strip()
                self.command_input.setText(cmd)
                self.execute_command()
        else:
            current_tab.web_view.page().runJavaScript(f"console.log('Voice command: {text}')")
    
    def show_help(self):
        terminal = self.tab_widget.currentWidget()
        
        if isinstance(terminal, HackerTerminal):
            terminal.append("Available commands:")
            terminal.append("help - show this help")
            terminal.append("clear - clear screen")
            terminal.append("scan - scan network")
            terminal.append("hack - start hacking process")
            terminal.append("exit - exit")
            terminal.append("newtab - create new tab")
            terminal.append("ipconfig - show network settings")
            terminal.append("dir - show directory contents")
            terminal.append("ping [host] - check host availability")
            terminal.append("weather - update weather data")
            terminal.append("Hotkeys:")
            terminal.append("Ctrl+T - New Terminal")
            terminal.append("Ctrl+B - New Browser")
            terminal.append("Ctrl+V - Voice Assistant")
            terminal.append("F1 - Help")
    
    def execute_command(self):
        command = self.command_input.text()
        self.command_input.clear()
        
        terminal = self.tab_widget.currentWidget()
        
        if isinstance(terminal, HackerTerminal):
            terminal.append(f"> {command}")
            
            # Real commands
            if command.lower() in ["help", "помощь"]:
                self.show_help()
            elif command.lower() in ["clear", "очистить"]:
                terminal.clear()
            elif command.lower() in ["scan", "сканировать"]:
                terminal.append("Scanning network...")
                terminal.append("Found 5 devices:")
                terminal.append("192.168.1.1 - Router")
                terminal.append("192.168.1.2 - Computer")
                terminal.append("192.168.1.3 - Smartphone")
                terminal.append("192.168.1.4 - Printer")
                terminal.append("192.168.1.5 - Smart TV")
            elif command.lower() in ["hack", "взлом"]:
                self.simulate_hacking(terminal)
            elif command.lower() in ["exit", "выход"]:
                terminal.append("Exiting system...")
                QTimer.singleShot(1000, self.close)
            elif command.lower() in ["newtab", "новая вкладка"]:
                self.add_terminal_tab("Terminal")
            elif command.lower().startswith("ping "):
                host = command[5:].strip()
                terminal.append(f"Pinging {host}...")
                try:
                    result = subprocess.run(["ping", "-n", "1", host], capture_output=True, text=True)
                    terminal.append(result.stdout)
                except Exception as e:
                    terminal.append(f"Error: {str(e)}")
            elif command.lower() == "ipconfig":
                try:
                    result = subprocess.run(["ipconfig"], capture_output=True, text=True)
                    terminal.append(result.stdout)
                except Exception as e:
                    terminal.append(f"Error: {str(e)}")
            elif command.lower() == "dir":
                try:
                    result = subprocess.run(["dir"], shell=True, capture_output=True, text=True)
                    terminal.append(result.stdout)
                except Exception as e:
                    terminal.append(f"Error: {str(e)}")
            elif command.lower() == "weather":
                self.update_weather()
                terminal.append("Updating weather data...")
            else:
                # Try to execute command in real system
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    if result.stdout:
                        terminal.append(result.stdout)
                    if result.stderr:
                        terminal.append(result.stderr)
                except Exception as e:
                    terminal.append(f"'{command}' is not recognized as an internal or external command\nError: {str(e)}")
    
    def simulate_hacking(self, terminal):
        terminal.append("Initializing hack...")
        
        steps = [
            ("Finding vulnerabilities...", 2),
            ("Bypassing protection...", 3),
            ("Injecting exploit...", 4),
            ("Gaining access...", 3),
            ("Installing backdoor...", 2),
            ("Cleaning logs...", 3),
            ("Hack completed successfully!", 1)
        ]
        
        for step, duration in steps:
            QTimer.singleShot(sum(s[1] for s in steps[:steps.index((step, duration))]) * 1000, 
                            lambda s=step: terminal.append(s))
    
    def toggle_anonymity(self):
        if self.anonymity_status.text() == "Mode: DISABLED":
            self.anonymity_status.setText("Mode: ACTIVE")
            self.anonymity_status.setStyleSheet(f"color: {self.highlight_color}; font-weight: bold; font-family: {self.default_font};")
            self.network_status.setText("Status: ANONYMOUS")
            self.network_status.setStyleSheet(f"color: {self.highlight_color}; font-weight: bold; font-family: {self.default_font};")
            
            # Simulate VPN and Tor activation
            try:
                vpn_path = "C:\\Program Files\\SoftEther VPN Client\\vpncmgr_x64.exe"
                if os.path.exists(vpn_path):
                    subprocess.Popen([vpn_path])
                
                # Simulate time change to Japan
                self.time_timer.timeout.disconnect(self.update_time)
                self.time_timer.timeout.connect(self.update_japan_time)
                
                current_terminal = self.tab_widget.currentWidget()
                if isinstance(current_terminal, HackerTerminal):
                    current_terminal.append("[SYSTEM] Anonymous mode activated")
                    current_terminal.append("[SYSTEM] VPN connected")
                    current_terminal.append("[SYSTEM] Time switched to Japan timezone")
            except Exception as e:
                current_terminal = self.tab_widget.currentWidget()
                if isinstance(current_terminal, HackerTerminal):
                    current_terminal.append(f"[ERROR] Error activating anonymous mode: {str(e)}")
        else:
            self.anonymity_status.setText("Mode: DISABLED")
            self.anonymity_status.setStyleSheet(f"color: {self.text_color}; font-family: {self.default_font};")
            self.network_status.setText("Status: ONLINE")
            self.network_status.setStyleSheet(f"color: {self.highlight_color}; font-family: {self.default_font};")
            
            # Simulate VPN deactivation and time reset
            self.time_timer.timeout.disconnect(self.update_japan_time)
            self.time_timer.timeout.connect(self.update_time)
            
            current_terminal = self.tab_widget.currentWidget()
            if isinstance(current_terminal, HackerTerminal):
                current_terminal.append("[SYSTEM] Anonymous mode deactivated")
                current_terminal.append("[SYSTEM] VPN disconnected")
                current_terminal.append("[SYSTEM] Time restored")
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d.%m.%Y")
        self.time_label.setText(f"{current_time}\n{current_date}")
    
    def update_japan_time(self):
        # Japan UTC+9
        japan_time = datetime.utcnow() + timedelta(hours=9)
        current_time = japan_time.strftime("%H:%M:%S")
        current_date = japan_time.strftime("%d.%m.%Y")
        self.time_label.setText(f"{current_time}\n{current_date}\n(Japan)")
    
    def update_system_info(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        
        # GPU (simplified implementation)
        try:
            gpu_info = subprocess.check_output("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits", shell=True)
            gpu_percent = gpu_info.decode().strip()
            self.gpu_label.setText(f"GPU: {gpu_percent}%")
        except:
            self.gpu_label.setText("GPU: N/A")
        
        # Memory
        memory = psutil.virtual_memory()
        self.memory_label.setText(f"RAM: {memory.percent}%")
    
    def update_network_info(self):
        # IP address
        try:
            ip = requests.get('https://ident.me', timeout=5).text.strip()
            self.ip_label.setText(f"IP: {ip}")
        except:
            self.ip_label.setText("IP: N/A")
        
        # Ping (simplified implementation)
        try:
            ping = subprocess.check_output("ping -n 1 8.8.8.8 | find \"Average =\"", shell=True)
            ping = ping.decode('cp866').split('=')[-1].strip()
            self.ping_label.setText(f"Ping: {ping}")
        except:
            self.ping_label.setText("Ping: N/A")
        
        # Network speed (simplified implementation)
        net_io = psutil.net_io_counters()
        self.speed_label.setText(f"Speed: ↑{net_io.bytes_sent//1024}K ↓{net_io.bytes_recv//1024}K")
    
    def update_weather(self):
        """Обновление информации о погоде"""
        try:
            weather = get_weather()
            if weather:
                self.weather_label.setText(
                    f"{weather['city']}\n"
                    f"Температура: {weather['temp']}\n"
                    f"{weather['weather'].capitalize()}"
                )
            else:
                self.weather_label.setText("Данные о погоде недоступны")
        except Exception as e:
            print(f"Ошибка обновления погоды: {e}")
            self.weather_label.setText("Ошибка загрузки погоды")
    
    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        if self.cursor_visible:
            self.command_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.bg_color};
                    color: {self.text_color};
                    border: 1px solid {self.accent_color};
                    border-radius: 8px;
                    font-family: {self.default_font};
                    font-size: 14px;
                    padding: 10px;
                }}
            """)
        else:
            self.command_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.bg_color};
                    color: #64f5d2;
                    border: 1px solid #64f5d2;
                    border-radius: 8px;
                    font-family: {self.default_font};
                    font-size: 14px;
                    padding: 10px;
                }}
            """)
    
    def simulate_boot(self):
        self.boot_terminal = self.add_terminal_tab("System Boot")
        self.boot_terminal.append("Initializing NeonOS v4.0...")
        
        boot_messages = [
            ("Loading kernel modules...", 500),
            ("Mounting filesystems...", 700),
            ("Starting network services...", 600),
            ("Initializing security protocols...", 800),
            ("Starting system daemons...", 500),
            ("Loading user interface...", 900),
            ("System ready.", 1000)
        ]
        
        total_delay = 0
        for msg, delay in boot_messages:
            total_delay += delay
            QTimer.singleShot(total_delay, lambda m=msg: self.boot_terminal.append(m))
        
        QTimer.singleShot(total_delay + 500, lambda: self.tab_widget.setCurrentIndex(1))
    
    def show_error_message(self, message):
        error_label = QLabel(message)
        error_label.setStyleSheet(f"color: {self.error_color}; font-family: {self.default_font};")
        error_label.setWindowTitle("Error")
        error_label.show()
    
    def closeEvent(self, event):
        # Clean up cookies and cache
        if hasattr(self, 'web_profile'):
            self.web_profile.cookieStore().deleteAllCookies()
            self.web_profile.clearHttpCache()
        
        # Stop voice assistant
        if self.voice_assistant:
            self.voice_assistant.stop()
        
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set style
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 25, 34))
    palette.setColor(QPalette.WindowText, QColor(100, 255, 210))
    palette.setColor(QPalette.Base, QColor(10, 25, 34))
    palette.setColor(QPalette.AlternateBase, QColor(20, 56, 72))
    palette.setColor(QPalette.ToolTipBase, QColor(100, 255, 210))
    palette.setColor(QPalette.ToolTipText, QColor(100, 255, 210))
    palette.setColor(QPalette.Text, QColor(100, 255, 210))
    palette.setColor(QPalette.Button, QColor(10, 25, 34))
    palette.setColor(QPalette.ButtonText, QColor(100, 255, 210))
    palette.setColor(QPalette.BrightText, QColor(255, 85, 85))
    palette.setColor(QPalette.Highlight, QColor(30, 74, 95))
    palette.setColor(QPalette.HighlightedText, QColor(100, 255, 210))
    app.setPalette(palette)
    
    window = HackerOS()
    
    # Fade in animation
    window.setWindowOpacity(0)
    window.show()
    
    fade_in = QPropertyAnimation(window, b"windowOpacity")
    fade_in.setDuration(1500)
    fade_in.setStartValue(0)
    fade_in.setEndValue(1)
    fade_in.setEasingCurve(QEasingCurve.InOutQuad)
    fade_in.start()
    
    sys.exit(app.exec_())
