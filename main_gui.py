import sys
import time
import threading
import random
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QScrollArea, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QThread, pyqtSignal, QSize, QRectF
from PyQt6.QtGui import QColor, QPainter, QFont, QIcon, QLinearGradient, QRadialGradient, QPen, QBrush
import qtawesome as qta
from alfred_core import AlfredCore

class JarvisCore(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 220)
        self.angle1 = 0.0
        self.angle2 = 0.0
        self.angle3 = 0.0
        self.pulse = 0
        self.pulse_dir = 1
        self.loudness = 0
        self.is_active = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        
    def update_animation(self):
        self.angle1 += 1
        self.angle2 -= 1.5
        self.angle3 += 0.5
        
        self.pulse += 2 * self.pulse_dir
        if self.pulse >= 40 or self.pulse <= 0:
            self.pulse_dir *= -1
            
        if self.is_active:
            self.loudness = random.randint(30, 60)
        elif self.loudness > 0:
            self.loudness = max(0, self.loudness - 2)
             
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() // 2, self.height() // 2
        
        # Central Glow
        grad = QRadialGradient(cx, cy, 40 + self.pulse/4)
        grad.setColorAt(0, QColor(0, 210, 255, 180))
        grad.setColorAt(1, QColor(0, 210, 255, 0))
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx-50, cy-50, 100, 100)
        
        # Rotating Rings
        pen = QPen(QColor(0, 210, 255, 150))
        pen.setWidth(2)
        pen.setDashPattern([10, 20])
        painter.setPen(pen)
        
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle1)
        painter.drawEllipse(QRectF(-60, -60, 120, 120))
        painter.restore()
        
        pen.setDashPattern([5, 10])
        pen.setColor(QColor(58, 123, 213, 100))
        painter.setPen(pen)
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.angle2)
        painter.drawEllipse(QRectF(-75, -75, 150, 150))
        painter.restore()
        
        # Circular Waveform
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setColor(QColor(0, 210, 255, 200))
        pen.setWidth(2)
        painter.setPen(pen)
        
        num_bars = 40
        for i in range(num_bars):
            angle = (i / num_bars) * 360
            rad = math.radians(angle)
            h = 8 + (random.randint(5, 15) if self.loudness > 10 else 2)
            
            x1 = cx + math.cos(rad) * 85
            y1 = cy + math.sin(rad) * 85
            x2 = cx + math.cos(rad) * (85 + h)
            y2 = cy + math.sin(rad) * (85 + h)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
            
        # Core Center
        painter.setBrush(QColor(0, 210, 255))
        painter.drawEllipse(cx-15, cy-15, 30, 30)

class HUDElement(QFrame):
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 150);
                border: 1px solid rgba(0, 210, 255, 50);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout = QVBoxLayout(self)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #00d2ff; font-size: 8px; font-weight: bold; text-transform: uppercase;")
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet("color: white; font-size: 10px; font-family: 'Consolas';")
        layout.addWidget(title_lbl)
        layout.addWidget(self.val_lbl)

class ChatBubble(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 5, 10, 5)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 10))
        self.label.setContentsMargins(12, 8, 12, 8)
        
        if is_user:
            self.setStyleSheet("""
                background-color: rgba(78, 67, 118, 180);
                color: white;
                border-radius: 15px;
                border-top-right-radius: 2px;
            """)
            self.layout.addStretch()
            self.layout.addWidget(self.label)
        else:
            self.setStyleSheet("""
                background-color: rgba(36, 36, 36, 180);
                color: #00d2ff;
                border-radius: 15px;
                border-top-left-radius: 2px;
                border: 1px solid rgba(0, 210, 255, 100);
            """)
            self.layout.addWidget(self.label)
            self.layout.addStretch()

