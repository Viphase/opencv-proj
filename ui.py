from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFontDatabase, QFont, QImage
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from cv2 import COLOR_BGR2RGB, cvtColor
import sys

UI_EVENTS = {
    "start": False,
    "instruction_yes": False,
    "instruction_no": False,
    "continue": False
}

class GameMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cowboy-Shootout")

        self.menu_bg = "./ui/menu_background.png"
        self.game_bg = "./ui/game_background.png"

        with open("./ui/cowboy_font.ttf", "rb") as f:
            font_data = f.read()

        font_id = QFontDatabase.addApplicationFontFromData(font_data)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        title_font = QFont(font_family)
        title_font.setPointSize(120)
        title_font.setBold(True)

        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout(self.menu_widget)

        self.label = QLabel("COWBOY-SHOOTOUT")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(title_font)
        self.label.setStyleSheet("""
            QLabel {
                color: black;
                background: rgba(255,255,255,150);
                padding: 20px;
                border-radius: 20px;
            }
        """)

        self.play_btn = QPushButton("Играть")
        self.settings_btn = QPushButton("Правила")
        self.exit_btn = QPushButton("Выход")

        for b in (self.play_btn, self.settings_btn, self.exit_btn):
            b.setMinimumHeight(100)
            b.setFixedWidth(600)
            b.setStyleSheet("""
                QPushButton {
                    font-size: 48px;
                    color: white;
                    background: rgba(0,0,0,150);
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background: rgba(0,0,0,200);
                }
            """)

        menu_layout.addStretch()
        menu_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addSpacing(50)
        menu_layout.addWidget(self.play_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.settings_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addStretch()

        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)

        self.settings_text = QLabel(
            "Cowboy-Shootout — это дуэльная игра.\n\n"
            "• Два ковбоя должны стоять друг напротив друга\n"
            "• Пистолет правой рукой — выстрел\n"
            "• Кулак левой рукой — защита\n"
            "• Побеждает тот кто попадёт в тело!\n"
        )
        self.settings_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settings_text.setStyleSheet("""
            QLabel {
                font-size: 36px;
                color: black;
                background: rgba(255,255,255,180);
                padding: 40px;
                border-radius: 20px;
            }
        """)

        self.back_btn = QPushButton("Назад")
        self.back_btn.setFixedSize(400, 90)
        self.back_btn.setStyleSheet("""
            QPushButton {
                font-size: 40px;
                color: white;
                background: rgba(0,0,0,150);
                border-radius: 20px;
            }
            QPushButton:hover {
                background: rgba(0,0,0,200);
            }
        """)

        settings_layout.addStretch()
        settings_layout.addWidget(self.settings_text, alignment=Qt.AlignmentFlag.AlignCenter)
        settings_layout.addSpacing(40)
        settings_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        settings_layout.addStretch()

        self.settings_widget.hide()
        self.game_widget = QLabel("ИГРА ЗАПУЩЕНА")
        self.game_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_widget.setStyleSheet("""
            QLabel {
                font-size: 80px;
                color: white;
            }
        """)
        self.game_widget.hide()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(self.settings_widget)

        self.exit_btn.clicked.connect(self.close)
        self.play_btn.clicked.connect(self._on_play)
        self.settings_btn.clicked.connect(self._on_rules)
        self.back_btn.clicked.connect(self._on_back)

        self.audio = QAudioOutput()
        self.audio.setVolume(0.35)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)
        self.player.setSource(QUrl.fromLocalFile("./ui/cowboy_music.mp3"))
        self.player.mediaStatusChanged.connect(self.loop_music)
        self.player.play()

        self.showFullScreen()
        self.set_background(self.menu_bg)

    def _on_play(self):
        UI_EVENTS["start"] = True
        self.menu_widget.hide()
        self.settings_widget.hide()
        self.game_widget.show()
        self.set_background(self.game_bg)

    def _on_rules(self):
        UI_EVENTS["open_rules"] = True
        self.menu_widget.hide()
        self.settings_widget.show()
        self.game_widget.hide()
        self.set_background(self.menu_bg)

    def _on_back(self):
        UI_EVENTS["back_to_menu"] = True
        self.settings_widget.hide()
        self.menu_widget.show()
        self.game_widget.hide()
        self.set_background(self.menu_bg)

    def loop_music(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def set_background(self, path):
        pixmap = QPixmap(path).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio
        )
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        bg = self.game_bg if self.game_widget.isVisible() else self.menu_bg
        self.set_background(bg)
        super().resizeEvent(event)


class UIController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = GameMenu()

        self.camera_label = QLabel(self.window)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background: black;")
        self.camera_label.setFixedSize(960, 540)

        self.error_label = QLabel(self.window)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            color: red;
            font-size: 28px;
            background: rgba(0,0,0,150);
            padding: 10px;
        """)
        self.error_label.hide()

        layout = self.window.layout()
        layout.addWidget(self.camera_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignBottom)

        self.window.show()

    def draw_frame(self, frame):
        rgb = cvtColor(frame, COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)

        self.camera_label.setPixmap(
            pix.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio))
        self.app.processEvents()

    def show_error(self, text):
        if text:
            self.error_label.setText(text)
            self.error_label.show()
        else:
            self.error_label.hide()