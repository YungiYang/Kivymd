"""Екран Game Over із результатами гри, кредитами та переходом в ангар."""

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, RoundedRectangle, Line
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from game.background import ParallaxBackground
from game.storage import get_credits, get_high_score, update_high_score


class GameOverScreen(MDScreen):
    """Екран завершення гри з кібер-оформленням."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game_over_screen"
        self.score = 0
        self._build_ui()

    def _build_ui(self):
        # 1. Зоряний фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний контейнер
        root_layout = BoxLayout(
            orientation="vertical",
            padding=[24, 36, 24, 30],
            spacing=16,
            size_hint=(1, 1),
        )

        # Заголовок Game Over
        title_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=110, spacing=6
        )
        game_over_label = MDLabel(
            text="КОРАБЕЛЬ ЗНИЩЕНО",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.25, 0.32, 1.0),
            font_style="Display",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=48,
        )
        subtitle = MDLabel(
            text="— МІСІЮ ПЕРЕРВАНО —",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.85, 0.45, 0.5, 0.9),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=26,
        )
        title_box.add_widget(game_over_label)
        title_box.add_widget(subtitle)
        root_layout.add_widget(title_box)

        # Картка результатів (Рахунок, Рекорд, Кредити)
        score_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=165,
            padding=[18, 14, 18, 14],
            spacing=8,
        )
        with score_card.canvas.before:
            Color(0.08, 0.11, 0.22, 0.92)
            self.card_bg = RoundedRectangle(
                pos=score_card.pos, size=score_card.size, radius=[10]
            )
            Color(0.9, 0.25, 0.35, 0.5)
            self.card_border = Line(
                rounded_rectangle=[
                    score_card.x,
                    score_card.y,
                    score_card.width,
                    score_card.height,
                    10,
                ],
                width=1.5,
            )
        score_card.bind(
            pos=lambda *args: self._update_card_rect(score_card),
            size=lambda *args: self._update_card_rect(score_card),
        )

        self.score_label = MDLabel(
            text="📊 НАБРАНІ ОЧКИ: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.9, 1.0, 1.0),
            font_style="Title",
            role="large",
            bold=True,
            size_hint=(1, None),
            height=32,
        )
        self.high_score_label = MDLabel(
            text="🏆 НАЙКРАЩИЙ РЕКОРД: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.2, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=26,
        )
        self.credits_label = MDLabel(
            text="🪙 БАЛАНС КРЕДИТІВ: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.25, 1.0),
            font_style="Body",
            role="large",
            bold=True,
            size_hint=(1, None),
            height=26,
        )

        score_card.add_widget(self.score_label)
        score_card.add_widget(self.high_score_label)
        score_card.add_widget(self.credits_label)
        root_layout.add_widget(score_card)

        # Кнопки дій
        btn_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=12,
            padding=[8, 8, 8, 8],
        )

        # Кнопка «Грати знову»
        restart_btn = MDButton(
            MDButtonText(text="🔄 ГРАТИ ЗНОВУ", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(1, None),
            height=52,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.75, 0.45, 1.0),
        )
        restart_btn.bind(on_release=self._restart_game)
        btn_box.add_widget(restart_btn)

        # Кнопка «Ангар кораблів»
        hangar_btn = MDButton(
            MDButtonText(
                text="🛸 АНГАР / МАГАЗИН КОРАБЛІВ",
                font_style="Title",
                role="medium",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 0.9, 0.35, 1.0),
            ),
            style="elevated",
            size_hint=(1, None),
            height=50,
            theme_bg_color="Custom",
            md_bg_color=(0.22, 0.16, 0.05, 0.9),
        )
        hangar_btn.bind(on_release=self._to_hangar)
        btn_box.add_widget(hangar_btn)

        # Кнопка «Головне меню»
        menu_btn = MDButton(
            MDButtonText(
                text="🏠 ГОЛОВНЕ МЕНЮ",
                font_style="Title",
                role="small",
                theme_text_color="Custom",
                text_color=(0.85, 0.9, 1.0, 1.0),
            ),
            style="outlined",
            size_hint=(1, None),
            height=46,
        )
        menu_btn.bind(on_release=self._to_menu)
        btn_box.add_widget(menu_btn)

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

    def set_score(self, score: int):
        """Встановлює набраний рахунок, оновлює рекорд та зберігає прогрес."""
        self.score = score
        update_high_score(score)
        hs = get_high_score()
        self.score_label.text = f"📊 НАБРАНІ ОЧКИ: {score}"
        self.high_score_label.text = f"🏆 НАЙКРАЩИЙ РЕКОРД: {hs}"
        self.credits_label.text = f"🪙 БАЛАНС КРЕДИТІВ: {get_credits()}"

    def on_pre_enter(self, *args):
        self.credits_label.text = f"🪙 БАЛАНС КРЕДИТІВ: {get_credits()}"
        self.high_score_label.text = f"🏆 НАЙКРАЩИЙ РЕКОРД: {get_high_score()}"

    def _restart_game(self, *args):
        """Перезапускає нову гру."""
        if self.manager:
            game_screen = self.manager.get_screen("game_screen")
            self.manager.current = "game_screen"
            game_screen.start_new_game()

    def _to_hangar(self, *args):
        """Переходить до ангару кораблів."""
        if self.manager:
            self.manager.current = "hangar_screen"

    def _to_menu(self, *args):
        """Повертає до головного меню."""
        if self.manager:
            self.manager.current = "menu_screen"
