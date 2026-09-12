from kivy.config import Config
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from game.game_over_screen import GameOverScreen

Config.set("graphics", "width", str(WINDOW_WIDTH))
Config.set("graphics", "height", str(WINDOW_HEIGHT))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from game.menu_screen import MenuScreen
from game.game_over_screen import GameOverScreen
# from game.game_screen import GameScreen
# from game.game_over_screen import GameOverScreen

class GalaxyDefenderApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        
        sm = MDScreenManager()
        sm.add_widget(MenuScreen(name="menu_screen"))
        sm.add_widget(GameOverScreen(name="game_over_screen"))
        # sm.add_widget(GameScreen(name="game_screen"))
        # sm.add_widget(GameOverScreen(name="game_over_screen"))
        return sm

if __name__ == "__main__":
    GalaxyDefenderApp().run()