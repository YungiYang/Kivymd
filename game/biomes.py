"""Модуль визначення біомів (рівнів) для Galaxy Defender."""

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class BiomeConfig:
    """Конфігурація унікального біому (ігрового рівня)."""

    biome_id: str
    name: str
    icon: str
    subtitle: str
    hazard_type: str  # "none", "burn", "slow", "emp", "freeze", "toxin", "gravity", "dark", "void"
    hazard_text: str
    bg_color: tuple
    particle_type: str  # "stars", "embers", "bubbles", "cyber", "snow", "spores", "debris", "shadows", "void_ripples"
    primary_color: tuple
    accent_color: tuple
    bullet_color: tuple


BIOMES_CATALOG: dict[str, BiomeConfig] = {
    "space": BiomeConfig(
        biome_id="space",
        name="ГЛИБОКИЙ КОСМОС",
        icon="🌌",
        subtitle="Сектор Альфа: Зоряне Скупчення",
        hazard_type="none",
        hazard_text="Стандартні космічні умови.",
        bg_color=(0.02, 0.03, 0.08, 1.0),
        particle_type="stars",
        primary_color=(0.15, 0.25, 0.5),
        accent_color=(0.2, 0.85, 1.0, 1.0),
        bullet_color=(1.0, 0.2, 0.35, 1.0),
    ),
    "lava": BiomeConfig(
        biome_id="lava",
        name="ЛАВОВЕ ПЕКЛО",
        icon="🔥",
        subtitle="Вулканічні Надра Планети Магма-9",
        hazard_type="burn",
        hazard_text="Ворожі атаки підпалюють корабель (періодична DoT-шкода)!",
        bg_color=(0.12, 0.02, 0.02, 1.0),
        particle_type="embers",
        primary_color=(0.55, 0.12, 0.05),
        accent_color=(1.0, 0.45, 0.1, 1.0),
        bullet_color=(1.0, 0.35, 0.05, 1.0),
    ),
    "water": BiomeConfig(
        biome_id="water",
        name="ОКЕАНІЧНА БЕЗОДНЯ",
        icon="🌊",
        subtitle="Абісальні Глибини Водної Планети",
        hazard_type="slow",
        hazard_text="Гідро-торпеди сповільнюють маневреність корабля на 35%!",
        bg_color=(0.01, 0.07, 0.14, 1.0),
        particle_type="bubbles",
        primary_color=(0.05, 0.35, 0.45),
        accent_color=(0.1, 0.95, 0.8, 1.0),
        bullet_color=(0.15, 0.85, 0.95, 1.0),
    ),
    "cyber_storm": BiomeConfig(
        biome_id="cyber_storm",
        name="ЕЛЕКТРОМАГНІТНА БУРЯ",
        icon="⚡",
        subtitle="Кібер-Зона Високої Напруги",
        hazard_type="emp",
        hazard_text="EMP-розряди збивають енергетичний щит та системи стрільби!",
        bg_color=(0.07, 0.02, 0.12, 1.0),
        particle_type="cyber",
        primary_color=(0.45, 0.08, 0.45),
        accent_color=(0.85, 0.25, 1.0, 1.0),
        bullet_color=(0.85, 0.2, 1.0, 1.0),
    ),
    "ice": BiomeConfig(
        biome_id="ice",
        name="КРИЖАНА ПУСТКА",
        icon="❄️",
        subtitle="Кріогенний Пояс Вічної Мерзлоти",
        hazard_type="freeze",
        hazard_text="Крижані осколки заморожують сопла двигунів!",
        bg_color=(0.02, 0.06, 0.13, 1.0),
        particle_type="snow",
        primary_color=(0.1, 0.3, 0.5),
        accent_color=(0.4, 0.9, 1.0, 1.0),
        bullet_color=(0.5, 0.9, 1.0, 1.0),
    ),
}

# ---------------------------------------------------------------------------
# Додаткові біоми: токсичний, гравітаційний, порожнеча, небула
# ---------------------------------------------------------------------------

