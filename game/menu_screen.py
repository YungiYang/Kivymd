"""Головне меню гри Galaxy Defender з кіберпанк дизайном, ангаром та налаштуваннями."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from game.background import ParallaxBackground
from game.storage import (
    get_credits,
    get_high_score,
    get_selected_ship,
    is_sound_enabled,
    is_music_enabled,
)
from game.ships import get_ship_config
from game.audio import get_audio_manager


class MenuScreen(MDScreen):
    """Екран головного меню гри з футуристичним кібер-дизайном."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "menu_screen"
        self._build_ui()

    def _build_ui(self):
        # 1. Зоряний паралакс-фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний вертикальний контейнер
        root_layout = BoxLayout(
            orientation="vertical",
            padding=[20, 32, 20, 28],
            spacing=16,
            size_hint=(1, 1),
        )

        # Заголовок гри
        title_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=110, spacing=6
        )

        game_title = MDLabel(
            text="GALAXY DEFENDER",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.15, 0.9, 1.0, 1.0),
            font_style="Display",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=48,
        )

        subtitle = MDLabel(
            text="★ КІБЕРПРОСТОРОВИЙ 2D ШУТЕР ★",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.5, 0.8, 1.0, 0.85),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=26,
        )

        title_box.add_widget(game_title)
        title_box.add_widget(subtitle)
        root_layout.add_widget(title_box)

        # Картка профілю пілота (Рекорд, Баланс кредитів, Поточний корабель)
        status_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=145,
            padding=[16, 12, 16, 12],
            spacing=8,
        )
        with status_card.canvas.before:
            Color(0.06, 0.10, 0.20, 0.92)
            self.card_bg = RoundedRectangle(
                pos=status_card.pos, size=status_card.size, radius=[10]
            )
            Color(0.18, 0.55, 0.95, 0.6)
            self.card_border = Line(
                rounded_rectangle=[
                    status_card.x,
                    status_card.y,
                    status_card.width,
                    status_card.height,
                    10,
                ],
                width=1.5,
            )
        status_card.bind(
            pos=lambda *args: self._update_card_rect(status_card),
            size=lambda *args: self._update_card_rect(status_card),
        )

        self.credits_badge = MDLabel(
            text="🪙 КРЕДИТИ: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.25, 1.0),
            font_style="Title",
            role="medium",
            bold=True,
            size_hint=(1, None),
            height=28,
        )

        self.high_score_badge = MDLabel(
            text="🏆 РЕКОРД: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.3, 0.95, 0.5, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=26,
        )

        self.ship_badge = MDLabel(
            text="🛸 КОРАБЕЛЬ: ШТУРМОВИК «ФЕНІКС»",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.4, 0.8, 1.0, 0.9),
            font_style="Body",
            role="medium",
            size_hint=(1, None),
            height=24,
        )

        status_card.add_widget(self.credits_badge)
        status_card.add_widget(self.high_score_badge)
        status_card.add_widget(self.ship_badge)
        root_layout.add_widget(status_card)

        # Контейнер головних дій
        btn_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=12,
            padding=[8, 6, 8, 6],
        )

        # Кнопка «В БІЙ!»
        self.start_btn = MDButton(
            MDButtonText(
                text="🚀 В БІЙ!",
                font_style="Headline",
                role="small",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 1.0, 1.0, 1.0),
            ),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.65, 0.95, 1.0),
        )
        self.start_btn.bind(on_release=self._start_game)
        btn_box.add_widget(self.start_btn)

        # Кнопка «АНГАР КОРАБЛІВ» (Магазин нових типів зброї)
        self.hangar_btn = MDButton(
            MDButtonText(
                text="🛸 АНГАР КОРАБЛІВ (МАГАЗИН)",
                font_style="Title",
                role="medium",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 0.92, 0.35, 1.0),
            ),
            style="elevated",
            size_hint=(1, None),
            height=50,
            theme_bg_color="Custom",
            md_bg_color=(0.22, 0.16, 0.05, 0.9),
        )
        self.hangar_btn.bind(on_release=self._open_hangar)
        btn_box.add_widget(self.hangar_btn)

        # Рядок налаштувань звуку та музики
        audio_row = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=46,
            spacing=10,
        )

        sound_txt = "🔊 ЗВУК: УВІМК" if is_sound_enabled() else "🔇 ЗВУК: ВИМК"
        self.sound_toggle_btn = MDButton(
            MDButtonText(text=sound_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(0.5, 1),
        )
        self.sound_toggle_btn.bind(on_release=self._toggle_sound)
        audio_row.add_widget(self.sound_toggle_btn)

        music_txt = "🎵 МУЗИКА: УВІМК" if is_music_enabled() else "🔇 МУЗИКА: ВИМК"
        self.music_toggle_btn = MDButton(
            MDButtonText(text=music_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(0.5, 1),
        )
        self.music_toggle_btn.bind(on_release=self._toggle_music)
        audio_row.add_widget(self.music_toggle_btn)

        btn_box.add_widget(audio_row)

        # Кнопка «Вихід»
        exit_btn = MDButton(
            MDButtonText(
                text="ВИХІД З ГРИ",
                font_style="Title",
                role="small",
                theme_text_color="Custom",
                text_color=(0.95, 0.38, 0.38, 1.0),
            ),
            style="outlined",
            size_hint=(1, None),
            height=44,
        )
        exit_btn.bind(on_release=self._exit_app)
        btn_box.add_widget(exit_btn)

        root_layout.add_widget(btn_box)
        self.add_widget(root_layout)

    def _update_card_rect(self, card):
        if hasattr(self, "card_bg"):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size
            self.card_border.rounded_rectangle = [
                card.x,
                card.y,
                card.width,
                card.height,
                10,
            ]

    def on_pre_enter(self, *args):
        """Оновлює показники кредитів, рекорду та обраного корабля при переході до меню."""
        self.credits_badge.text = f"🪙 КРЕДИТИ: {get_credits()}"
        self.high_score_badge.text = f"🏆 РЕКОРД: {get_high_score()}"

        ship_id = get_selected_ship()
        cfg = get_ship_config(ship_id)
        self.ship_badge.text = f"🛸 КОРАБЕЛЬ: {cfg.name.upper()}"

        # Оновлення кнопок звуку
        for child in self.sound_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🔊 ЗВУК: УВІМК" if is_sound_enabled() else "🔇 ЗВУК: ВИМК"
        for child in self.music_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🎵 МУЗИКА: УВІМК" if is_music_enabled() else "🔇 МУЗИКА: ВИМК"

    def _toggle_sound(self, *args):
        active = get_audio_manager().toggle_sound()
        for child in self.sound_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🔊 ЗВУК: УВІМК" if active else "🔇 ЗВУК: ВИМК"

    def _toggle_music(self, *args):
        active = get_audio_manager().toggle_music()
        for child in self.music_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🎵 МУЗИКА: УВІМК" if active else "🔇 МУЗИКА: ВИМК"

    def _start_game(self, *args):
        """Перехід до екрана гри та запуск нової партії."""
        if self.manager:
            game_screen = self.manager.get_screen("game_screen")
            self.manager.current = "game_screen"
            game_screen.start_new_game()

    def _open_hangar(self, *args):
        """Перехід до ангару покупки та вибору кораблів."""
        if self.manager:
            self.manager.current = "hangar_screen"

    def _exit_app(self, *args):
        from kivy.app import App
        app = App.get_running_app()
        if app:
            app.stop()
