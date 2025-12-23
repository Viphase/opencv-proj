from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFontDatabase, QFont, QImage
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from cv2 import COLOR_BGR2RGB, cvtColor
import sys


UI_EVENTS = {
    "start": False,
    "instruction_yes": False,
    "instruction_no": False,
    "open_rules": False,
    "continue_game": False,
}


class GameMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cowboy-Shootout")

        self.menu_bg = "./ui/menu_background.png"
        self.game_bg = "./ui/game_background.png"

        # ---------- FONT ----------
        with open("./ui/cowboy_font.ttf", "rb") as f:
            font_data = f.read()

        font_id = QFontDatabase.addApplicationFontFromData(font_data)
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]

        title_font = QFont(font_family)
        title_font.setPointSize(110)
        title_font.setBold(True)

        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout(self.menu_widget)

        self.label = QLabel("COWBOY SHOOTOUT")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(title_font)
        self.label.setStyleSheet("""
            QLabel {
                color: black;
                background: rgba(255,255,255,160);
                padding: 30px;
                border-radius: 30px;
            }
        """)

        self.play_btn = QPushButton("Играть")
        self.exit_btn = QPushButton("Выход")

        for b in (self.play_btn, self.exit_btn):
            b.setMinimumHeight(90)
            b.setFixedWidth(520)
            b.setStyleSheet("""
                QPushButton {
                    font-size: 44px;
                    color: white;
                    background: rgba(0,0,0,160);
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background: rgba(0,0,0,220);
                }
            """)

        menu_layout.addStretch()
        menu_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addSpacing(40)
        menu_layout.addWidget(self.play_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addWidget(self.exit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        menu_layout.addStretch()

        self.ask_widget = QWidget()
        ask_layout = QVBoxLayout(self.ask_widget)

        self.ask_label = QLabel("Хочешь увидеть правила?")
        self.ask_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ask_label.setStyleSheet("""
            QLabel {
                font-size: 56px;
                color: black;
                background: rgba(255,255,255,180);
                padding: 30px;
                border-radius: 25px;
            }
        """)

        self.yes_btn = QPushButton("Да")
        self.no_btn = QPushButton("Нет")

        for b in (self.yes_btn, self.no_btn):
            b.setFixedSize(260, 90)
            b.setStyleSheet("""
                QPushButton {
                    font-size: 40px;
                    color: white;
                    background: rgba(0,0,0,160);
                    border-radius: 20px;
                }
                QPushButton:hover {
                    background: rgba(0,0,0,220);
                }
            """)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(self.yes_btn)
        btn_row.addSpacing(50)
        btn_row.addWidget(self.no_btn)
        btn_row.addStretch()

        ask_layout.addStretch()
        ask_layout.addWidget(self.ask_label, alignment=Qt.AlignmentFlag.AlignCenter)
        ask_layout.addSpacing(40)
        ask_layout.addLayout(btn_row)
        ask_layout.addStretch()

        self.ask_widget.hide()

        self.rules_widget = QWidget()
        rules_layout = QVBoxLayout(self.rules_widget)

        self.rules_text = QLabel(
            "Cowboy-Shootout — дуэль на реакцию\n\n"
            "- Два игрока стоят напротив камеры\n"
            "- Правая рука пистолет - выстрел\n"
            "- Левая рука кулак - щит\n"
            "- У ковбоя есть 3 части тела - голова, тело и ноги\n"
            "  тебе нужно угадать куда выстрелить а где защититься\n"
            "- После нажатия кнопки продолжить, будет обратный отсчёт\n"
            "- Когда отсчёт пройдет - стреляй или защищайся!\n"
        )
        self.rules_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.rules_text.setStyleSheet("""
            QLabel {
                font-size: 34px;
                color: black;
                background: rgba(255,255,255,190);
                padding: 40px;
                border-radius: 25px;
            }
        """)

        self.continue_btn = QPushButton("Продолжить")
        self.continue_btn.setFixedSize(360, 80)
        self.continue_btn.setStyleSheet("""
            QPushButton {
                font-size: 36px;
                color: white;
                background: rgba(0,0,0,160);
                border-radius: 18px;
            }
            QPushButton:hover {
                background: rgba(0,0,0,220);
            }
        """)

        rules_layout.addStretch()
        rules_layout.addWidget(self.rules_text, alignment=Qt.AlignmentFlag.AlignCenter)
        rules_layout.addSpacing(40)
        rules_layout.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        rules_layout.addStretch()

        self.rules_widget.hide()

        self.game_widget = QLabel("")
        self.game_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.game_widget.setStyleSheet("""
            QLabel {
                font-size: 96px;
                color: white;
                background: rgba(0,0,0,0);
                padding: 20px;
                border-radius: 15px;
            }
        """)
        self.game_widget.hide()

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(self.ask_widget)
        main_layout.addWidget(self.rules_widget)
        main_layout.addWidget(self.game_widget)

        self.exit_btn.clicked.connect(sys.exit(0))
        self.play_btn.clicked.connect(lambda: UI_EVENTS.update({"start": True}))
        self.continue_btn.clicked.connect(lambda: UI_EVENTS.update({"continue_game": True}))

        self.yes_btn.clicked.connect(lambda: UI_EVENTS.update({"instruction_yes": True}))
        self.no_btn.clicked.connect(lambda: UI_EVENTS.update({"instruction_no": True}))

        self.audio = QAudioOutput()
        self.audio.setVolume(0.35)

        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio)
        self.player.setSource(QUrl.fromLocalFile("./ui/cowboy_music.mp3"))
        self.player.mediaStatusChanged.connect(self._loop_music)
        self.player.play()

        self.showFullScreen()
        self._set_background(self.menu_bg)

    def _loop_music(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.play()

    def _set_background(self, path):
        pixmap = QPixmap(path).scaled(
            self.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio
        )
        palette = QPalette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
        self.setPalette(palette)

    def resizeEvent(self, event):
        bg = self.game_bg if self.game_widget.isVisible() else self.menu_bg
        self._set_background(bg)
        super().resizeEvent(event)


class UIController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = GameMenu()

        self.camera_label = QLabel(self.window)
        self.camera_label.setFixedSize(960, 540)
        self.camera_label.setStyleSheet("background: black;")
        self.camera_label.hide()

        self.error_label = QLabel(self.window)
        self.error_label.setWordWrap(True)
        self.error_label.setMaximumWidth(800)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 26px;
                background: rgba(0,0,0,120);
                padding: 12px 20px;
                border-radius: 12px;
            }
        """)
        self.error_label.hide()

        self.window.show()

    def draw_frame(self, frame):
        rgb = cvtColor(frame, COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(img)

        self.camera_label.setPixmap(
            pix.scaled(self.camera_label.size(), Qt.AspectRatioMode.IgnoreAspectRatio)
        )
        self.camera_label.move(
            (self.window.width() - self.camera_label.width()) // 2,
            (self.window.height() - self.camera_label.height()) // 2
        )
        self.app.processEvents()

    def show_menu(self):
        self.window.menu_widget.show()
        self.window.ask_widget.hide()
        self.window.rules_widget.hide()
        self.window.game_widget.hide()
        self.camera_label.hide()

    def show_ask_rules(self):
        self.window.menu_widget.hide()
        self.window.ask_widget.show()
        self.window.rules_widget.hide()
        self.window.game_widget.hide()
        self.camera_label.hide()

    def show_rules(self):
        self.window.menu_widget.hide()
        self.window.ask_widget.hide()
        self.window.rules_widget.show()
        self.window.game_widget.hide()
        self.camera_label.hide()

    def show_game(self):
        self.window.menu_widget.hide()
        self.window.ask_widget.hide()
        self.window.rules_widget.hide()
        self.window.game_widget.show()
        self.camera_label.show()

    def show_countdown(self, value):
        self.window.game_widget.setText(str(value))

    def show_error(self, text):
        if text:
            self.error_label.setText(text)
            self.error_label.adjustSize()
            self.error_label.move(
                (self.window.width() - self.error_label.width()) // 2,
                self.window.height() - self.error_label.height() - 40
            )
            self.error_label.show()
        else:
            self.error_label.hide()
