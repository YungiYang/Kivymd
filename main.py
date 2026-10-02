"""Головна точка входу додатку Galaxy Defender."""

import os
from kivy.config import Config
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT

# Налаштування розміру вікна для вертикального формату Android
Config.set("graphics", "width", str(WINDOW_WIDTH))
Config.set("graphics", "height", str(WINDOW_HEIGHT))
Config.set("graphics", "resizable", "1")

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from game.menu_screen import MenuScreen
from game.game_screen import GameScreen
from game.game_over_screen import GameOverScreen
from game.hangar_screen import HangarScreen


class GalaxyDefenderApp(MDApp):
    """Головний клас гри на базі KivyMD."""

    def build(self):
        self.title = "Galaxy Defender - 2D Space Shooter"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"

        # Менеджер екранів гри
        self.sm = MDScreenManager()

        self.menu_screen = MenuScreen(name="menu_screen")
        self.game_screen = GameScreen(name="game_screen")
        self.game_over_screen = GameOverScreen(name="game_over_screen")
        self.hangar_screen = HangarScreen(name="hangar_screen")

        self.sm.add_widget(self.menu_screen)
        self.sm.add_widget(self.game_screen)
        self.sm.add_widget(self.game_over_screen)
        self.sm.add_widget(self.hangar_screen)

        self.sm.current = "menu_screen"

        # Обробка системної кнопки "Назад" на Android (код 27 / Escape)
        Window.bind(on_keyboard=self._on_android_back_button)

        return self.sm

    def _on_android_back_button(self, window, key, *args):
        """Обробляє натискання кнопки 'Назад' на пристроях Android."""
        if key == 27:
            current = self.sm.current
            if current == "game_screen":
                if not self.game_screen.is_paused:
                    self.game_screen.pause_game()
                else:
                    self.game_screen._quit_to_menu()
                return True
            elif current in ("game_over_screen", "hangar_screen"):
                self.sm.current = "menu_screen"
                return True
            elif current == "menu_screen":
                return False
        return False


if __name__ == "__main__":
    GalaxyDefenderApp().run()
