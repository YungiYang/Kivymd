import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from game.game_screen import GameScreen

class ControlTouch:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.spos = (x / 420.0, y / 750.0)
        self.device = "mouse"
        self.id = 1
        self.is_touch = True
        self.is_double_tap = False
        self.is_triple_tap = False
        self.is_mouse_scrolling = False
        self.grab_current = None
        self.grab_list = []
        self.ud = {}
        self.button = "left"
        self._pos_stack = []

    def grab(self, widget):
        if widget not in self.grab_list:
            self.grab_list.append(widget)

    def ungrab(self, widget):
        if widget in self.grab_list:
            self.grab_list.remove(widget)

    def push(self):
        self._pos_stack.append((self.x, self.y))

    def pop(self):
        if self._pos_stack:
            self.x, self.y = self._pos_stack.pop()
            self.pos = (self.x, self.y)

    def apply_transform_2d(self, fn):
        self.x, self.y = fn(self.x, self.y)
        self.pos = (self.x, self.y)


def test_control_buttons():
    print("=== ТЕСТУВАННЯ КНОПОК КЕРУВАННЯ КОРАБЛЕМ ===")
    app = MDApp()
    sm = MDScreenManager()
    gs = GameScreen(name="game_screen")
    sm.add_widget(gs)

    gs.width = 420
    gs.height = 750
    sm.width = 420
    sm.height = 750
    sm.do_layout()
    gs.do_layout()
    gs.root_layout.do_layout()
    gs.controls_box.do_layout()
    gs.hud_box.do_layout()
    gs.start_new_game()

    # 1. Тест кнопки «Ліворуч»
    t_left = ControlTouch(gs.btn_left.center_x, gs.btn_left.center_y)
    sm.dispatch("on_touch_down", t_left)
    assert gs.player.move_direction == -1, f"Очікувався рух ліворуч (-1), отримано {gs.player.move_direction}"
    assert gs.btn_left.state == "down", "Стан кнопки має бути 'down'"
    print("[OK] Натискання '< ЛІВОРУЧ' активує рух ліворуч")

    # Відпускання кнопки «Ліворуч»
    for w in list(t_left.grab_list):
        t_left.grab_current = w
        w.dispatch("on_touch_up", t_left)
    t_left.grab_current = None
    assert gs.player.move_direction == 0, f"Після відпускання рух має зупинитися (0), отримано {gs.player.move_direction}"
    assert gs.btn_left.state == "normal", "Стан кнопки має повернутися у 'normal'"
    print("[OK] Відпускання '< ЛІВОРУЧ' зупиняє корабель")

    # 2. Тест кнопки «Праворуч»
    t_right = ControlTouch(gs.btn_right.center_x, gs.btn_right.center_y)
    sm.dispatch("on_touch_down", t_right)
    assert gs.player.move_direction == 1, f"Очікувався рух праворуч (1), отримано {gs.player.move_direction}"
    assert gs.btn_right.state == "down", "Стан кнопки має бути 'down'"
    print("[OK] Натискання 'ПРАВОРУЧ >' активує рух праворуч")

    for w in list(t_right.grab_list):
        t_right.grab_current = w
        w.dispatch("on_touch_up", t_right)
    t_right.grab_current = None
    assert gs.player.move_direction == 0, f"Після відпускання рух має бути 0, отримано {gs.player.move_direction}"
    print("[OK] Відпускання 'ПРАВОРУЧ >' зупиняє корабель")

    # 3. Тест кнопки «Вогонь»
    t_fire = ControlTouch(gs.btn_fire.center_x, gs.btn_fire.center_y)
    sm.dispatch("on_touch_down", t_fire)
    assert gs.is_shooting is True, "Натискання кнопки 'ВОГОНЬ' має увімкнути стрільбу"
    print("[OK] Натискання кнопки 'ВОГОНЬ' активує стрільбу")

    for w in list(t_fire.grab_list):
        t_fire.grab_current = w
        w.dispatch("on_touch_up", t_fire)
    t_fire.grab_current = None
    assert gs.is_shooting is False, "Відпускання кнопки 'ВОГОНЬ' має вимкнути стрільбу"
    print("[OK] Відпускання кнопки 'ВОГОНЬ' вимикає стрільбу")

    # 4. Перевірка кнопки Паузи
    t_pause = ControlTouch(gs.pause_btn.center_x, gs.pause_btn.center_y)
    sm.dispatch("on_touch_down", t_pause)
    assert gs.is_paused is True, "Кнопка 'II' має активувати паузу"
    print("[OK] Кнопка паузи 'II' працює штатно")

    print("\n=== ВСІ ТЕСТИ КНОПОК КЕРУВАННЯ УСПІШНО ПРОЙШЛИ! ===")

if __name__ == "__main__":
    test_control_buttons()
