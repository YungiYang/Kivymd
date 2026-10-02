"""Комплексне тестування систем крафту, нових кораблів, 9 біомів, перешкод, розширених ворогів та здібностей."""

import os
import sys

# Додаємо корінь проєкту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from game.materials import (
    MATERIALS_CATALOG,
    CRAFT_RECIPES,
    get_material,
    get_drop_table,
    roll_drops,
    can_craft,
    craft_ship,
)
from game.storage import (
    get_materials,
    add_material,
    remove_material,
    set_materials,
    get_crafted_ships,
    add_crafted_ship,
)
from game.biomes import BIOMES_CATALOG, ORDERED_BIOMES, get_biome_config
from game.ships import SHIPS_CATALOG, ORDERED_SHIP_IDS, CRAFT_ONLY_SHIPS, get_ship_config
from game.abilities import (
    PASSIVE_ABILITIES_CATALOG,
    ACTIVE_ABILITIES_CATALOG,
    PlayerAbilities,
    roll_passive_drop,
    roll_active_drop,
    get_passive_config,
    get_active_config,
)
from game.obstacles import Obstacle, spawn_obstacle, BIOME_OBSTACLES
from game.advanced_enemies import AdvancedEnemy, EliteBoss, spawn_enemy_for_biome
from game.entities import PlayerShip, Bullet


def test_materials_and_crafting():
    print("--- 1. Тестування матеріалів, дропів та крафту кораблів ---")
    assert len(MATERIALS_CATALOG) == 12, f"Очікувалось 12 матеріалів, знайдено {len(MATERIALS_CATALOG)}"
    assert "stellar_dust" in MATERIALS_CATALOG
    assert "plasma_core" in MATERIALS_CATALOG
    assert "void_essence" in MATERIALS_CATALOG

    # Перевірка 3 легендарних рецептів
    assert len(CRAFT_RECIPES) == 3
    assert "recipe_inferno_titan" in CRAFT_RECIPES
    assert "recipe_abyssal_leviathan" in CRAFT_RECIPES
    assert "recipe_void_phantom" in CRAFT_RECIPES

    # Перевірка логіки крафту
    inv = {"magma_shard": 3, "obsidian_plate": 2, "plasma_core": 1, "stellar_dust": 5}
    assert can_craft("recipe_inferno_titan", inv) is True
    assert can_craft("recipe_void_phantom", inv) is False

    success, new_inv = craft_ship("recipe_inferno_titan", inv)
    assert success is True
    assert new_inv.get("magma_shard", 0) == 0
    assert new_inv.get("stellar_dust", 0) == 0

    # Дропи з боса
    boss_drops = roll_drops("lava", is_boss=True, is_elite=True)
    assert isinstance(boss_drops, list)
    print(f"[OK] Матеріали та крафт: {len(MATERIALS_CATALOG)} матеріалів, 3 рецепти функціонують успішно")


def test_expanded_biomes():
    print("--- 2. Тестування 9 розширених біомів ---")
    assert len(BIOMES_CATALOG) >= 9, f"Очікувалось як мінімум 9 біомів, знайдено {len(BIOMES_CATALOG)}"
    expected = ["space", "lava", "water", "cyber_storm", "ice", "toxic", "gravity", "void", "nebula"]
    for b_id in expected:
        assert b_id in BIOMES_CATALOG, f"Біом {b_id} відсутній"
        cfg = get_biome_config(b_id)
        assert len(cfg.name) > 0
        assert len(cfg.bg_color) == 4

    # Перевірка нових небезпек
    assert get_biome_config("toxic").hazard_type == "toxin"
    assert get_biome_config("gravity").hazard_type == "gravity"
    assert get_biome_config("void").hazard_type == "dark"
    assert get_biome_config("nebula").hazard_type == "void"
    print(f"[OK] 9 біомів перевірено, унікальні небезпеки та палітри активні")


def test_expanded_ships_and_attacks():
    print("--- 3. Тестування 9 кораблів та нових видів атак ---")
    assert len(SHIPS_CATALOG) >= 9
    assert len(CRAFT_ONLY_SHIPS) == 3
    for s_id in CRAFT_ONLY_SHIPS:
        assert s_id in SHIPS_CATALOG

    # Корабель з ракетами «Нова»
    player_nova = PlayerShip(ship_id="nova_hunter")
    assert player_nova.attack_type == "missile"
    missiles = player_nova.shoot_bullets()
    assert len(missiles) > 0
    assert missiles[0].damage == player_nova.bullet_damage

    # Корабель з дуальним лазером «Тінь»
    player_shade = PlayerShip(ship_id="phantom_shade")
    assert player_shade.attack_type == "dual_beam"
    beams = player_shade.shoot_bullets()
    assert len(beams) == 2

    print(f"[OK] 9 кораблів (в т.ч. 3 крафтові), атаки missile та dual_beam працюють")


