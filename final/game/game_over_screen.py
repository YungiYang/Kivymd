"""Екран Game Over із результатами гри."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from game.background import ParallaxBackground


class GameOverScreen(MDScreen):
    """Екран завершення гри."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game_over_screen"
        self.high_score = 0
        self._build_ui()

    def _build_ui(self):
        # 1. Зоряний фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний контейнер
        root_layout = BoxLayout(
            orientation="vertical",
            padding=[24, 40, 24, 40],
            spacing=20,
            size_hint=(1, 1),
        )

        # Заголовок Game Over
        title_box = BoxLayout(orientation="vertical", size_hint=(1, None), height=120, spacing=8)
        game_over_label = MDLabel(
            text="ГРА ЗАКІНЧЕНА",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.25, 0.25, 1.0),
            font_style="Display",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=50,
        )
        subtitle = MDLabel(
            text="Ваш корабель було знищено!",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.8, 0.8, 0.8, 0.8),
            font_style="Title",
            role="small",
            size_hint=(1, None),
            height=30,
        )
        title_box.add_widget(game_over_label)
        title_box.add_widget(subtitle)
        root_layout.add_widget(title_box)

        # Картка результатів (Рахунок та Рекорд)
        score_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=160,
            padding=[20, 20, 20, 20],
            spacing=12,
        )
        with score_card.canvas.before:
            Color(0.12, 0.14, 0.25, 0.8)
            self.card_rect = Rectangle(pos=score_card.pos, size=score_card.size)
        score_card.bind(
            pos=lambda *args: setattr(self.card_rect, "pos", score_card.pos),
            size=lambda *args: setattr(self.card_rect, "size", score_card.size),
        )

        self.score_label = MDLabel(
            text="Набрані бали: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.9, 1.0, 1.0),
            font_style="Headline",
            role="medium",
            bold=True,
            size_hint=(1, None),
            height=40,
        )
        self.high_score_label = MDLabel(
            text="Найкращий рекорд: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.2, 1.0),
            font_style="Title",
            role="medium",
            size_hint=(1, None),
            height=35,
        )
        score_card.add_widget(self.score_label)
        score_card.add_widget(self.high_score_label)
        root_layout.add_widget(score_card)

        # Кнопки дій
        btn_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=16,
            padding=[20, 20, 20, 20],
        )

        # Кнопка «Грати знову»
        restart_btn = MDButton(
            MDButtonText(text="ГРАТИ ЗНОВУ", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.75, 0.45, 1.0),
        )
        restart_btn.bind(on_release=self._restart_game)
        btn_box.add_widget(restart_btn)

        # Кнопка «Головне меню»
        menu_btn = MDButton(
            MDButtonText(
                text="ГОЛОВНЕ МЕНЮ",
                font_style="Title",
                role="small",
                theme_text_color="Custom",
                text_color=(0.85, 0.9, 1.0, 1.0),
            ),
            style="outlined",
            size_hint=(1, None),
            height=48,
        )
        menu_btn.bind(on_release=self._to_menu)
        btn_box.add_widget(menu_btn)

        root_layout.add_widget(btn_box)
        self.add_widget(root_layout)

    def set_score(self, score: int):
        """Встановлює набраний рахунок та оновлює рекорд."""
        if score > self.high_score:
            self.high_score = score
        self.score_label.text = f"Набрані бали: {score}"
        self.high_score_label.text = f"Найкращий рекорд: {self.high_score}"

    def _restart_game(self, *args):
        """Перезапускає нову гру."""
        if self.manager:
            game_screen = self.manager.get_screen("game_screen")
            self.manager.current = "game_screen"
            game_screen.start_new_game()

    def _to_menu(self, *args):
        """Повертає до головного меню."""
        if self.manager:
            self.manager.current = "menu_screen"
