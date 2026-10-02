"""Автоматизований тест перевірки логіки гри Galaxy Defender."""

import os
import sys

# Додаємо корінь проєкту до шляхів пошуку
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from game.constants import (
    PLAYER_MAX_HP,
    PLAYER_FIRE_COOLDOWN,
    ENEMY_DEFAULT_HP,
)
from game.background import ParallaxBackground
from game.entities import (
    PlayerShip,
    Enemy,
    Bullet,
    Particle,
    check_collision,
    create_explosion,
)
from game.menu_screen import MenuScreen
from game.game_screen import GameScreen
from game.game_over_screen import GameOverScreen


class DummyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        sm = MDScreenManager()
        self.menu_screen = MenuScreen(name="menu_screen")
        self.game_screen = GameScreen(name="game_screen")
        self.game_over_screen = GameOverScreen(name="game_over_screen")
        sm.add_widget(self.menu_screen)
        sm.add_widget(self.game_screen)
        sm.add_widget(self.game_over_screen)
        return sm


def test_game_components():
    print("=== ЗАПУСК ТЕСТУВАННЯ КОМПОНЕНТІВ ГРИ ===")

    # 1. Ініціалізація додатку та екранів
    app = DummyApp()
    sm = app.build()
    assert sm.has_screen("menu_screen"), "Відсутній menu_screen"
    assert sm.has_screen("game_screen"), "Відсутній game_screen"
    assert sm.has_screen("game_over_screen"), "Відсутній game_over_screen"
    print("[OK] 3 екрани успішно створені та додані до MDScreenManager")

    game_screen: GameScreen = sm.get_screen("game_screen")
    game_screen.width = 420
    game_screen.height = 750

    # 2. Тест 2-шарового фону
    bg = ParallaxBackground(size=(420, 750))
    bg.update(0.016)
    assert len(bg.layer1_stars) > 0, "Шар 1 зірок порожній"
    assert len(bg.layer2_stars) > 0, "Шар 2 зірок порожній"
    print(f"[OK] Двошаровий рухомий фон: {len(bg.layer1_stars)} далеких зірок, {len(bg.layer2_stars)} близьких зірок")

    # 3. Тест гравця
    player = PlayerShip()
    player.x = 200
    player.y = 80
    assert player.hp == PLAYER_MAX_HP, "HP гравця не дорівнює максимуму"
    assert player.can_shoot() is True, "Гравець має могти стріляти на старті"

    # Стрільба та кулдаун
    b1 = player.shoot()
    assert isinstance(b1, Bullet), "Постріл не повернув об'єкт Bullet"
    assert b1.is_player is True, "Куля має належати гравцеві"
    assert player.can_shoot() is False, "Кулдаун стрільби не спрацював"

    # Симуляція спливання часу кулдауну
    for _ in range(16):
        player.update(0.016, 420)
    assert player.can_shoot() is True, "Кулдаун мав відновитися після оновлення"
    assert len(player.engine_particles) > 0, "Часточки полум'я двигунів не згенеровані"
    print("[OK] Гравець: стрільба, кулдаун та часточки полум'я працюють вірно")

    # Рух ліворуч/праворуч
    initial_x = player.x
    player.set_move_direction(1)
    player.update(0.1, 420)
    assert player.x > initial_x, "Корабель не змістився праворуч"

    player.set_move_direction(-1)
    player.update(0.2, 420)
    assert player.x < initial_x + 10, "Корабель не змістився ліворуч"
    player.set_move_direction(0)
    print("[OK] Рух корабля ліворуч та праворуч функціонує коректно")

    # 4. Тест ворогів
    enemy = Enemy(x=150, y=700)
    assert enemy.hp == ENEMY_DEFAULT_HP, "HP ворога некоректне"
    initial_ey = enemy.y
    enemy_bullet = None
    for _ in range(200):
        b = enemy.update(0.016)
        if b:
            enemy_bullet = b
            break
    assert enemy.y < initial_ey, "Ворог не рухається вниз"
    assert enemy_bullet is not None, "Ворог не вистрілив кулею протягом часу"
    assert enemy_bullet.is_player is False, "Куля ворога має прапорець is_player=False"
    assert enemy_bullet.vy < 0, "Куля ворога має рухатися вниз (vy < 0)"
    print("[OK] Вороги: автоматичний рух вниз, стрільба та таймери працюють")

    # 5. Тест куль та колізій
    # Куля гравця -> Ворог
    player_bullet = Bullet(x=150, y=600, is_player=True)
    assert player_bullet.vy > 0, "Куля гравця має рухатися вгору (vy > 0)"

    enemy.x = 150
    enemy.y = 600
    assert check_collision(player_bullet, enemy) is True, "Колізія кулі з ворогом не виявлена"

    initial_hp = enemy.hp
    enemy.take_damage(player_bullet.damage)
    assert enemy.hp < initial_hp, "HP ворога не зменшилось після пошкодження"
    print("[OK] Колізія: куля гравця -> ворог успішно реєструється та завдає шкоди")

    # Куля ворога -> Гравець
    enemy_bullet.x = player.x
    enemy_bullet.y = player.y
    assert check_collision(enemy_bullet, player) is True, "Колізія ворожої кулі з гравцем не виявлена"
    player_hp_before = player.hp
    player.take_damage(enemy_bullet.damage)
    assert player.hp < player_hp_before, "HP гравця не зменшилось"
    print("[OK] Колізія: ворожа куля -> гравець успішно реєструється")

    # 6. Тест вибухів та часточок
    explosions = create_explosion(200, 300, count=15)
    assert len(explosions) == 15, "Кількість часточок вибуху не відповідає заданій"
    explosions[0].update(0.1)
    print("[OK] Система часточок вибуху генерує правильну кількість часточок")

    # 7. Тест ігрового циклу, запуску гри та паузи
    game_screen.start_new_game()
    assert game_screen.is_playing is True, "Гра не перейшла в стан запущеної"
    assert game_screen.is_paused is False, "Гра не повинна бути на паузі на старті"

    # Пауза
    game_screen.pause_game()
    assert game_screen.is_paused is True, "Пауза не активувалася"
    assert game_screen.game_clock_event is None, "Ігровий цикл (Clock) не зупинився на паузі"

    # Відновлення гри
    game_screen.resume_game()
    assert game_screen.is_paused is False, "Гра не відновилася після паузи"
    assert game_screen.game_clock_event is not None, "Ігровий цикл (Clock) не відновився"
    print("[OK] Пауза: зупиняє ігровий цикл та коректно відновлює гру")

    # 8. Тест Game Over при HP = 0
    game_screen.player.hp = 0
    game_screen._trigger_game_over()
    assert game_screen.is_playing is False, "Гра не зупинилася при HP = 0"
    print("[OK] Game Over: коректне завершення гри при нульовому HP")

    print("\n=== ВСІ ТЕСТИ ПРОЙДЕНО УСПІШНО! ===")


if __name__ == "__main__":
    test_game_components()
