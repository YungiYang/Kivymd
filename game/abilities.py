"""Система активних та пасивних здібностей гравця для Galaxy Defender."""

from dataclasses import dataclass, field
from typing import Callable
import random


# ---------------------------------------------------------------------------
# ПАСИВНІ ЗДІБНОСТІ (DropAbility) — постійні бафи з дропу боса
# ---------------------------------------------------------------------------

@dataclass
class PassiveAbility:
    """Опис однієї пасивної здібності."""
    ability_id: str
    name: str
    icon: str
    description: str
    rarity: str          # "rare", "epic", "legendary"
    color: tuple         # RGBA
    drop_chance: float   # базовий шанс дропу від боса (0.01–0.05)


# Каталог усіх пасивних здібностей
PASSIVE_ABILITIES_CATALOG: dict[str, PassiveAbility] = {
    "regen_coil": PassiveAbility(
        ability_id="regen_coil",
        name="Регенераційна Котушка",
        icon="🔄",
        description="Автоматично відновлює 1 HP кожні 3 секунди.",
        rarity="rare",
        color=(0.2, 1.0, 0.5, 1.0),
        drop_chance=0.04,
    ),
    "armor_plating": PassiveAbility(
        ability_id="armor_plating",
        name="Нанобронепластини",
        icon="🛡️",
        description="Зменшує весь вхідний урон на 15%.",
        rarity="rare",
        color=(0.6, 0.6, 0.9, 1.0),
        drop_chance=0.035,
    ),
    "targeting_ai": PassiveAbility(
        ability_id="targeting_ai",
        name="Targeting-ШІ",
        icon="🎯",
        description="Кулі злегка наводяться на найближчого ворога (легкий хомінг).",
        rarity="rare",
        color=(0.9, 0.7, 0.2, 1.0),
        drop_chance=0.03,
    ),
    "void_shield": PassiveAbility(
        ability_id="void_shield",
        name="Щит Пустоти",
        icon="🌌",
        description="Раз на 15 секунд автоматично блокує один смертельний удар.",
        rarity="epic",
        color=(0.6, 0.1, 0.9, 1.0),
        drop_chance=0.025,
    ),
    "overdrive_core": PassiveAbility(
        ability_id="overdrive_core",
        name="Ядро Надприводу",
        icon="⚡",
        description="+20% урон куль та +15% швидкість стрільби назавжди.",
        rarity="epic",
        color=(1.0, 0.8, 0.1, 1.0),
        drop_chance=0.02,
    ),
    "phoenix_matrix": PassiveAbility(
        ability_id="phoenix_matrix",
        name="Матриця Фенікса",
        icon="🔥",
        description="При смерті — одноразово відроджується з 30% HP.",
        rarity="legendary",
        color=(1.0, 0.4, 0.1, 1.0),
        drop_chance=0.01,
    ),
    "quantum_cloak": PassiveAbility(
        ability_id="quantum_cloak",
        name="Квантовий Плащ",
        icon="👻",
        description="Кожні 20 секунд автоматично стає невразливим на 2 секунди.",
        rarity="legendary",
        color=(0.4, 0.2, 0.8, 1.0),
        drop_chance=0.01,
    ),
    "stellar_core": PassiveAbility(
        ability_id="stellar_core",
        name="Зоряне Ядро",
        icon="⭐",
        description="Усі характеристики +10%: HP, урон, швидкість, швидкість стрільби.",
        rarity="legendary",
        color=(1.0, 0.95, 0.3, 1.0),
        drop_chance=0.008,
    ),
}


# ---------------------------------------------------------------------------
# АКТИВНІ ЗДІБНОСТІ (ActiveAbility) — юзабельні скіли з кулдауном
# ---------------------------------------------------------------------------

@dataclass
class ActiveAbility:
    """Опис однієї активної здібності."""
    ability_id: str
    name: str
    icon: str
    description: str
    rarity: str           # "rare", "epic", "legendary"
    color: tuple          # RGBA
    drop_chance: float    # базовий шанс дропу від боса
    cooldown: float       # тривалість перезарядки (секунди)
    duration: float       # тривалість ефекту (0 = миттєвий)


