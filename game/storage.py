"""Модуль для локального збереження очок, рекордів та куплених кораблів."""

import os
import json

SAVE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "save_data.json")

DEFAULT_DATA = {
    "credits": 0,
    "high_score": 0,
    "unlocked_ships": ["striker"],
    "selected_ship": "striker",
    "sound_enabled": True,
    "music_enabled": True,
    "materials": {},
    "crafted_ships": [],
}

_cache = None


def _load_data() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _cache = {**DEFAULT_DATA, **data}
                return _cache
        except Exception:
            pass
    _cache = dict(DEFAULT_DATA)
    return _cache


def _save_data():
    global _cache
    if _cache is None:
        _cache = dict(DEFAULT_DATA)
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def get_credits() -> int:
    return _load_data().get("credits", 0)


def add_credits(amount: int) -> int:
    if amount <= 0:
        return get_credits()
    data = _load_data()
    data["credits"] = data.get("credits", 0) + amount
    _save_data()
    return data["credits"]


def spend_credits(amount: int) -> bool:
    data = _load_data()
    current = data.get("credits", 0)
    if current >= amount:
        data["credits"] = current - amount
        _save_data()
        return True
    return False


def get_high_score() -> int:
    return _load_data().get("high_score", 0)


def update_high_score(score: int) -> bool:
    data = _load_data()
    if score > data.get("high_score", 0):
        data["high_score"] = score
        _save_data()
        return True
    return False


def get_unlocked_ships() -> list[str]:
    data = _load_data()
    return data.get("unlocked_ships", ["striker"])


def is_ship_unlocked(ship_id: str) -> bool:
    return ship_id in get_unlocked_ships()


def unlock_ship(ship_id: str) -> bool:
    data = _load_data()
    unlocked = data.setdefault("unlocked_ships", ["striker"])
    if ship_id not in unlocked:
        unlocked.append(ship_id)
        _save_data()
        return True
    return False


def get_selected_ship() -> str:
    return _load_data().get("selected_ship", "striker")


def set_selected_ship(ship_id: str):
    data = _load_data()
    data["selected_ship"] = ship_id
    _save_data()


def is_sound_enabled() -> bool:
    return _load_data().get("sound_enabled", True)


def set_sound_enabled(enabled: bool):
    data = _load_data()
    data["sound_enabled"] = bool(enabled)
    _save_data()


def is_music_enabled() -> bool:
    return _load_data().get("music_enabled", True)


def set_music_enabled(enabled: bool):
    data = _load_data()
    data["music_enabled"] = bool(enabled)
    _save_data()


# ---------------------------------------------------------------------------
# Функції управління матеріалами
# ---------------------------------------------------------------------------

def get_materials() -> dict[str, int]:
    """Повертає поточний інвентар матеріалів {material_id: кількість}."""
    return _load_data().get("materials", {})


def get_all_materials() -> dict[str, int]:
    """Аліас для :func:`get_materials`."""
    return get_materials()


def set_materials(materials: dict[str, int]):
    """Зберігає словник матеріалів у файл збереження.

    Args:
        materials: Новий словник {material_id: кількість}.
    """
    data = _load_data()
    data["materials"] = materials
    _save_data()


def add_material(material_id: str, count: int = 1):
    """Додає вказану кількість матеріалу до інвентаря.

    Args:
        material_id: Ідентифікатор матеріалу.
        count: Кількість, яку потрібно додати (за замовчуванням 1).
    """
    data = _load_data()
    materials: dict[str, int] = data.setdefault("materials", {})
    materials[material_id] = materials.get(material_id, 0) + count
    _save_data()


def remove_material(material_id: str, count: int):
    """Знімає вказану кількість матеріалу з інвентаря.

    Якщо кількість стає нульовою або від'ємною — запис видаляється.

    Args:
        material_id: Ідентифікатор матеріалу.
        count: Кількість, яку потрібно списати.
    """
    data = _load_data()
    materials: dict[str, int] = data.setdefault("materials", {})
    current = materials.get(material_id, 0)
    remaining = current - count
    if remaining <= 0:
        materials.pop(material_id, None)
    else:
        materials[material_id] = remaining
    _save_data()


# ---------------------------------------------------------------------------
# Функції управління виготовленими кораблями
# ---------------------------------------------------------------------------

def get_crafted_ships() -> list[str]:
    """Повертає список ідентифікаторів кораблів, виготовлених крафтингом."""
    return _load_data().get("crafted_ships", [])


def add_crafted_ship(ship_id: str):
    """Додає корабель до списку виготовлених, якщо його ще немає.

    Args:
        ship_id: Ідентифікатор корабля.
    """
    data = _load_data()
    crafted: list[str] = data.setdefault("crafted_ships", [])
    if ship_id not in crafted:
        crafted.append(ship_id)
        _save_data()
