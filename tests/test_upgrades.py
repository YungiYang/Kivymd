"""Тести системи карток покращень (Upgrades) кожні 1000 очок."""

import os
import sys

# Корінь проєкту до шляхів
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from game.constants import (
    PLAYER_MAX_HP,
    PLAYER_SPEED,
    PLAYER_FIRE_COOLDOWN,
    BULLET_PLAYER_DAMAGE,
    BULLET_PLAYER_SPEED,
    ENEMY_DEFAULT_HP,
)
from game.entities import PlayerShip, Bullet
from game.upgrades import (
    Upgrade,
    get_random_upgrades,
    UpgradeOverlay,
    UpgradeCard,
)
from game.game_screen import GameScreen
from game.menu_screen import MenuScreen
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


def test_player_upgrade_attributes():
    print("--- 1. Тестування характеристик корабля гравця та мульти-стрільби ---")
    player = PlayerShip()

    # Базові параметри
    assert player.hp == PLAYER_MAX_HP
    assert player.max_hp == PLAYER_MAX_HP
    assert player.speed == PLAYER_SPEED
    assert player.fire_cooldown == PLAYER_FIRE_COOLDOWN
    assert player.bullet_damage == BULLET_PLAYER_DAMAGE
    assert player.bullet_speed == BULLET_PLAYER_SPEED
    assert player.shot_level == 1
    assert player.shield == 0

    # Одинарний постріл (shot_level = 1)
    b_single = player.shoot_bullets()
    assert len(b_single) == 1
    assert b_single[0].damage == BULLET_PLAYER_DAMAGE
    assert isinstance(player.shoot(), Bullet)

    # Подвійний постріл (shot_level = 2)
    player.shot_level = 2
    b_double = player.shoot_bullets()
    assert len(b_double) == 2
    assert b_double[0].damage == BULLET_PLAYER_DAMAGE
    assert b_double[1].damage == BULLET_PLAYER_DAMAGE

    # Потрійний постріл (shot_level = 3)
    player.shot_level = 3
    b_triple = player.shoot_bullets()
    assert len(b_triple) == 3

    # Перевірка щита
    player.shield = 2
    absorbed = player.take_damage(30)
    assert absorbed is True
    assert player.shield == 1
    assert player.hp == PLAYER_MAX_HP, "HP не мало зменшитися при активному щиті"

    absorbed2 = player.take_damage(30)
    assert absorbed2 is True
    assert player.shield == 0

    # Коли щит вичерпано, шкода завдається HP
    absorbed3 = player.take_damage(20)
    assert absorbed3 is False
    assert player.hp == PLAYER_MAX_HP - 20

    # Скидання параметрів
    player.reset_stats()
    assert player.hp == PLAYER_MAX_HP
    assert player.shot_level == 1
    assert player.shield == 0
    print("[OK] Мульти-стрільба (1-3 лазери), щит та скидання параметрів успішно перевірено")


def test_upgrades_pool_and_effects():
    print("--- 2. Тестування генератора карток покращень та їх ефектів ---")
    player = PlayerShip()

    # Генерація вибірки з 3 карток
    upgrades = get_random_upgrades(player, count=3)
    assert len(upgrades) == 3
    assert len({u.uid for u in upgrades}) == 3, "Картки мають бути унікальними"

    # Застосування покращення швидкострільності
    old_cd = player.fire_cooldown
    rf_upgrade = Upgrade(
        uid="rapid_fire",
        title="Швидкострільність",
        desc="+30%",
        icon="⚡",
        color=(0.2, 0.9, 1.0, 1.0),
        apply_fn=lambda p: setattr(p, "fire_cooldown", p.fire_cooldown * 0.72),
    )
    rf_upgrade.apply(player)
    assert player.fire_cooldown < old_cd

    # Застосування покращення шкоди
    old_dmg = player.bullet_damage
    dmg_upgrade = Upgrade(
        uid="damage_boost",
        title="Потужні заряди",
        desc="+18",
        icon="☄️",
        color=(1.0, 0.5, 0.15, 1.0),
        apply_fn=lambda p: setattr(p, "bullet_damage", p.bullet_damage + 18),
    )
    dmg_upgrade.apply(player)
    assert player.bullet_damage == old_dmg + 18

    # Застосування покращення броні та ремонту
    player.hp = 10
    armor_upgrade = Upgrade(
        uid="nano_armor",
        title="Броня",
        desc="+25",
        icon="❤️",
        color=(0.2, 1.0, 0.45, 1.0),
        apply_fn=lambda p: (
            setattr(p, "max_hp", p.max_hp + 25),
            setattr(p, "hp", p.max_hp),
        ),
    )
    armor_upgrade.apply(player)
    assert player.max_hp == PLAYER_MAX_HP + 25
    assert player.hp == PLAYER_MAX_HP + 25

    print("[OK] Пул карток та всі типи покращень коректно модифікують сутність гравця")


