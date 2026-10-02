"""Тестування системи 5 біомів, елементальних атак, статусних ефектів та аудіо."""

import os
import sys

# Додаємо корінь проєкту до sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game.biomes import (
    BIOMES_CATALOG,
    get_biome_config,
    get_next_random_biome,
    BiomeConfig,
)
from game.entities import PlayerShip, Bullet, Enemy, Boss
from game.background import ParallaxBackground
from game.audio import AudioManager


def test_biomes_catalog():
    print("--- 1. Тестування каталогу 5 біомів та випадкового вибору ---")
    assert len(BIOMES_CATALOG) >= 5, f"Очікувалось щонайменше 5 біомів, отримано {len(BIOMES_CATALOG)}"
    expected_biomes = ["space", "lava", "water", "cyber_storm", "ice"]
    for b_id in expected_biomes:
        assert b_id in BIOMES_CATALOG, f"Біом {b_id} відсутній у каталозі"
        cfg = get_biome_config(b_id)
        assert isinstance(cfg, BiomeConfig)
        assert len(cfg.name) > 0
        assert len(cfg.bg_color) == 4
        assert cfg.particle_type in ["stars", "embers", "bubbles", "cyber", "snow"]

    # Перевірка небезпек біомів
    assert get_biome_config("space").hazard_type == "none"
    assert get_biome_config("lava").hazard_type == "burn"
    assert get_biome_config("water").hazard_type == "slow"
    assert get_biome_config("cyber_storm").hazard_type == "emp"
    assert get_biome_config("ice").hazard_type == "freeze"

    # Перевірка get_next_random_biome: не повертає той самий біом
    for b_id in expected_biomes:
        for _ in range(15):
            nxt = get_next_random_biome(b_id)
            assert nxt != b_id, f"get_next_random_biome повернув той самий біом {b_id}"
            assert nxt in BIOMES_CATALOG

    print("[OK] Всі 5 біомів коректно налаштовані, випадкова зміна без повторів працює!")


def test_player_status_effects():
    print("--- 2. Тестування статусних ефектів гравця (Підпал DoT, Сповільнення, Заморозка, EMP) ---")
    player = PlayerShip()
    assert player.hp == 100
    assert not player.is_burning
    assert not player.is_slowed
    assert not player.is_emp
    assert not player.is_frozen

    # 1. Підпал (Lava Burn DoT)
    player.apply_burn(duration=3.0)
    assert player.is_burning is True
    assert player.burn_timer == 3.0

    # Оновлення гравця на 0.51с повинно завдати 2 шкоди від DoT
    initial_hp = player.hp
    player.update(0.51, 420.0)
    assert player.hp == initial_hp - 2, f"Шкода від підпалу не завдана: HP={player.hp}"

    # 2. Сповільнення (Water Slow)
    base_speed = player.speed
    player.apply_slow(duration=2.5)
    assert player.is_slowed is True

    # 3. EMP Шок
    player.apply_emp(duration=1.8)
    assert player.is_emp is True

    # 4. Крижана заморозка (Ice Freeze)
    player.apply_freeze(duration=2.0)
    assert player.is_frozen is True

    # Очищення всіх статусів
    player.clear_status_effects()
    assert player.is_burning is False
    assert player.is_slowed is False
    assert player.is_emp is False
    assert player.is_frozen is False
    assert len(player.burn_particles) == 0

    print("[OK] Статусні ефекти, DoT-шкода від підпалу та зняття ефектів працюють відмінно!")


