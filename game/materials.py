"""Модуль системи матеріалів та крафтингу для космічного шутера."""

import random
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Датаклас матеріалу
# ---------------------------------------------------------------------------

@dataclass
class Material:
    """Опис одного ресурсного матеріалу."""

    material_id: str
    """Унікальний ідентифікатор матеріалу."""

    name: str
    """Назва матеріалу (українська)."""

    icon: str
    """Emoji-іконка матеріалу."""

    rarity: str
    """Рідкісність: 'common', 'rare', 'epic', 'legendary'."""

    color: tuple
    """Колір RGBA у форматі (r, g, b, a)."""

    description: str
    """Короткий опис / де падає."""


# ---------------------------------------------------------------------------
# Каталог матеріалів
# ---------------------------------------------------------------------------

MATERIALS_CATALOG: dict[str, Material] = {
    "plasma_core": Material(
        material_id="plasma_core",
        name="Плазмове Ядро",
        icon="🔵",
        rarity="rare",
        color=(0.2, 0.7, 1.0, 1.0),
        description="Падає з космічних босів.",
    ),
    "magma_shard": Material(
        material_id="magma_shard",
        name="Магмовий Осколок",
        icon="🔥",
        rarity="rare",
        color=(1.0, 0.4, 0.05, 1.0),
        description="Падає з лавових босів.",
    ),
    "obsidian_plate": Material(
        material_id="obsidian_plate",
        name="Обсидіанова Плита",
        icon="⚫",
        rarity="epic",
        color=(0.25, 0.1, 0.2, 1.0),
        description="Падає з лавових босів.",
    ),
    "hydro_crystal": Material(
        material_id="hydro_crystal",
        name="Гідро-Кристал",
        icon="💎",
        rarity="rare",
        color=(0.1, 0.9, 0.8, 1.0),
        description="Падає з водних босів.",
    ),
    "abyss_membrane": Material(
        material_id="abyss_membrane",
        name="Оболонка Безодні",
        icon="🌊",
        rarity="epic",
        color=(0.05, 0.4, 0.6, 1.0),
        description="Падає з водних босів.",
    ),
    "thunder_coil": Material(
        material_id="thunder_coil",
        name="Грозова Котушка",
        icon="⚡",
        rarity="rare",
        color=(0.8, 0.3, 1.0, 1.0),
        description="Падає з кібер-босів.",
    ),
    "nano_chip": Material(
        material_id="nano_chip",
        name="Нано-Чіп",
        icon="💜",
        rarity="epic",
        color=(0.6, 0.2, 1.0, 1.0),
        description="Падає з кібер-босів.",
    ),
    "cryo_fragment": Material(
        material_id="cryo_fragment",
        name="Кріо-Фрагмент",
        icon="❄️",
        rarity="rare",
        color=(0.5, 0.9, 1.0, 1.0),
        description="Падає з льодових босів.",
    ),
    "void_essence": Material(
        material_id="void_essence",
        name="Есенція Пустоти",
        icon="🌌",
        rarity="legendary",
        color=(0.4, 0.1, 0.6, 1.0),
        description="Падає з елітних босів.",
    ),
    "quantum_alloy": Material(
        material_id="quantum_alloy",
        name="Квантовий Сплав",
        icon="✨",
        rarity="legendary",
        color=(1.0, 0.85, 0.2, 1.0),
        description="Падає з елітних босів.",
    ),
    "dark_matter": Material(
        material_id="dark_matter",
        name="Темна Матерія",
        icon="🖤",
        rarity="legendary",
        color=(0.15, 0.05, 0.25, 1.0),
        description="Падає з елітних босів.",
    ),
    "stellar_dust": Material(
        material_id="stellar_dust",
        name="Зоряний Пил",
        icon="⭐",
        rarity="common",
        color=(0.9, 0.85, 0.6, 1.0),
        description="Падає з будь-якого ворога.",
    ),
}


# ---------------------------------------------------------------------------
# Датаклас рецепту крафтингу
# ---------------------------------------------------------------------------