BIOMES_CATALOG["toxic"] = BiomeConfig(
    biome_id="toxic",
    name="ТОКСИЧНА ТУМАННІСТЬ",
    icon="☠️",
    subtitle="Отруйні Хмари Небули Мортіс",
    hazard_type="toxin",
    hazard_text="Токсичні спори поступово отруюють корабель (повільний DoT + зниження видимості)!",
    bg_color=(0.04, 0.10, 0.04, 1.0),
    particle_type="spores",
    primary_color=(0.15, 0.45, 0.10),
    accent_color=(0.4, 1.0, 0.2, 1.0),
    bullet_color=(0.35, 1.0, 0.1, 1.0),
)

BIOMES_CATALOG["gravity"] = BiomeConfig(
    biome_id="gravity",
    name="ГРАВІТАЦІЙНИЙ КОЛАПС",
    icon="🌀",
    subtitle="Зона Викривлення Простору-Часу",
    hazard_type="gravity",
    hazard_text="Аномальна гравітація тягне корабель вниз та викривляє траєкторії снарядів!",
    bg_color=(0.03, 0.02, 0.10, 1.0),
    particle_type="debris",
    primary_color=(0.30, 0.15, 0.55),
    accent_color=(0.7, 0.5, 1.0, 1.0),
    bullet_color=(0.8, 0.6, 1.0, 1.0),
)

BIOMES_CATALOG["void"] = BiomeConfig(
    biome_id="void",
    name="ПОРОЖНЕЧА ТЬМИ",
    icon="🕳️",
    subtitle="Провал між Вимірами: Нульова Зона",
    hazard_type="dark",
    hazard_text="Тьма поглинає щит та послаблює зброю. Вороги невидимі до наближення!",
    bg_color=(0.01, 0.01, 0.02, 1.0),
    particle_type="shadows",
    primary_color=(0.10, 0.05, 0.20),
    accent_color=(0.5, 0.15, 0.75, 1.0),
    bullet_color=(0.6, 0.2, 0.9, 1.0),
)

BIOMES_CATALOG["nebula"] = BiomeConfig(
    biome_id="nebula",
    name="ЗОРЯНА НЕБУЛА",
    icon="🌸",
    subtitle="Квітуче Скупчення Міжзоряних Газових Хмар",
    hazard_type="void",
    hazard_text="Небула розсіює лазери - шкода по ворогах знижена на 25%, але ворог теж уражений!",
    bg_color=(0.08, 0.03, 0.12, 1.0),
    particle_type="void_ripples",
    primary_color=(0.45, 0.10, 0.45),
    accent_color=(1.0, 0.4, 0.9, 1.0),
    bullet_color=(1.0, 0.3, 0.8, 1.0),
)

ORDERED_BIOMES = ["space", "lava", "water", "cyber_storm", "ice", "toxic", "gravity", "void", "nebula"]
OTHER_BIOMES = ["lava", "water", "cyber_storm", "ice", "toxic", "gravity", "void", "nebula"]


def get_biome_config(biome_id: str) -> BiomeConfig:
    """Повертає конфігурацію вказаного біому (за замовчуванням 'space')."""
    return BIOMES_CATALOG.get(biome_id, BIOMES_CATALOG["space"])


def get_next_random_biome(current_biome_id: str, visited_biomes: list[str] = None) -> str:
    """Обирає випадковий новий біом після поточного рівня.
    
    Пріоритет віддається біомам, які ще не відвідувались у поточній грі.
    """
    if visited_biomes is None:
        visited_biomes = []

    candidates = [b for b in ORDERED_BIOMES if b != current_biome_id and b not in visited_biomes]
    if not candidates:
        # Якщо всі біоми вже відвідані — обираємо будь-який відмінний від поточного
        candidates = [b for b in ORDERED_BIOMES if b != current_biome_id]

    return random.choice(candidates) if candidates else "space"