def test_elemental_bullets_and_enemies():
    print("--- 3. Тестування елементальних снарядів та поведінки ворогів у біомах ---")
    # Куля з підпалом
    b_fire = Bullet(x=100, y=200, is_player=False, hazard_type="burn")
    assert b_fire.hazard_type == "burn"

    # Куля зі сповільненням
    b_water = Bullet(x=100, y=200, is_player=False, hazard_type="slow")
    assert b_water.hazard_type == "slow"

    # Ворог у лавовому біомі
    enemy_lava = Enemy(x=150, y=600, biome="lava")
    assert enemy_lava.biome == "lava"
    assert enemy_lava.hazard_type == "burn"
    bullets_lava = enemy_lava.shoot()
    assert len(bullets_lava) > 0
    assert bullets_lava[0].hazard_type == "burn", "Снаряд ворога в лавовому біомі повинен мати ефект burn"

    # Ворог у водяному біомі
    enemy_water = Enemy(x=150, y=600, biome="water")
    assert enemy_water.hazard_type == "slow"
    bullets_water = enemy_water.shoot()
    assert len(bullets_water) > 0
    assert bullets_water[0].hazard_type == "slow"

    # Бос у кібер-біомі
    boss_cyber = Boss(x=150, y=600, biome="cyber_storm")
    assert boss_cyber.biome == "cyber_storm"
    assert boss_cyber.hazard_type == "emp"
    bullets_boss = boss_cyber.shoot_fan()
    assert len(bullets_boss) > 0
    assert bullets_boss[0].hazard_type == "emp"

    print("[OK] Вороги та боси коректно стріляють елементальними снарядами відповідного біому!")


def test_parallax_background_warp():
    print("--- 4. Тестування перемикання біомів у ParallaxBackground та ефекту гіперстрибка ---")
    bg = ParallaxBackground(size=(420, 750))
    bg.set_biome("lava", trigger_warp=True)
    assert bg.current_biome_id == "lava"
    assert bg.warp_active is True
    assert bg.warp_timer == 1.4
    assert len(bg.particles) > 0

    # Симуляція руху під час гіперстрибка
    bg.update(0.7)
    assert bg.warp_active is True
    assert bg.warp_timer < 1.4

    # Завершення гіперстрибка
    bg.update(1.0)
    assert bg.warp_active is False
    assert bg.warp_timer <= 0.0

    print("[OK] Паралакс-фон безшовно перемикає біоми та успішно запускає ефект гіперстрибка!")


def test_audio_assets_and_biomes():
    print("--- 5. Тестування наявності та відтворення аудіо для біомів та файлів з папки звуки ---")
    # Перевірка наявності наданих користувачем файлів у папці звуки/
    user_sound_dir = os.path.join(os.path.dirname(__file__), "..", "звуки")
    bgm_file = os.path.join(user_sound_dir, "kulakovka-space-283176.mp3")
    sfx_file = os.path.join(user_sound_dir, "zvuk-vystrela-iz-lazera_[Pro-Sound.org].mp3")

    assert os.path.isfile(bgm_file), f"Файл {bgm_file} не знайдено в папці звуки"
    assert os.path.isfile(sfx_file), f"Файл {sfx_file} не знайдено в папці звуки"

    # Перевірка наявності згенерованих біомних аудіо файлів
    audio_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")
    required_wavs = [
        "burn.wav", "freeze.wav", "shock.wav", "splash.wav", "warp.wav",
        "bgm_lava.wav", "bgm_water.wav", "bgm_cyber.wav", "bgm_ice.wav",
    ]
    for w in required_wavs:
        path = os.path.join(audio_dir, w)
        assert os.path.isfile(path), f"Аудіо-файл {w} відсутній у {audio_dir}"

    audio_mgr = AudioManager()
    audio_mgr.load_sounds()

    # Перевірка методу перемикання музики біомів
    for b_id in ["space", "lava", "water", "cyber_storm", "ice"]:
        audio_mgr.play_biome_music(b_id)
        assert audio_mgr.current_bgm_track == b_id

    audio_mgr.stop_music()
    print("[OK] Аудіо-ассети з папки 'звуки' та біомні саундтреки/звуки успішно завантажені!")


if __name__ == "__main__":
    print("\n=== ПОЧАТОК ТЕСТУВАННЯ СИСТЕМИ БІОМІВ ТА НЕБЕЗПЕК ===")
    test_biomes_catalog()
    test_player_status_effects()
    test_elemental_bullets_and_enemies()
    test_parallax_background_warp()
    test_audio_assets_and_biomes()
    print("\n=== ВСІ ТЕСТИ БІОМІВ ТА НЕБЕЗПЕК УСПІШНО ПРОЙДЕНІ! ===")