class AlfredWorker(QThread):
    command_received = pyqtSignal(str)
    response_ready = pyqtSignal(str)
    status_changed = pyqtSignal(str)
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.listening = False

    def run(self):
        while True:
            if self.listening:
                cmd = self.core.listen(self.status_changed.emit)
                if cmd:
                    self.command_received.emit(cmd)
                    is_running = self.core.process_command(cmd, self.response_ready.emit, self.status_changed.emit)
                    if not is_running:
                        self.listening = False
                        self.status_changed.emit("Offline")
                else:
                    self.status_changed.emit("Waiting...")
            time.sleep(0.1)

class AlfredGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = AlfredCore()
        self.worker = AlfredWorker(self.core)
        self.worker.command_received.connect(self.add_user_message)
        self.worker.response_ready.connect(self.add_assistant_message)
        self.worker.status_changed.connect(self.update_status)
        self.worker.start()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("ALFRED HUD")
        self.setFixedSize(400, 600)
        self.setStyleSheet("background-color: #080808;")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout(main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header - HUD Dash
        hud_header = QHBoxLayout()
        hud_header.addWidget(HUDElement("SYSTEM", "STABLE"))
        hud_header.addWidget(HUDElement("CPU", "12%"))
        hud_header.addStretch()
        hud_header.addWidget(HUDElement("CORE", "GEMINI-2"))
        self.main_layout.addLayout(hud_header)
        
        # Central Jarvis Core
        self.jarvis = JarvisCore()
        core_layout = QHBoxLayout()
        core_layout.addStretch()
        core_layout.addWidget(self.jarvis)
        core_layout.addStretch()
        self.main_layout.addLayout(core_layout)
        
        self.status_label = QLabel("SYSTEM IDLE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00d2ff; font-family: 'Segoe UI'; font-weight: bold; letter-spacing: 2px;")
        self.main_layout.addWidget(self.status_label)
        
        # Chat
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none; background: transparent;")
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.scroll.setWidget(self.chat_container)
        self.main_layout.addWidget(self.scroll)
        
        # Mic
        self.mic_btn = QPushButton()
        self.mic_btn.setFixedSize(80, 80)
        self.mic_btn.setIcon(qta.icon("fa5s.microphone", color="#00d2ff"))
        self.mic_btn.setIconSize(QSize(30, 30))
        self.mic_btn.setCheckable(True)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 100);
                border: 2px solid #00d2ff;
                border-radius: 40px;
            }
            QPushButton:checked {
                background-color: rgba(0, 210, 255, 50);
                border: 3px solid #00d2ff;
            }
            QPushButton:hover {
                border: 3px solid white;
            }
        """)
        self.mic_btn.clicked.connect(self.toggle_listening)
        
        mic_layout = QHBoxLayout()
        mic_layout.addStretch()
        mic_layout.addWidget(self.mic_btn)
        mic_layout.addStretch()
        self.main_layout.addLayout(mic_layout)
        
        # Scrollbar logic
        self.scroll.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical { width: 5px; background: transparent; }
            QScrollBar::handle:vertical { background: #00d2ff; border-radius: 2px; }
        """)

    def toggle_listening(self):
        self.worker.listening = self.mic_btn.isChecked()
        self.status_label.setText("LISTENING..." if self.worker.listening else "SYSTEM IDLE")
            
    def update_status(self, status):
        self.status_label.setText(status.upper())
        self.jarvis.is_active = (status == "Listening...")
        
    def add_user_message(self, text):
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, ChatBubble(text, True))
        self.scroll_to_bottom()
        
    def add_assistant_message(self, text):
        self.current_text = ""
        self.target_text = text
        self.bubble = ChatBubble("", False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.bubble)
        self.timer = QTimer()
        self.timer.timeout.connect(self.type_effect)
        self.timer.start(25)
        
    def type_effect(self):
        if len(self.current_text) < len(self.target_text):
            self.current_text += self.target_text[len(self.current_text)]
            self.bubble.label.setText(self.current_text)
            self.scroll_to_bottom()
        else:
            self.timer.stop()

    def scroll_to_bottom(self):
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlfredGUI()
    window.show()
    sys.exit(app.exec())