def test_obstacles_system():
    print("--- 4. Тестування перешкод (астероїди, осколки, міни, туманності) ---")
    for b_id in ORDERED_BIOMES:
        assert b_id in BIOME_OBSTACLES, f"Біом {b_id} не має таблиці перешкод"
        obs = spawn_obstacle(b_id, screen_width=420.0, screen_height=750.0)
        assert isinstance(obs, Obstacle)
        assert obs.hp > 0
        assert obs.contact_damage > 0
        # Оновлення руху
        initial_y = obs.y
        obs.update(0.1)
        assert obs.y != initial_y
        # Пошкодження та знищення
        obs.take_damage(99)
        assert obs.is_destroyed is True

    print("[OK] Система перешкод для всіх 9 біомів успішно перевірена")


def test_advanced_enemies_and_elite_boss():
    print("--- 5. Тестування розширених класів ворогів та елітного боса ---")
    # Перевірка спавнера для різних біомів
    for b_id in ORDERED_BIOMES:
        e = spawn_enemy_for_biome(x=150.0, y=700.0, biome_id=b_id, score=2500)
        assert e.hp > 0
        assert hasattr(e, "take_damage")
        assert hasattr(e, "update")

    # Перевірка дронів та splitter
    splitter = AdvancedEnemy(x=100.0, y=500.0, enemy_type="splitter", biome="space")
    assert splitter.enemy_type == "splitter"
    children = splitter.get_split_children()
    assert len(children) == 2
    assert children[0].enemy_type == "drone"

    # Перевірка EliteBoss з 4 фазами
    boss = EliteBoss(x=150.0, y=600.0, boss_level=5, biome="space")
    assert boss.max_hp >= 800
    assert boss.phase == 0
    # Зниження HP до 50% має перевести у фазу 2
    boss.take_damage(int(boss.max_hp * 0.55))
    boss.update(0.016, player_pos=(200, 100), screen_w=420, screen_h=750)
    assert boss.phase >= 2

    print("[OK] 8 класів ворогів, механіка splitter та 4 фази EliteBoss функціонують відмінно")


def test_abilities_system():
    print("--- 6. Тестування системи пасивних та активних здібностей ---")
    assert len(PASSIVE_ABILITIES_CATALOG) == 8
    assert len(ACTIVE_ABILITIES_CATALOG) == 8

    player = PlayerShip()
    ab = PlayerAbilities()

    # 1. Пасивна броня
    ab.add_passive("armor_plating")
    assert ab.get_armor_reduction() == 0.15

    # 2. Пасивний овердрайв
    ab.add_passive("overdrive_core")
    assert ab.get_damage_multiplier() == 1.20

    # 3. Активна здібність: Варп
    assert ab.add_active("warp_jump") is True
    assert ab.can_use_active("warp_jump") is True
    ab.use_active("warp_jump")
    assert ab.can_use_active("warp_jump") is False
    assert ab.get_active_cooldown_remaining("warp_jump") > 20.0

    # 4. Регенерація HP
    player.hp = 80
    ab.add_passive("regen_coil")
    # Симуляція спливання 3.1 сек
    ab.update(3.1, player)
    assert player.hp == 81

    # 5. Матриця Фенікса (Revive)
    ab.add_passive("phoenix_matrix")
    assert ab.phoenix_used is False

    print("[OK] Пасивні та активні здібності (8+8), таймери та баффи успішно перевірено")


if __name__ == "__main__":
    print("\n=== ЗАПУСК ПОВНОГО ТЕСТУВАННЯ КРАФТУ, ЗДІБНОСТЕЙ ТА 9 БІОМІВ ===")
    test_materials_and_crafting()
    test_expanded_biomes()
    test_expanded_ships_and_attacks()
    test_obstacles_system()
    test_advanced_enemies_and_elite_boss()
    test_abilities_system()
    print("\n=== ВСІ ТЕСТИ КРАФТУ, ЗДІБНОСТЕЙ ТА БІОМІВ УСПІШНО ПРОЙДЕНІ! ===")
