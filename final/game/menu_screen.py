"""Головне меню гри."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from game.constants import COLOR_BG_SPACE
from game.background import ParallaxBackground


class MenuScreen(MDScreen):
    """Екран головного меню гри."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "menu_screen"
        self._build_ui()

    def _build_ui(self):
        # 1. Фоновий шар із зірками
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний вертикальний контейнер контенту
        root_layout = BoxLayout(
            orientation="vertical",
            padding=[24, 40, 24, 40],
            spacing=20,
            size_hint=(1, 1),
        )

        # Заголовок гри
        title_box = BoxLayout(orientation="vertical", size_hint=(1, None), height=140, spacing=8)

        game_title = MDLabel(
            text="GALAXY DEFENDER",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            font_style="Display",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=50,
        )

        subtitle = MDLabel(
            text="Космічний 2D шутер",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.7, 0.8, 0.95, 0.8),
            font_style="Title",
            role="medium",
            size_hint=(1, None),
            height=30,
        )

        title_box.add_widget(game_title)
        title_box.add_widget(subtitle)
        root_layout.add_widget(title_box)

        # Картка з описом керування та порадами
        info_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=200,
            padding=[16, 16, 16, 16],
            spacing=10,
        )
        with info_box.canvas.before:
            Color(0.08, 0.12, 0.22, 0.75)
            self.info_rect = Rectangle(pos=info_box.pos, size=info_box.size)
        info_box.bind(
            pos=lambda *args: setattr(self.info_rect, "pos", info_box.pos),
            size=lambda *args: setattr(self.info_rect, "size", info_box.size),
        )

        info_header = MDLabel(
            text="Правила гри & Керування",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.3, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=28,
        )
        info_box.add_widget(info_header)

        rules_text = (
            "• Керуйте кораблем проведенням пальця або екранними кнопками (< >)\n"
            "• Стріляйте лазерами та знищуйте ворожі кораблі\n"
            "• Уникайте ворожих куль — кожне влучання забирає HP!\n"
            "• Натисніть кнопку II для паузи під час бою"
        )
        info_desc = MDLabel(
            text=rules_text,
            halign="left",
            theme_text_color="Custom",
            text_color=(0.85, 0.9, 0.95, 0.9),
            font_style="Body",
            role="medium",
            size_hint=(1, 1),
        )
        info_box.add_widget(info_desc)
        root_layout.add_widget(info_box)

        # Контейнер кнопок
        btn_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=16,
            padding=[20, 20, 20, 20],
        )

        # Кнопка «Почати гру»
        start_btn = MDButton(
            MDButtonText(text="ПОЧАТИ ГРУ", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=54,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.65, 0.95, 1.0),
        )
        start_btn.bind(on_release=self._start_game)
        btn_box.add_widget(start_btn)

        # Кнопка «Вихід»
        exit_btn = MDButton(
            MDButtonText(
                text="ВИХІД",
                font_style="Title",
                role="small",
                theme_text_color="Custom",
                text_color=(0.9, 0.4, 0.4, 1.0),
            ),
            style="outlined",
            size_hint=(1, None),
            height=48,
        )
        exit_btn.bind(on_release=self._exit_app)
        btn_box.add_widget(exit_btn)

        root_layout.add_widget(btn_box)
        self.add_widget(root_layout)

    def _start_game(self, *args):
        """Перехід до екрана гри та запуск нової партії."""
        if self.manager:
            game_screen = self.manager.get_screen("game_screen")
            self.manager.current = "game_screen"
            game_screen.start_new_game()

    def _exit_app(self, *args):
        """Закриває додаток."""
        from kivy.app import App
        app = App.get_running_app()
        if app:
            app.stop()