# Каталог усіх активних здібностей
ACTIVE_ABILITIES_CATALOG: dict[str, ActiveAbility] = {
    "warp_jump": ActiveAbility(
        ability_id="warp_jump",
        name="Варп-Стрибок",
        icon="🚀",
        description="Миттєво телепортує у безпечну випадкову позицію (уникає всіх куль).",
        rarity="rare",
        color=(0.3, 0.7, 1.0, 1.0),
        drop_chance=0.05,
        cooldown=25.0,
        duration=0,
    ),
    "emergency_repair": ActiveAbility(
        ability_id="emergency_repair",
        name="Аварійний Ремонт",
        icon="🔧",
        description="Миттєво відновлює 50% максимального HP.",
        rarity="rare",
        color=(0.2, 1.0, 0.4, 1.0),
        drop_chance=0.06,
        cooldown=45.0,
        duration=0,
    ),
    "time_warp": ActiveAbility(
        ability_id="time_warp",
        name="Уповільнення Часу",
        icon="⏱️",
        description="Уповільнює всіх ворогів та кулі на 60% протягом 4 секунд.",
        rarity="epic",
        color=(0.8, 0.4, 1.0, 1.0),
        drop_chance=0.04,
        cooldown=35.0,
        duration=4.0,
    ),
    "nova_burst": ActiveAbility(
        ability_id="nova_burst",
        name="Спалах Нови",
        icon="💥",
        description="Миттєво завдає 80 урону ВСІМ ворогам на екрані.",
        rarity="epic",
        color=(1.0, 0.5, 0.1, 1.0),
        drop_chance=0.03,
        cooldown=40.0,
        duration=0,
    ),
    "biome_shift": ActiveAbility(
        ability_id="biome_shift",
        name="Зміна Локації",
        icon="🌀",
        description="Негайно ініціює перехід біому — втеча від небезпеки!",
        rarity="rare",
        color=(0.4, 0.9, 0.6, 1.0),
        drop_chance=0.06,
        cooldown=60.0,
        duration=0,
    ),
    "resurrection": ActiveAbility(
        ability_id="resurrection",
        name="Воскресіння",
        icon="☀️",
        description="Відроджує зі 100% HP та тимчасовою невразливістю на 3 секунди.",
        rarity="legendary",
        color=(1.0, 0.9, 0.2, 1.0),
        drop_chance=0.015,
        cooldown=180.0,
        duration=0,
    ),
    "shield_overload": ActiveAbility(
        ability_id="shield_overload",
        name="Перевантаження Щита",
        icon="⚡",
        description="Активує мега-щит, що поглинає ВЕСЬ урон протягом 5 секунд.",
        rarity="epic",
        color=(0.3, 0.8, 1.0, 1.0),
        drop_chance=0.035,
        cooldown=30.0,
        duration=5.0,
    ),
    "missile_barrage": ActiveAbility(
        ability_id="missile_barrage",
        name="Ракетний Шторм",
        icon="🚀",
        description="Випускає 12 ракет у всіх напрямках, кожна завдає 60 урону.",
        rarity="epic",
        color=(1.0, 0.3, 0.2, 1.0),
        drop_chance=0.025,
        cooldown=50.0,
        duration=0,
    ),
}


# ---------------------------------------------------------------------------
# СТАН ЗДІБНОСТЕЙ ГРАВЦЯ
# ---------------------------------------------------------------------------