def test_upgrade_overlay_and_game_trigger():
    print("--- 3. Тестування відкриття модального вікна кожні 1000 очок ---")
    app = DummyApp()
    sm = app.build()
    game_screen: GameScreen = sm.get_screen("game_screen")
    game_screen.width = 420
    game_screen.height = 750

    game_screen.start_new_game()
    assert game_screen.next_upgrade_score == 1000
    assert game_screen.is_upgrading is False
    assert game_screen.upgrade_overlay.opacity == 0.0

    # Симулюємо досягнення 1000 очок (1-ше покращення, базова ціна 1000)
    game_screen.score = 1000
    game_screen._handle_bullet_collisions()

    # Оверлей покращень має відкритися
    assert game_screen.is_upgrading is True
    assert game_screen.upgrade_overlay in game_screen.root_layout.children
    assert game_screen.upgrade_overlay.opacity == 1.0
    # Наступний поріг прогресивно збільшується (+1500 -> 2500)
    assert game_screen.next_upgrade_score == 2500
    assert len(game_screen.upgrade_overlay.current_cards) == 3

    # Вибираємо картку за допомогою виклику select_by_index(0)
    game_screen.upgrade_overlay.select_by_index(0)

    # Після вибору оверлей закривається, гра готова продовжитись
    assert game_screen.is_upgrading is False
    assert game_screen.upgrade_overlay.opacity == 0.0
    assert game_screen.next_upgrade_score == 2500

    # 2-ге покращення: досягаємо 2500 очок (наступна ціна +2000 -> 4500)
    game_screen.score = 2500
    game_screen._handle_bullet_collisions()
    assert game_screen.is_upgrading is True
    assert game_screen.next_upgrade_score == 4500
    game_screen.upgrade_overlay.select_by_index(1)
    assert game_screen.is_upgrading is False
    assert game_screen.next_upgrade_score == 4500

    # 3-тє покращення: досягаємо 4500 очок (наступна ціна +2500 -> 7000)
    game_screen.score = 4500
    game_screen._handle_bullet_collisions()
    assert game_screen.is_upgrading is True
    assert game_screen.next_upgrade_score == 7000
    game_screen.upgrade_overlay.select_by_index(2)
    assert game_screen.is_upgrading is False
    assert game_screen.next_upgrade_score == 7000

    print("[OK] Прогресивне зростання вартості карток (1000 -> 2500 -> 4500 -> 7000) успішно працює!")


def test_boss_and_enemy_types():
    print("--- 4. Тестування різних типів ворогів, атак та ескалації босів ---")
    from game.entities import Enemy, Boss

    # 1. Тест 5 класів кораблів ворогів
    fighter = Enemy(100, 500, enemy_type="fighter")
    assert fighter.hp == ENEMY_DEFAULT_HP
    assert fighter.score_value == 100

    scout = Enemy(100, 500, enemy_type="scout")
    assert scout.hp == 20
    assert scout.speed > fighter.speed
    assert scout.score_value == 150
    # Розвідник робить зигзаг
    old_x = scout.x
    scout.update(0.1)
    assert scout.x != old_x

    sniper = Enemy(100, 500, enemy_type="sniper")
    assert sniper.hp == 30
    assert sniper.score_value == 220
    sniper.time_since_last_shot = 99.0
    sniper_shot = sniper.update(0.016, player_pos=(200, 100))
    assert sniper_shot is not None
    assert sniper_shot.vy < 0

    bomber = Enemy(100, 500, enemy_type="bomber")
    assert bomber.hp == 55
    assert bomber.score_value == 280
    bomber.time_since_last_shot = 99.0
    bomber_shots = bomber.update(0.016)
    assert isinstance(bomber_shots, list)
    assert len(bomber_shots) == 3, "Бомбардувальник має стріляти віялом з 3 куль"

    cruiser = Enemy(100, 500, enemy_type="cruiser")
    assert cruiser.hp == 90
    assert cruiser.score_value == 380
    cruiser.time_since_last_shot = 99.0
    cruiser_shots = cruiser.update(0.016)
    assert isinstance(cruiser_shots, list)
    assert len(cruiser_shots) == 2, "Крейсер має робити спарений залп з 2 важких куль"
    print("[OK] Всі 5 класів ворожих кораблів та їх унікальні атаки успішно протестовано")

    # 2. Тест масштабування складності босів
    boss1 = Boss(150, 700, boss_level=1)
    boss2 = Boss(150, 700, boss_level=2)
    boss3 = Boss(150, 700, boss_level=3)

    assert boss1.max_hp == 2500
    assert boss2.max_hp == 4000
    assert boss3.max_hp == 5500
    assert boss2.max_hp > boss1.max_hp, "HP боса має зростати з рівнем"
    assert boss2.speed > boss1.speed, "Швидкість боса має зростати з рівнем"
    assert boss2.score_value > boss1.score_value, "Нагорода за боса має зростати"
    assert boss2.fire_cooldown < boss1.fire_cooldown, "Темп стрільби боса має прискорюватись"

    # Тест фаз атак боса
    boss1.entered = True
    boss1.attack_mode = 0  # 5-променевий віяловий залп
    b_mode0 = boss1._execute_attack(player_pos=(200, 100))
    assert len(b_mode0) == 5

    boss1.attack_mode = 1  # Прицільний подвійний лазер
    b_mode1 = boss1._execute_attack(player_pos=(200, 100))
    assert len(b_mode1) == 2

    boss1.attack_mode = 2  # Плазмовий шквал з 3 гармат
    b_mode2 = boss1._execute_attack(player_pos=(200, 100))
    assert len(b_mode2) == 3

    print("[OK] Ескалація характеристик босів (HP, швидкість, темп, нагорода) та 3 патерни атак перевірено")


if __name__ == "__main__":
    test_player_upgrade_attributes()
    test_upgrades_pool_and_effects()
    test_upgrade_overlay_and_game_trigger()
    test_boss_and_enemy_types()
    print("\n=== ВСІ ТЕСТИ КАРТОК ПОКРАЩЕНЬ, ВОРОГІВ ТА БОСІВ ПРОЙШЛИ УСПІШНО! ===")
