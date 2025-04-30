import sys
import os
import subprocess
import platform
import psutil
import time
from datetime import datetime, timedelta
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QLineEdit, QLabel, QTabWidget, QPushButton, 
                             QListWidget, QFileSystemModel, QTreeView, QSplitter, 
                             QGraphicsOpacityEffect, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QDir, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QTextCursor, QIcon, QFontDatabase

class HackerTerminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeonOS v2.0")
        self.setWindowIcon(QIcon("hacker_icon.png"))
        self.showFullScreen()
        
        # Загрузка шрифта Hack
        font_dir = os.path.dirname(os.path.abspath(__file__))
        hack_font_path = os.path.join(font_dir, "hack_font.ttf")
        
        if os.path.exists(hack_font_path):
            QFontDatabase.addApplicationFont(hack_font_path)
            self.default_font = "Hack"
        else:
            self.default_font = "Courier New"  # Запасной шрифт
        
    def append(self, text):
        self.moveCursor(QTextCursor.End)
        self.insertPlainText(text + "\n")
        self.moveCursor(QTextCursor.End)

class HackerOS(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NeonOS v2.0")
        self.setWindowIcon(QIcon("hacker_icon.png"))
        self.showFullScreen()
        
        # Загрузка шрифта Hack
        font_dir = os.path.dirname(os.path.abspath(__file__))
        hack_font_path = os.path.join(font_dir, "hack_font.ttf")
        
        if os.path.exists(hack_font_path):
            QFontDatabase.addApplicationFont(hack_font_path)
            self.default_font = "Hack"
        else:
            self.default_font = "Courier New"
        
        self.bg_color = "#0a1922"
        self.text_color = "#64f5d2"
        self.accent_color = "#1e4a5f"
        self.highlight_color = "#00ffaa"
        
        self.setStyle()
        self.initUI()
        self.initTimers()
        self.initAnimations()
        
        self.simulate_boot()

    def simulate_boot(self):
        self.boot_terminal = self.add_terminal_tab("System Boot")
        self.boot_terminal.append("Initializing NeonOS v2.0...")
        
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
        
    def setStyle(self):
        self.setStyleSheet(f"""
            QTextEdit {{
                font-family: {self.default_font}, Consolas, 'Courier New', monospace;
            }}
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
                font-family: 'Fira Code', Consolas, monospace;
                font-size: 12px;
                padding: 8px;
            }}
            QPushButton {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                padding: 8px;
                font-family: 'Fira Code', Consolas, monospace;
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
                font-family: 'Fira Code', Consolas, monospace;
            }}
            QTreeView {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: 1px solid {self.accent_color};
                border-radius: 8px;
                font-family: 'Fira Code', Consolas, monospace;
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
        """)
        
    def initUI(self):
        # Главный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Левая панель (системная информация)
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setMaximumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(15)
        
        # Время и дата
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(f"color: {self.highlight_color}; font-size: 16px; font-family: 'Fira Code';")
        left_layout.addWidget(self.time_label)
        
        # Погода
        self.weather_label = QLabel("Загрузка погоды...")
        self.weather_label.setAlignment(Qt.AlignCenter)
        self.weather_label.setWordWrap(True)
        self.weather_label.setStyleSheet(f"font-family: 'Fira Code'; color: {self.text_color};")
        left_layout.addWidget(self.weather_label)
        
        # Графики загрузки системы
        sys_info_frame = QFrame()
        sys_info_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        sys_info_layout = QVBoxLayout(sys_info_frame)
        sys_info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.cpu_label = QLabel("CPU: 0%")
        self.gpu_label = QLabel("GPU: N/A")
        self.memory_label = QLabel("RAM: 0%")
        
        for label in [self.cpu_label, self.gpu_label, self.memory_label]:
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(f"font-family: 'Fira Code'; color: {self.text_color};")
            sys_info_layout.addWidget(label)
        
        left_layout.addWidget(sys_info_frame)
        left_layout.addStretch()
        
        # Центральная область с терминалами
        center_panel = QFrame()
        center_panel.setFrameShape(QFrame.StyledPanel)
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        
        # Вкладки с терминалами
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Кнопка добавления новой вкладки
        self.tab_widget.setCornerWidget(QPushButton("+", self.tab_widget), Qt.TopRightCorner)
        self.tab_widget.cornerWidget().clicked.connect(self.add_new_tab)
        self.tab_widget.cornerWidget().setFixedSize(30, 30)
        self.tab_widget.cornerWidget().setStyleSheet(f"""
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
        
        # CMD вкладка
        self.add_terminal_tab("CMD")
        
        # Поле ввода команд
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Введите команду...")
        self.command_input.returnPressed.connect(self.execute_command)
        
        center_layout.addWidget(self.tab_widget)
        center_layout.addWidget(self.command_input)
        
        # Правая панель (сетевая информация)
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_panel.setMaximumWidth(250)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Статус сети
        self.network_status = QLabel("Статус: ONLINE")
        self.network_status.setAlignment(Qt.AlignCenter)
        self.network_status.setStyleSheet(f"color: {self.highlight_color}; font-size: 16px; font-family: 'Fira Code';")
        right_layout.addWidget(self.network_status)
        
        # Сетевая информация
        net_info_frame = QFrame()
        net_info_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        net_info_layout = QVBoxLayout(net_info_frame)
        net_info_layout.setContentsMargins(10, 10, 10, 10)
        
        self.ping_label = QLabel("Пинг: N/A")
        self.speed_label = QLabel("Скорость: N/A")
        
        for label in [self.ping_label, self.speed_label]:
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(f"font-family: 'Fira Code'; color: {self.text_color};")
            net_info_layout.addWidget(label)
        
        right_layout.addWidget(net_info_frame)
        
        # Кнопка анонимности
        self.anon_button = QPushButton("Активировать режим АНОНИМ")
        self.anon_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #143848;
                color: {self.highlight_color};
                font-weight: bold;
                border: 1px solid {self.highlight_color};
                border-radius: 8px;
                padding: 12px;
                font-family: 'Fira Code';
            }}
            QPushButton:hover {{
                background-color: #1e4a5f;
            }}
        """)
        self.anon_button.clicked.connect(self.toggle_anonymity)
        right_layout.addWidget(self.anon_button)
        
        self.anonymity_status = QLabel("Режим: ОТКЛЮЧЕН")
        self.anonymity_status.setAlignment(Qt.AlignCenter)
        self.anonymity_status.setStyleSheet(f"font-family: 'Fira Code'; color: {self.text_color};")
        right_layout.addWidget(self.anonymity_status)
        
        right_layout.addStretch()
        
        # Нижняя панель
        bottom_panel = QFrame()
        bottom_panel.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(10)
        
        # Проводник (слева)
        explorer_frame = QFrame()
        explorer_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        explorer_layout = QVBoxLayout(explorer_frame)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        
        self.file_explorer = QTreeView()
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
        bottom_layout.addWidget(explorer_frame, 3)
        
        # Быстрый доступ (справа)
        quick_access_frame = QFrame()
        quick_access_frame.setStyleSheet(f"border: 1px solid {self.accent_color}; border-radius: 8px;")
        quick_access_layout = QVBoxLayout(quick_access_frame)
        quick_access_layout.setContentsMargins(10, 10, 10, 10)
        
        self.keyboard_display = QLabel("Ввод: ")
        self.keyboard_display.setStyleSheet(f"font-family: 'Fira Code'; color: {self.text_color}; font-size: 14px;")
        quick_access_layout.addWidget(self.keyboard_display)
        
        quick_buttons_layout = QHBoxLayout()
        
        apps = ["Браузер", "Терминал", "Редактор", "Настройки"]
        for app in apps:
            btn = QPushButton(app)
            btn.setFixedSize(80, 60)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: 'Fira Code';
                    border-radius: 8px;
                }}
            """)
            quick_buttons_layout.addWidget(btn)
        
        quick_access_layout.addLayout(quick_buttons_layout)
        bottom_layout.addWidget(quick_access_frame, 1)
        
        # Основная компоновка
        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.setHandleWidth(5)
        main_splitter.setStyleSheet("""
            QSplitter::handle {
                background: #1e4a5f;
            }
        """)
        
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(5)
        top_splitter.setStyleSheet("""
            QSplitter::handle {
                background: #1e4a5f;
            }
        """)
        
        top_splitter.addWidget(left_panel)
        top_splitter.addWidget(center_panel)
        top_splitter.addWidget(right_panel)
        
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(bottom_panel)
        
        main_layout.addWidget(main_splitter)
        
        # Установка размеров
        main_splitter.setSizes([int(self.height() * 0.7), int(self.height() * 0.3)])
        top_splitter.setSizes([200, 800, 200])
        
    def add_terminal_tab(self, name):
        terminal = HackerTerminal()
        tab_index = self.tab_widget.addTab(terminal, name)
        self.tab_widget.setCurrentIndex(tab_index)
        return terminal
        
    def add_new_tab(self):
        tab_count = self.tab_widget.count()
        new_tab_name = f"Terminal-{tab_count + 1}"
        self.add_terminal_tab(new_tab_name)
        
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        
    def initTimers(self):
        # Таймер для обновления времени
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # Таймер для обновления системной информации
        self.system_timer = QTimer()
        self.system_timer.timeout.connect(self.update_system_info)
        self.system_timer.start(2000)
        
        # Таймер для обновления сетевой информации
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.update_network_info)
        self.network_timer.start(3000)
        
        # Таймер для обновления погоды
        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(1800000)  # 30 минут
        
        # Обновляем данные сразу
        self.update_time()
        self.update_system_info()
        self.update_network_info()
        self.update_weather()
        
    def initAnimations(self):
        # Анимация мигания курсора
        self.cursor_visible = True
        self.cursor_timer = QTimer()
        self.cursor_timer.timeout.connect(self.blink_cursor)
        self.cursor_timer.start(500)
        
        # Анимация ввода с клавиатуры
        self.command_input.textChanged.connect(self.update_keyboard_display)
        
    def simulate_boot(self):
        self.boot_terminal = self.add_terminal_tab("System Boot")
        self.boot_terminal.append("Initializing NeonOS v2.0...")
        
        boot_messages = [
            ("Loading kernel modules...", 0.5),
            ("Mounting filesystems...", 0.7),
            ("Starting network services...", 0.6),
            ("Initializing security protocols...", 0.8),
            ("Starting system daemons...", 0.5),
            ("Loading user interface...", 0.9),
            ("System ready.", 1.0)
        ]
        
        for msg, delay in boot_messages:
            QTimer.singleShot(int(sum(m[1] for m in boot_messages[:boot_messages.index((msg, delay))]) * 1000, 
                            lambda m=msg: self.boot_terminal.append(m)))
        
        QTimer.singleShot(int(sum(m[1] for m in boot_messages) * 1000 + 500, 
                         lambda: self.tab_widget.setCurrentIndex(1)))
        
    def blink_cursor(self):
        self.cursor_visible = not self.cursor_visible
        if self.cursor_visible:
            self.command_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.bg_color};
                    color: {self.text_color};
                    border: 1px solid {self.accent_color};
                    border-radius: 8px;
                    font-family: 'Fira Code', Consolas, monospace;
                    font-size: 12px;
                    padding: 8px;
                }}
            """)
        else:
            self.command_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {self.bg_color};
                    color: #64f5d2;
                    border: 1px solid #64f5d2;
                    border-radius: 8px;
                    font-family: 'Fira Code', Consolas, monospace;
                    font-size: 12px;
                    padding: 8px;
                }}
            """)
    
    def update_keyboard_display(self):
        text = self.command_input.text()
        self.keyboard_display.setText(f"Ввод: {text}")
        
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d.%m.%Y")
        self.time_label.setText(f"{current_time}\n{current_date}")
        
    def update_japan_time(self):
        # Япония UTC+9
        japan_time = datetime.utcnow() + timedelta(hours=9)
        current_time = japan_time.strftime("%H:%M:%S")
        current_date = japan_time.strftime("%d.%m.%Y")
        self.time_label.setText(f"{current_time}\n{current_date}\n(Япония)")
        
    def update_system_info(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        
        # GPU (упрощенная реализация)
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
        # Пинг (упрощенная реализация)
        try:
            ping = subprocess.check_output("ping -n 1 8.8.8.8 | find \"Среднее =\"", shell=True)
            ping = ping.decode('cp866').split('=')[-1].strip()
            self.ping_label.setText(f"Пинг: {ping}")
        except:
            self.ping_label.setText("Пинг: N/A")
        
        # Скорость сети (упрощенная реализация)
        net_io = psutil.net_io_counters()
        self.speed_label.setText(f"Скорость: ↑{net_io.bytes_sent//1024}K ↓{net_io.bytes_recv//1024}K")
        
    def update_weather(self):
        try:
            # Здесь должен быть парсинг погоды с сайта
            # Для примера используем mock данные
            weather_data = {
                "location": "Москва",
                "temp": "+15°C",
                "condition": "Облачно",
                "humidity": "75%"
            }
            self.weather_label.setText(
                f"{weather_data['location']}\n"
                f"Температура: {weather_data['temp']}\n"
                f"{weather_data['condition']}\n"
                f"Влажность: {weather_data['humidity']}"
            )
        except Exception as e:
            self.weather_label.setText("Ошибка загрузки погоды")
        
    def execute_command(self):
        command = self.command_input.text()
        self.command_input.clear()
        
        terminal = self.tab_widget.currentWidget()
        
        terminal.append(f"> {command}")
        
        # Имитация выполнения команд
        if command.lower() in ["help", "помощь"]:
            terminal.append("Доступные команды:")
            terminal.append("help - показать эту справку")
            terminal.append("clear - очистить экран")
            terminal.append("scan - сканировать сеть")
            terminal.append("hack - запустить процесс взлома")
            terminal.append("exit - выйти")
            terminal.append("newtab - создать новую вкладку")
        elif command.lower() in ["clear", "очистить"]:
            terminal.clear()
        elif command.lower() in ["scan", "сканировать"]:
            terminal.append("Сканирование сети...")
            terminal.append("Найдено 5 устройств:")
            terminal.append("192.168.1.1 - Роутер")
            terminal.append("192.168.1.2 - Компьютер")
            terminal.append("192.168.1.3 - Смартфон")
            terminal.append("192.168.1.4 - Принтер")
            terminal.append("192.168.1.5 - Умный телевизор")
        elif command.lower() in ["hack", "взлом"]:
            self.simulate_hacking(terminal)
        elif command.lower() in ["exit", "выход"]:
            terminal.append("Выход из системы...")
            QTimer.singleShot(1000, self.close)
        elif command.lower() in ["newtab", "новая вкладка"]:
            self.add_new_tab()
        else:
            terminal.append(f"'{command}' не является внутренней или внешней командой")
        
    def simulate_boot(self):
        self.boot_terminal = self.add_terminal_tab("System Boot")
        self.boot_terminal.append("Initializing NeonOS v2.0...")
        
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
    def toggle_anonymity(self):
        if self.anonymity_status.text() == "Режим: ОТКЛЮЧЕН":
            self.anonymity_status.setText("Режим: АКТИВЕН")
            self.anonymity_status.setStyleSheet(f"color: {self.highlight_color}; font-weight: bold; font-family: 'Fira Code';")
            self.network_status.setText("Статус: АНОНИМНЫЙ")
            self.network_status.setStyleSheet(f"color: {self.highlight_color}; font-weight: bold; font-family: 'Fira Code';")
            
            # Имитация запуска VPN и Tor
            try:
                # В реальном приложении здесь должен быть код для запуска VPN и Tor
                vpn_path = "C:\\Program Files\\SoftEther VPN Client\\vpncmgr_x64.exe"
                if os.path.exists(vpn_path):
                    subprocess.Popen([vpn_path])
                
                # Имитация смены времени на японское
                self.time_timer.timeout.disconnect(self.update_time)
                self.time_timer.timeout.connect(self.update_japan_time)
                
                current_terminal = self.tab_widget.currentWidget()
                current_terminal.append("[SYSTEM] Анонимный режим активирован")
                current_terminal.append("[SYSTEM] VPN подключен")
                current_terminal.append("[SYSTEM] Время переключено на японский часовой пояс")
            except Exception as e:
                current_terminal = self.tab_widget.currentWidget()
                current_terminal.append(f"[ERROR] Ошибка активации анонимного режима: {str(e)}")
        else:
            self.anonymity_status.setText("Режим: ОТКЛЮЧЕН")
            self.anonymity_status.setStyleSheet(f"color: {self.text_color}; font-family: 'Fira Code';")
            self.network_status.setText("Статус: ONLINE")
            self.network_status.setStyleSheet(f"color: {self.highlight_color}; font-family: 'Fira Code';")
            
            # Имитация отключения VPN и возврата времени
            self.time_timer.timeout.disconnect(self.update_japan_time)
            self.time_timer.timeout.connect(self.update_time)
            
            current_terminal = self.tab_widget.currentWidget()
            current_terminal.append("[SYSTEM] Анонимный режим деактивирован")
            current_terminal.append("[SYSTEM] VPN отключен")
            current_terminal.append("[SYSTEM] Время восстановлено")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка стиля
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 25, 34))
    palette.setColor(QPalette.WindowText, QColor(100, 245, 210))
    palette.setColor(QPalette.Base, QColor(10, 25, 34))
    palette.setColor(QPalette.AlternateBase, QColor(20, 56, 72))
    palette.setColor(QPalette.ToolTipBase, QColor(100, 245, 210))
    palette.setColor(QPalette.ToolTipText, QColor(100, 245, 210))
    palette.setColor(QPalette.Text, QColor(100, 245, 210))
    palette.setColor(QPalette.Button, QColor(10, 25, 34))
    palette.setColor(QPalette.ButtonText, QColor(100, 245, 210))
    palette.setColor(QPalette.BrightText, QColor(255, 85, 85))
    palette.setColor(QPalette.Highlight, QColor(30, 74, 95))
    palette.setColor(QPalette.HighlightedText, QColor(100, 245, 210))
    app.setPalette(palette)
    
    window = HackerOS()
    
    # Анимация появления
    window.setWindowOpacity(0)
    window.show()
    
    fade_in = QPropertyAnimation(window, b"windowOpacity")
    fade_in.setDuration(1500)
    fade_in.setStartValue(0)
    fade_in.setEndValue(1)
    fade_in.setEasingCurve(QEasingCurve.InOutQuad)
    fade_in.start()
    
    sys.exit(app.exec_())
