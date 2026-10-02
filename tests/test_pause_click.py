import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from game.game_screen import GameScreen

class TouchEvent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.grab_current = None
        self.grab_list = []
        self.is_touch = True
        self.ud = {}

    def grab(self, widget):
        self.grab_current = widget
        self.grab_list.append(widget)

    def ungrab(self, widget):
        if widget in self.grab_list:
            self.grab_list.remove(widget)
        if self.grab_current == widget:
            self.grab_current = None

    def push(self): pass
    def pop(self): pass
    def apply_transform_2d(self, fn): pass


def test_pause_flow():
    print("=== ТЕСТУВАННЯ НОВОЇ КНОПКИ ТА МЕХАНІЗМУ ПАУЗИ ===")
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
    gs.hud_box.do_layout()
    gs.start_new_game()

    assert gs.is_paused is False, "Гра не повинна бути на паузі на початку"
    print("[OK] Гра успішно запущена")

    # 1. Торкання кнопки паузи (або верхнього правого кутка)
    touch_pause = TouchEvent(gs.pause_btn.center_x, gs.pause_btn.center_y)
    handled = gs.on_touch_down(touch_pause)
    assert handled is True, "on_touch_down не обробив торкання кнопки паузи"
    assert gs.is_paused is True, "Кнопка паузи не активувала стан паузи"
    assert gs.pause_overlay in gs.root_layout.children, "Оверлей паузи не з'явився у віджетах"
    print("[OK] Натискання на кнопку паузи 'II' успішно активує паузу та показує меню")

    # 2. Торкання кнопки «Продовжити» (Resume)
    touch_resume = TouchEvent(gs.resume_btn.center_x, gs.resume_btn.center_y)
    handled_resume = gs.on_touch_down(touch_resume)
    assert handled_resume is True, "on_touch_down не обробив кнопку «Продовжити»"
    assert gs.is_paused is False, "Кнопка «Продовжити» не відновила гру"
    assert gs.pause_overlay not in gs.root_layout.children, "Оверлей паузи не видалився після відновлення"
    print("[OK] Натискання на кнопку «Продовжити» успішно знімає гру з паузи")

    # 3. Торкання кутка (запасна зона натискання на сенсорному екрані)
    touch_corner = TouchEvent(400, 730)
    handled_corner = gs.on_touch_down(touch_corner)
    assert handled_corner is True, "Кутова зона паузи не спрацювала"
    assert gs.is_paused is True, "Кутова зона не перевела гру на паузу"
    print("[OK] Зручна кутова зона паузи працює бездоганно")

    print("\n=== ВСІ ТЕСТИ ПАУЗИ ПРОЙШЛИ УСПІШНО! ===")


if __name__ == "__main__":
    test_pause_flow()