@dataclass
class CraftRecipe:
    """Рецепт крафтингу корабля."""

    recipe_id: str
    """Унікальний ідентифікатор рецепту."""

    ship_id: str
    """Ідентифікатор корабля, який розблоковується."""

    name: str
    """Назва корабля (українська)."""

    icon: str
    """Emoji-іконка корабля."""

    description: str
    """Опис корабля."""

    materials_required: dict[str, int]
    """Словник {material_id: кількість}, необхідна для крафтингу."""

    rarity: str
    """Рідкісність рецепту: 'epic' або 'legendary'."""


# ---------------------------------------------------------------------------
# Каталог рецептів крафтингу
# ---------------------------------------------------------------------------

CRAFT_RECIPES: dict[str, CraftRecipe] = {
    "recipe_inferno_titan": CraftRecipe(
        recipe_id="recipe_inferno_titan",
        ship_id="inferno_titan",
        name="ІНФЕРНО-ТИТАН",
        icon="🌋",
        description="Легендарний дредноут із надр Магма-9",
        materials_required={
            "magma_shard": 3,
            "obsidian_plate": 2,
            "plasma_core": 1,
            "stellar_dust": 5,
        },
        rarity="legendary",
    ),
    "recipe_abyssal_leviathan": CraftRecipe(
        recipe_id="recipe_abyssal_leviathan",
        ship_id="abyssal_leviathan",
        name="ЛЕВІАФАН БЕЗОДНІ",
        icon="🐋",
        description="Елітний глибоководний лінкор",
        materials_required={
            "hydro_crystal": 3,
            "abyss_membrane": 2,
            "cryo_fragment": 2,
            "stellar_dust": 5,
        },
        rarity="legendary",
    ),
    "recipe_void_phantom": CraftRecipe(
        recipe_id="recipe_void_phantom",
        ship_id="void_phantom",
        name="ФАНТОМ ПУСТОТИ",
        icon="👁️",
        description="Найрідкісніший корабель у всесвіті",
        materials_required={
            "void_essence": 2,
            "quantum_alloy": 2,
            "dark_matter": 1,
            "thunder_coil": 2,
            "nano_chip": 1,
        },
        rarity="legendary",
    ),
}


# ---------------------------------------------------------------------------
# Внутрішні таблиці дропу за біомами (для регулярних ворогів та босів)
# ---------------------------------------------------------------------------

# Формат: {biome_id: {"boss_specific": [material_id, ...], "rare": [material_id, ...]}}
_BIOME_DROPS: dict[str, dict[str, list[str]]] = {
    "space": {
        "boss_specific": ["plasma_core"],
        "rare": ["stellar_dust"],
    },
    "magma": {
        "boss_specific": ["magma_shard", "obsidian_plate"],
        "rare": ["stellar_dust"],
    },
    "water": {
        "boss_specific": ["hydro_crystal", "abyss_membrane"],
        "rare": ["stellar_dust"],
    },
    "cyber": {
        "boss_specific": ["thunder_coil", "nano_chip"],
        "rare": ["stellar_dust"],
    },
    "ice": {
        "boss_specific": ["cryo_fragment"],
        "rare": ["stellar_dust"],
    },
}

# Легендарні матеріали (доступні з елітних босів)
_LEGENDARY_MATERIALS: list[str] = ["void_essence", "quantum_alloy", "dark_matter"]


# ---------------------------------------------------------------------------
# Публічні функції
# ---------------------------------------------------------------------------

def get_material(material_id: str) -> Material:
    """Повертає об'єкт Material за ідентифікатором.

    Args:
        material_id: Ідентифікатор матеріалу.

    Returns:
        Відповідний об'єкт :class:`Material`.

    Raises:
        KeyError: Якщо матеріал з таким ідентифікатором не існує.
    """
    if material_id not in MATERIALS_CATALOG:
        raise KeyError(f"Матеріал '{material_id}' не знайдено в каталозі.")
    return MATERIALS_CATALOG[material_id]


