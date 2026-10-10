from kivy.clock import Clock
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
    """Екран головного меню гри з футуристичним кібер-дизайном (AAA Tactical Flight Deck)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "menu_screen"
        self._anim_event = None
        self._build_ui()

    def _build_ui(self):
        # 1. Зоряний паралакс-фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний вертикальний контейнер
        root_layout = BoxLayout(
            orientation="vertical",
            padding=[20, 26, 20, 24],
            spacing=14,
            size_hint=(1, 1),
        )

        # Тактичний системний тег верхівки
        top_tag = MDLabel(
            text="[ SECTOR DEFENSE COMMAND // MK-IV ]",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.25, 0.75, 1.0, 0.65),
            font_style="Label",
            role="medium",
            bold=True,
            size_hint=(1, None),
            height=18,
        )
        root_layout.add_widget(top_tag)

        # Заголовок гри
        title_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=96, spacing=4
        )

        game_title = MDLabel(
            text="✦ GALAXY DEFENDER ✦",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.05, 0.92, 1.0, 1.0),
            font_style="Display",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=48,
        )

        subtitle = MDLabel(
            text="⚔️  ELITE SPACE COMBAT SIMULATOR  ⚔️",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.6, 0.88, 1.0, 0.9),
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
            height=142,
            padding=[18, 14, 18, 14],
            spacing=8,
        )
        with status_card.canvas.before:
            Color(0.05, 0.09, 0.18, 0.94)
            self.card_bg = RoundedRectangle(
                pos=status_card.pos, size=status_card.size, radius=[14]
            )
            Color(0.18, 0.55, 0.95, 0.75)
            self.card_border = Line(
                rounded_rectangle=[
                    status_card.x,
                    status_card.y,
                    status_card.width,
                    status_card.height,
                    14,
                ],
                width=1.5,
            )
        status_card.bind(
            pos=lambda *args: self._update_card_rect(status_card),
            size=lambda *args: self._update_card_rect(status_card),
        )

        self.credits_badge = MDLabel(
            text="💠 КРЕДИТЫ: 0",
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
            text="🏆 РЕКОРД СЕССИИ: 0",
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
            text="🚀 КОРАБЛЬ: STRIKER «ФЕНИКС»",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.4, 0.82, 1.0, 0.9),
            font_style="Body",
            role="medium",
            bold=True,
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

        # Кнопка «ВСТУПИТЬ В БОЙ!»
        self.start_btn = MDButton(
            MDButtonText(
                text="🚀  ВСТУПИТЬ В БОЙ!",
                font_style="Headline",
                role="small",
                bold=True,
                theme_text_color="Custom",
                text_color=(0.02, 0.04, 0.10, 1.0),
            ),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.05, 0.88, 0.95, 1.0),
        )
        self.start_btn.bind(on_release=self._start_game)
        btn_box.add_widget(self.start_btn)

        # Кнопка «АНГАР — ВЕРФЬ КОРАБЛЕЙ»
        self.hangar_btn = MDButton(
            MDButtonText(
                text="🛸  АНГАР — ВЕРФЬ КОРАБЛЕЙ",
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

        sound_txt = "🔊 ЗВУК: ВКЛ" if is_sound_enabled() else "🔇 ЗВУК: ВЫКЛ"
        self.sound_toggle_btn = MDButton(
            MDButtonText(text=sound_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(0.5, 1),
        )
        self.sound_toggle_btn.bind(on_release=self._toggle_sound)
        audio_row.add_widget(self.sound_toggle_btn)

        music_txt = "🎵 МУЗЫКА: ВКЛ" if is_music_enabled() else "🔇 МУЗЫКА: ВЫКЛ"
        self.music_toggle_btn = MDButton(
            MDButtonText(text=music_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(0.5, 1),
        )
        self.music_toggle_btn.bind(on_release=self._toggle_music)
        audio_row.add_widget(self.music_toggle_btn)

        btn_box.add_widget(audio_row)

        # Кнопка «Покинуть игру»
        exit_btn = MDButton(
            MDButtonText(
                text="🚪  ПОКИНУТЬ ИГРУ",
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
        self.credits_badge.text = f"💠 КРЕДИТЫ: {get_credits()}"
        self.high_score_badge.text = f"🏆 РЕКОРД СЕССИИ: {get_high_score()}"

        ship_id = get_selected_ship()
        cfg = get_ship_config(ship_id)
        self.ship_badge.text = f"🚀 КОРАБЛЬ: {cfg.name.upper()}"

        # Оновлення кнопок звуку
        for child in self.sound_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🔊 ЗВУК: ВКЛ" if is_sound_enabled() else "🔇 ЗВУК: ВЫКЛ"
        for child in self.music_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🎵 МУЗЫКА: ВКЛ" if is_music_enabled() else "🔇 МУЗЫКА: ВЫКЛ"

    def on_enter(self, *args):
        self._anim_event = Clock.schedule_interval(self._on_anim_tick, 1.0 / 30.0)
        get_audio_manager().play_menu_music()

    def on_leave(self, *args):
        if hasattr(self, "_anim_event") and self._anim_event:
            Clock.unschedule(self._anim_event)
            self._anim_event = None

    def _on_anim_tick(self, dt: float):
        if hasattr(self, "bg") and self.bg:
            self.bg.update(dt)


    def _toggle_sound(self, *args):
        active = get_audio_manager().toggle_sound()
        for child in self.sound_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🔊 ЗВУК: ВКЛ" if active else "🔇 ЗВУК: ВЫКЛ"

    def _toggle_music(self, *args):
        active = get_audio_manager().toggle_music()
        for child in self.music_toggle_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🎵 МУЗЫКА: ВКЛ" if active else "🔇 МУЗЫКА: ВЫКЛ"


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