class PlayerAbilities:
    """Зберігає та оновлює стан усіх здібностей поточного гравця."""

    # Константи пасивних механік
    _REGEN_INTERVAL: float = 3.0       # секунди між тіками регенерації
    _VOID_SHIELD_CD: float = 15.0      # кулдаун щита пустоти
    _QUANTUM_INTERVAL: float = 20.0    # інтервал активації квантового плаща
    _QUANTUM_DURATION: float = 2.0     # тривалість невразливості плаща

    def __init__(self) -> None:
        # Зібрані пасивні та активні здібності
        self.passive_ids: list[str] = []
        self.active_ids: list[str] = []      # максимум 3 активних
        self.active_cooldowns: dict[str, float] = {}        # таймери перезарядки
        self.active_duration_timers: dict[str, float] = {}  # таймери активних ефектів

        # Стан пасивних ефектів
        self.regen_timer: float = 0.0
        self.void_shield_timer: float = 0.0          # кулдаун щита пустоти
        self.quantum_cloak_timer: float = 0.0        # час до наступної активації плаща
        self.quantum_cloak_active: bool = False       # чи активний плащ зараз
        self.quantum_cloak_duration_timer: float = 0.0
        self.phoenix_used: bool = False               # чи вже використано відродження
        self.invincible_timer: float = 0.0            # загальний таймер невразливості

    # ------------------------------------------------------------------
    # Додавання здібностей
    # ------------------------------------------------------------------

    def add_passive(self, ability_id: str) -> bool:
        """Додає пасивну здібність, якщо ще не зібрана. Повертає True при успіху."""
        if ability_id in self.passive_ids:
            return False
        if ability_id not in PASSIVE_ABILITIES_CATALOG:
            return False
        self.passive_ids.append(ability_id)
        return True

    def add_active(self, ability_id: str) -> bool:
        """Додає активну здібність (макс. 3). Повертає True при успіху."""
        if ability_id in self.active_ids:
            return False
        if ability_id not in ACTIVE_ABILITIES_CATALOG:
            return False
        if len(self.active_ids) >= 3:
            return False
        self.active_ids.append(ability_id)
        self.active_cooldowns[ability_id] = 0.0
        return True

    # ------------------------------------------------------------------
    # Перевірки наявності
    # ------------------------------------------------------------------

    def has_passive(self, ability_id: str) -> bool:
        """Повертає True якщо гравець має вказану пасивну здібність."""
        return ability_id in self.passive_ids

    def has_active(self, ability_id: str) -> bool:
        """Повертає True якщо гравець має вказану активну здібність."""
        return ability_id in self.active_ids

    # ------------------------------------------------------------------
    # Активні здібності — використання та кулдаун
    # ------------------------------------------------------------------

    def can_use_active(self, ability_id: str) -> bool:
        """Повертає True якщо активна здібність готова до використання."""
        if not self.has_active(ability_id):
            return False
        return self.active_cooldowns.get(ability_id, 0.0) <= 0.0

    def use_active(self, ability_id: str) -> None:
        """Запускає кулдаун після використання активної здібності."""
        if ability_id not in ACTIVE_ABILITIES_CATALOG:
            return
        cfg = ACTIVE_ABILITIES_CATALOG[ability_id]
        self.active_cooldowns[ability_id] = cfg.cooldown
        # Якщо здібність має тривалість — запускаємо таймер ефекту
        if cfg.duration > 0:
            self.active_duration_timers[ability_id] = cfg.duration

    def get_active_cooldown_remaining(self, ability_id: str) -> float:
        """Повертає час, що залишився до завершення кулдауну (0 якщо готово)."""
        return max(0.0, self.active_cooldowns.get(ability_id, 0.0))

    # ------------------------------------------------------------------
    # Оновлення таймерів та застосування пасивних ефектів
    # ------------------------------------------------------------------

    def update(self, dt: float, player) -> None:
        """Оновлює всі таймери та застосовує пасивні ефекти.

        Args:
            dt:     дельта часу з минулого кадру (секунди).
            player: об'єкт гравця з полями hp, max_hp тощо.
        """
        # --- Кулдауни активних здібностей ---
        for aid in list(self.active_cooldowns.keys()):
            if self.active_cooldowns[aid] > 0.0:
                self.active_cooldowns[aid] = max(0.0, self.active_cooldowns[aid] - dt)

        # --- Таймери тривалості активних ефектів ---
        for aid in list(self.active_duration_timers.keys()):
            if self.active_duration_timers[aid] > 0.0:
                self.active_duration_timers[aid] = max(
                    0.0, self.active_duration_timers[aid] - dt
                )

        # --- Загальний таймер невразливості ---
        if self.invincible_timer > 0.0:
            self.invincible_timer = max(0.0, self.invincible_timer - dt)

        # --- regen_coil: регенерація 1 HP кожні 3 секунди ---
        if self.has_passive("regen_coil"):
            self.regen_timer += dt
            if self.regen_timer >= self._REGEN_INTERVAL:
                self.regen_timer -= self._REGEN_INTERVAL
                if hasattr(player, "hp") and hasattr(player, "max_hp"):
                    if player.hp < player.max_hp:
                        player.hp = min(player.max_hp, player.hp + 1)

        # --- quantum_cloak: невразливість 2с кожні 20с ---
        if self.has_passive("quantum_cloak"):
            if self.quantum_cloak_active:
                # Відраховуємо тривалість активного плаща
                self.quantum_cloak_duration_timer -= dt
                if self.quantum_cloak_duration_timer <= 0.0:
                    self.quantum_cloak_active = False
                    self.quantum_cloak_timer = 0.0  # скидаємо інтервал
            else:
                self.quantum_cloak_timer += dt
                if self.quantum_cloak_timer >= self._QUANTUM_INTERVAL:
                    self.quantum_cloak_timer = 0.0
                    self.quantum_cloak_active = True
                    self.quantum_cloak_duration_timer = self._QUANTUM_DURATION

        # --- void_shield: перезарядка щита ---
        if self.has_passive("void_shield"):
            if self.void_shield_timer < self._VOID_SHIELD_CD:
                self.void_shield_timer = min(
                    self._VOID_SHIELD_CD, self.void_shield_timer + dt
                )

    # ------------------------------------------------------------------
    # Геттери модифікаторів характеристик
    # ------------------------------------------------------------------

    def get_armor_reduction(self) -> float:
        """Повертає відсоток зниження вхідного урону (0.15 якщо є armor_plating)."""
        return 0.15 if self.has_passive("armor_plating") else 0.0

    def get_damage_multiplier(self) -> float:
        """Повертає множник урону куль (1.2 якщо є overdrive_core)."""
        base = 1.2 if self.has_passive("overdrive_core") else 1.0
        if self.has_passive("stellar_core"):
            base *= 1.1
        return base

    def get_firerate_multiplier(self) -> float:
        """Повертає множник кулдауну стрільби (<1 = швидше).

        overdrive_core скорочує кулдаун на 15% (множник 0.85).
        stellar_core додатково скорочує ще на 10%.
        """
        base = 0.85 if self.has_passive("overdrive_core") else 1.0
        if self.has_passive("stellar_core"):
            base *= 0.9
        return base

    def is_invincible(self) -> bool:
        """Повертає True якщо гравець зараз невразливий (плащ або таймер)."""
        return self.quantum_cloak_active or self.invincible_timer > 0.0

    # ------------------------------------------------------------------
    # Спеціальні перевірки
    # ------------------------------------------------------------------

    def check_void_shield_proc(self) -> bool:
        """Перевіряє чи спрацьовує щит пустоти при смертельному ударі.

        Повертає True та скидає таймер, якщо щит готовий.
        """
        if not self.has_passive("void_shield"):
            return False
        if self.void_shield_timer >= self._VOID_SHIELD_CD:
            self.void_shield_timer = 0.0  # починаємо перезарядку знову
            return True
        return False

    # ------------------------------------------------------------------
    # Скидання стану
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Повністю очищає всі здібності (викликається при перезапуску гри)."""
        self.passive_ids.clear()
        self.active_ids.clear()
        self.active_cooldowns.clear()
        self.active_duration_timers.clear()

        self.regen_timer = 0.0
        self.void_shield_timer = 0.0
        self.quantum_cloak_timer = 0.0
        self.quantum_cloak_active = False
        self.quantum_cloak_duration_timer = 0.0
        self.phoenix_used = False
        self.invincible_timer = 0.0


# ---------------------------------------------------------------------------
# ДОПОМІЖНІ ФУНКЦІЇ
# ---------------------------------------------------------------------------

def roll_passive_drop(biome_id: str) -> str | None:
    """Кидає кубик на дроп пасивної здібності після перемоги над босом.

    Базовий шанс кожної здібності = drop_chance * 0.5.
    Повертає ability_id або None якщо нічого не випало.

    Args:
        biome_id: ідентифікатор поточного біому (для майбутньої гнучкості).
    """
    # Перемішуємо для рівномірності
    candidates = list(PASSIVE_ABILITIES_CATALOG.values())
    random.shuffle(candidates)

    for ability in candidates:
        effective_chance = ability.drop_chance * 0.5
        if random.random() < effective_chance:
            return ability.ability_id
    return None


def roll_active_drop(biome_id: str) -> str | None:
    """Кидає кубик на дроп активної здібності після перемоги над босом.

    Базовий шанс кожної здібності = drop_chance * 0.5.
    Повертає ability_id або None якщо нічого не випало.

    Args:
        biome_id: ідентифікатор поточного біому (для майбутньої гнучкості).
    """
    candidates = list(ACTIVE_ABILITIES_CATALOG.values())
    random.shuffle(candidates)

    for ability in candidates:
        effective_chance = ability.drop_chance * 0.5
        if random.random() < effective_chance:
            return ability.ability_id
    return None


def get_passive_config(ability_id: str) -> PassiveAbility:
    """Повертає конфігурацію пасивної здібності за її ID.

    Raises:
        KeyError: якщо ability_id не існує в каталозі.
    """
    return PASSIVE_ABILITIES_CATALOG[ability_id]


def get_active_config(ability_id: str) -> ActiveAbility:
    """Повертає конфігурацію активної здібності за її ID.

    Raises:
        KeyError: якщо ability_id не існує в каталозі.
    """
    return ACTIVE_ABILITIES_CATALOG[ability_id]