def get_drop_table(biome_id: str, is_boss: bool = False) -> list[tuple[str, float]]:
    """Повертає таблицю дропу матеріалів для заданого біому.

    Args:
        biome_id: Ідентифікатор біому (наприклад, 'magma', 'water').
        is_boss: True, якщо ворог є босом — збільшує шанси дропу.

    Returns:
        Список пар (material_id, шанс_дропу).
    """
    # Завжди є шанс отримати зоряний пил
    table: list[tuple[str, float]] = [("stellar_dust", 0.70 if is_boss else 0.25)]

    biome_info = _BIOME_DROPS.get(biome_id, {})

    if is_boss:
        # Специфічні матеріали біому — найвищий шанс для босів
        for mat_id in biome_info.get("boss_specific", []):
            mat = MATERIALS_CATALOG.get(mat_id)
            if mat is None:
                continue
            if mat.rarity == "epic":
                table.append((mat_id, 0.35))
            else:
                table.append((mat_id, 0.50))

        # Рідкісні матеріали з невеликим шансом
        for mat_id in biome_info.get("rare", []):
            if mat_id == "stellar_dust":
                continue  # вже додано вище
            table.append((mat_id, 0.20))

        # Легендарні матеріали — мінімальний шанс
        for mat_id in _LEGENDARY_MATERIALS:
            table.append((mat_id, 0.05))

    return table


def roll_drops(
    biome_id: str,
    is_boss: bool = False,
    is_elite: bool = False,
) -> list[str]:
    """Виконує кидки по таблиці дропу та повертає список матеріалів.

    Для звичайних ворогів повертає 0–1 предмет.
    Для босів — 0–3 предмети.
    Для елітних босів — підвищений шанс (0.20) на легендарні матеріали.

    Args:
        biome_id: Ідентифікатор біому.
        is_boss: True, якщо ворог є босом.
        is_elite: True, якщо ворог є елітним босом (перекриває is_boss).

    Returns:
        Список ідентифікаторів матеріалів, що випали.
    """
    if is_elite:
        is_boss = True

    table = get_drop_table(biome_id, is_boss=is_boss)

    # Для елітних босів підвищуємо шанс легендарних матеріалів
    if is_elite:
        table = [
            (mat_id, 0.20 if mat_id in _LEGENDARY_MATERIALS else chance)
            for mat_id, chance in table
        ]

    dropped: list[str] = []
    max_drops = 3 if is_boss else 1

    for mat_id, chance in table:
        if len(dropped) >= max_drops:
            break
        if random.random() < chance:
            dropped.append(mat_id)

    return dropped


def can_craft(recipe_id: str, inventory: dict[str, int]) -> bool:
    """Перевіряє, чи є у гравця достатньо матеріалів для крафтингу.

    Args:
        recipe_id: Ідентифікатор рецепту.
        inventory: Поточний інвентар {material_id: кількість}.

    Returns:
        True, якщо всі необхідні матеріали є в достатній кількості.

    Raises:
        KeyError: Якщо рецепт не існує.
    """
    if recipe_id not in CRAFT_RECIPES:
        raise KeyError(f"Рецепт '{recipe_id}' не знайдено.")
    recipe = CRAFT_RECIPES[recipe_id]
    for mat_id, required in recipe.materials_required.items():
        if inventory.get(mat_id, 0) < required:
            return False
    return True


def craft_ship(
    recipe_id: str,
    inventory: dict[str, int],
) -> tuple[bool, dict[str, int]]:
    """Виконує крафтинг корабля, списуючи матеріали з інвентаря.

    Args:
        recipe_id: Ідентифікатор рецепту.
        inventory: Поточний інвентар {material_id: кількість}.

    Returns:
        Кортеж (успіх, оновлений_інвентар).
        Якщо матеріалів недостатньо — повертає (False, незмінений_інвентар).

    Raises:
        KeyError: Якщо рецепт не існує.
    """
    if not can_craft(recipe_id, inventory):
        return False, inventory

    recipe = CRAFT_RECIPES[recipe_id]
    # Копіюємо інвентар, щоб не змінювати оригінал
    updated = dict(inventory)
    for mat_id, required in recipe.materials_required.items():
        updated[mat_id] = updated.get(mat_id, 0) - required
        # Видаляємо запис, якщо кількість стала нульовою
        if updated[mat_id] <= 0:
            del updated[mat_id]
    return True, updated
