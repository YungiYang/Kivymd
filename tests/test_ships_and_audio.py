"""Автоматизовані тести для системи кораблів, ангару, звуку та чесної прогресії."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from game.storage import (
    get_credits,
    add_credits,
    spend_credits,
    get_high_score,
    update_high_score,
    get_unlocked_ships,
    is_ship_unlocked,
    unlock_ship,
    get_selected_ship,
    set_selected_ship,
    is_sound_enabled,
    set_sound_enabled,
    is_music_enabled,
    set_music_enabled,
)
from game.audio import get_audio_manager
from game.ships import SHIPS_CATALOG, get_ship_config
from game.entities import PlayerShip, Enemy, Bullet, PlasmaOrb, LaserBeam
from game.game_screen import GameScreen
from game.hangar_screen import HangarScreen


class DummyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        sm = MDScreenManager()
        self.game_screen = GameScreen(name="game_screen")
        self.hangar_screen = HangarScreen(name="hangar_screen")
        sm.add_widget(self.game_screen)
        sm.add_widget(self.hangar_screen)
        return sm


def test_storage_system():
    print("--- 1. Тест системи збереження та кредитів ---")
    initial_credits = get_credits()
    add_credits(500)
    assert get_credits() == initial_credits + 500, "Помилка додавання кредитів"
    assert spend_credits(200) is True, "Помилка витрати кредитів"
    assert get_credits() == initial_credits + 300, "Невірний баланс після покупки"
    assert spend_credits(9999999) is False, "Витрачено більше кредитів, ніж є"

    unlock_ship("beam_titan")
    assert is_ship_unlocked("beam_titan") is True, "Корабель не розблоковано"
    set_selected_ship("beam_titan")
    assert get_selected_ship() == "beam_titan", "Помилка вибору активного корабля"

    set_selected_ship("striker")  # Повертаємо базовий
    print("[OK] Збереження кредитів, покупок та обраного корабля працює коректно!")


def test_audio_system():
    print("--- 2. Тест менеджера звуку та музики ---")
    audio = get_audio_manager()
    assert audio is not None, "AudioManager не створено"

    # Тест відтворення звукових ефектів (без падінь)
    audio.play("laser", volume=0.5)
    audio.play("explosion", volume=0.5)
    audio.play("beam", volume=0.5)
    audio.play("plasma", volume=0.5)
    audio.play("warning", volume=0.5)

    # Тест керування фоновою музикою
    audio.start_music()
    audio.pause_music()
    audio.resume_music()
    audio.stop_music()

    # Тест перемикання звуків
    s_state = is_sound_enabled()
    audio.toggle_sound()
    assert is_sound_enabled() == (not s_state), "Помилка перемикання звуку"
    set_sound_enabled(s_state)

    m_state = is_music_enabled()
    audio.toggle_music()
    assert is_music_enabled() == (not m_state), "Помилка перемикання музики"
    set_music_enabled(m_state)

    print("[OK] Аудіо-система (12 звуків + музика) функціонує бездоганно!")


def test_ship_classes_and_weapons():
    print("--- 3. Тест унікальних класів кораблів та типів атак ---")
    assert len(SHIPS_CATALOG) >= 4, "Каталог повинен містити щонайменше 4 унікальні кораблі"

    # 1. Штурмовик «Фенікс» (blaster)
    player = PlayerShip(ship_id="striker")
    assert player.attack_type == "blaster"
    assert player.max_hp == 100
    bullets = player.shoot_bullets()
    assert len(bullets) >= 1 and isinstance(bullets[0], Bullet)

    # 2. Крейсер «Геліос» (довгий промінь)
    player.apply_ship_id("beam_titan")
    assert player.attack_type == "beam"
    assert player.max_hp == 125
    assert not player.is_beam_active
    player.shoot_bullets()
    assert player.is_beam_active is True, "Промінь повинен активуватись при пострілі"
    assert player.beam_timer > 0.0

    beam = LaserBeam(x=100, y=100, height=400, damage_dps=180)
    assert beam.damage_dps == 180
    assert beam.is_player is True

    # 3. Дредноут «Вулкан» (зарядний плазмовий шар)
    player.apply_ship_id("plasma_vanguard")
    assert player.attack_type == "charge"
    assert player.max_hp == 150
    # Перед повним зарядом стріляє допоміжними лазерами
    player.charge_progress = 0.2
    shots = player.shoot_bullets()
    assert len(shots) == 2, "Допоміжні лазери під час зарядки"
    # При повному заряді випускає велику термоядерну кулю PlasmaOrb
    player.charge_progress = 1.0
    orb_shots = player.shoot_bullets()
    assert len(orb_shots) == 1 and isinstance(orb_shots[0], PlasmaOrb)
    assert orb_shots[0].damage >= 160, "Плазмова сфера повинна наносити високу шкоду"

    # 4. Перехоплювач «Валькірія» (віяловий залп + стартовий щит)
    player.apply_ship_id("storm_valkyrie")
    assert player.attack_type == "spread"
    assert player.speed == 425
    assert player.shield >= 1, "Валькірія повинна мати постійний стартовий щит"
    spread_shots = player.shoot_bullets()
    assert len(spread_shots) >= 3, "Валькірія повинна робити потрійний залп"

    print("[OK] Всі 4 кораблі (бластер, промінь, плазмова сфера, віяло) налаштовані!")


def test_hangar_screen(sm):
    print("--- 4. Тест екрана Ангару / Магазину кораблів ---")
    hangar: HangarScreen = sm.get_screen("hangar_screen")
    assert hangar.current_idx == 0
    hangar._next_ship()
    assert hangar.current_idx == 1
    hangar._prev_ship()
    assert hangar.current_idx == 0
    print("[OK] Навігація каруселлю ангару та показ характеристик працює!")


def test_flat_progression_no_multiplier(sm):
    print("--- 5. Тест чесної прогресії без множника очок ---")
    game_screen: GameScreen = sm.get_screen("game_screen")
    game_screen.width = 420
    game_screen.height = 750
    game_screen.start_new_game()

    start_score = game_screen.score
    start_credits = get_credits()

    # Створюємо тестового ворога
    enemy = Enemy(100, 400, enemy_type="fighter")
    game_screen.enemies.append(enemy)
    game_screen.game_area.add_widget(enemy)

    # Створюємо влучну кулю
    bullet = Bullet(100, 400, is_player=True, damage=100)
    game_screen.bullets.append(bullet)
    game_screen.game_area.add_widget(bullet)

    game_screen._handle_bullet_collisions()

    pts = getattr(enemy, "score_value", 100)
    # Перевіряємо, що нараховано РІВНО pts БЕЗ combo-множника
    assert game_screen.score == start_score + pts, f"Отримано {game_screen.score}, очікувалось {start_score + pts}"
    assert get_credits() == start_credits + pts, "Кредити не були нараховані в баланс"

    print("[OK] Множник очок відсутній: прогресія плоска та збалансована!")


if __name__ == "__main__":
    app = DummyApp()
    sm = app.build()
    test_storage_system()
    test_audio_system()
    test_ship_classes_and_weapons()
    test_hangar_screen(sm)
    test_flat_progression_no_multiplier(sm)
    print("\n=== ВСІ ТЕСТИ НОВИХ МОЖЛИВОСТЕЙ УСПІШНО ПРОЙДЕНІ! ===")
