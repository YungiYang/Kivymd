"""Розширений каталог ворогів та типів босів для Galaxy Defender.

Містить нові типи рядових ворогів (8 типів) та елітних/розширених босів.
"""

import random
import math
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, Ellipse, Triangle, Line, RoundedRectangle
)
from game.constants import (
    ENEMY_WIDTH, ENEMY_HEIGHT,
    BULLET_HEIGHT, BULLET_PLAYER_DAMAGE,
    COLOR_BULLET_ENEMY,
)
from game.entities import Bullet, Particle


# ─── Розширені типи ворогів ───────────────────────────────────────────────────

class AdvancedEnemy(Widget):
    """Розширений ворог з унікальними патернами атак та специфікою біому.

    Типи:
        - \"drone\"      : Швидкий рій-дрон (з'являється по 3-5 штук)
        - \"turret\"     : Нерухома турель з швидким вогнем
        - \"shielder\"   : Ворог зі щитом — треба стріляти з-за боку
        - \"kamikaze\"   : Камікадзе — летить прямо на гравця
        - \"healer\"     : Хілер — лікує сусідніх ворогів
        - \"stealth\"    : Стелс — стає невидимим кожні 3 сек
        - \"splitter\"   : При знищенні ділиться на 2 маленьких
        - \"titan\"      : Супер-важкий — повільний, але дуже живучий
    """

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str = "drone",
        biome: str = "space",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.enemy_type = enemy_type
        self.biome = biome
        self.x = x
        self.y = y
        self.spawn_x = x
        self.time_alive = random.uniform(0.0, 6.28)
        self.time_since_last_shot = random.uniform(0.0, 2.0)
        self.is_dead = False
        self.is_visible = True
        self.stealth_timer = 0.0
        self.stealth_active = False
        self.split_done = False  # для splitter

        self._configure_type()
        self.redraw()

    def _configure_type(self):
        """Налаштовує статистику відповідно до типу."""
        t = self.enemy_type

        if t == "drone":
            self.width = 28
            self.height = 28
            self.max_hp = 15
            self.hp = 15
            self.speed = random.uniform(240.0, 320.0)
            self.score_value = 80
            self.fire_cooldown = random.uniform(2.8, 4.0)

        elif t == "turret":
            self.width = 40
            self.height = 40
            self.max_hp = 50
            self.hp = 50
            self.speed = 0.0  # Нерухома
            self.score_value = 200
            self.fire_cooldown = random.uniform(0.55, 0.9)

        elif t == "shielder":
            self.width = 48
            self.height = 44
            self.max_hp = 65
            self.hp = 65
            self.shield = 40  # Поглинає 40 шкоди
            self.speed = random.uniform(85.0, 115.0)
            self.score_value = 280
            self.fire_cooldown = random.uniform(1.5, 2.5)

        elif t == "kamikaze":
            self.width = 34
            self.height = 34
            self.max_hp = 25
            self.hp = 25
            self.speed = random.uniform(300.0, 420.0)
            self.score_value = 120
            self.fire_cooldown = 999.0  # Не стріляє — тільки летить

        elif t == "healer":
            self.width = 38
            self.height = 42
            self.max_hp = 35
            self.hp = 35
            self.speed = random.uniform(75.0, 100.0)
            self.score_value = 240
            self.fire_cooldown = random.uniform(2.0, 3.0)

        elif t == "stealth":
            self.width = 36
            self.height = 36
            self.max_hp = 28
            self.hp = 28
            self.speed = random.uniform(150.0, 200.0)
            self.score_value = 220
            self.fire_cooldown = random.uniform(1.8, 2.8)

        elif t == "splitter":
            self.width = 46
            self.height = 44
            self.max_hp = 55
            self.hp = 55
            self.speed = random.uniform(95.0, 135.0)
            self.score_value = 260
            self.fire_cooldown = random.uniform(2.0, 3.0)

        elif t == "titan":
            self.width = 70
            self.height = 64
            self.max_hp = 180
            self.hp = 180
            self.speed = random.uniform(50.0, 75.0)
            self.score_value = 500
            self.fire_cooldown = random.uniform(1.0, 1.6)

        else:
            self.width = ENEMY_WIDTH
            self.height = ENEMY_HEIGHT
            self.max_hp = 30
            self.hp = 30
            self.speed = 120.0
            self.score_value = 100
            self.fire_cooldown = 2.0

        if not hasattr(self, "shield"):
            self.shield = 0

    @property
    def hazard_type(self) -> str:
        """Повертає тип небезпеки відповідно до поточного біому."""
        from game.biomes import get_biome_config
        return get_biome_config(self.biome).hazard_type

    def shoot(self, player_pos: tuple = None) -> list[Bullet]:
        """Здійснює постріл відповідно до типу ворога та біому."""
        result = self._shoot_pattern(player_pos)
        return result if isinstance(result, list) else [result]

    def _get_hazard_color(self):
        """Повертає колір кулі відповідно до біому."""
        hazard_colors = {
            "burn": (1.0, 0.40, 0.05, 1.0),
            "slow": (0.15, 0.90, 0.95, 1.0),
            "emp": (0.85, 0.25, 1.0, 1.0),
            "freeze": (0.50, 0.90, 1.0, 1.0),
            "toxin": (0.35, 1.0, 0.10, 1.0),
            "gravity": (0.7, 0.5, 1.0, 1.0),
            "dark": (0.6, 0.2, 0.9, 1.0),
            "void": (1.0, 0.3, 0.8, 1.0),
        }
        return hazard_colors.get(self.hazard_type, COLOR_BULLET_ENEMY)

    def _shoot_pattern(self, player_pos: tuple = None):
        """Патерн стрільби відповідно до типу ворога."""
        cx = self.x + self.width / 2.0
        cy = self.y - BULLET_HEIGHT
        haz = self.hazard_type
        col = self._get_hazard_color()

        if self.enemy_type == "drone":
            # Простий одиночний постріл
            return Bullet(cx - 3, cy, is_player=False, damage=8, speed=-380.0,
                          color=col, hazard_type=haz)

        elif self.enemy_type == "turret":
            # Швидкий спарений залп
            b1 = Bullet(cx - 6, cy, is_player=False, damage=12, speed=-420.0,
                        color=col, hazard_type=haz)
            b2 = Bullet(cx + 3, cy, is_player=False, damage=12, speed=-420.0,
                        color=col, hazard_type=haz)
            return [b1, b2]

        elif self.enemy_type == "shielder":
            # Три-кулі широкий залп
            b1 = Bullet(cx - 14, cy, is_player=False, damage=14, vx=-55.0, vy=-300.0,
                        color=col, hazard_type=haz)
            b2 = Bullet(cx - 3, cy, is_player=False, damage=14, speed=-300.0,
                        color=col, hazard_type=haz)
            b3 = Bullet(cx + 8, cy, is_player=False, damage=14, vx=55.0, vy=-300.0,
                        color=col, hazard_type=haz)
            return [b1, b2, b3]

        elif self.enemy_type == "healer":
            # Слабкий постріл (він більше хілить)
            return Bullet(cx - 3, cy, is_player=False, damage=10, speed=-260.0,
                          color=col, hazard_type=haz)

        elif self.enemy_type == "stealth":
            # Прицільний постріл у гравця
            px, py = player_pos if player_pos else (cx, 0.0)
            dx, dy = px - cx, py - cy
            dist = max(1.0, math.hypot(dx, dy))
            vx = (dx / dist) * 460.0
            vy = (dy / dist) * 460.0
            return Bullet(cx - 3, cy, is_player=False, damage=16, vx=vx, vy=vy,
                          color=col, hazard_type=haz)

        elif self.enemy_type == "splitter":
            # Подвійний широкий залп
            b1 = Bullet(cx - 8, cy, is_player=False, damage=15, vx=-80.0, vy=-310.0,
                        color=col, hazard_type=haz)
            b2 = Bullet(cx + 5, cy, is_player=False, damage=15, vx=80.0, vy=-310.0,
                        color=col, hazard_type=haz)
            return [b1, b2]

        elif self.enemy_type == "titan":
            # Потрійний важкий залп (3 великих снаряди)
            b1 = Bullet(cx - 14, cy, is_player=False, damage=28, vx=-70.0, vy=-250.0,
                        color=col, hazard_type=haz, width=12, height=18)
            b2 = Bullet(cx - 3, cy, is_player=False, damage=30, speed=-280.0,
                        color=col, hazard_type=haz, width=12, height=18)
            b3 = Bullet(cx + 8, cy, is_player=False, damage=28, vx=70.0, vy=-250.0,
                        color=col, hazard_type=haz, width=12, height=18)
            return [b1, b2, b3]

        return Bullet(cx - 3, cy, is_player=False, damage=10, speed=-300.0,
                      color=col, hazard_type=haz)

    def get_split_children(self) -> list["AdvancedEnemy"]:
        """Для splitter: повертає 2 маленьких drone-ворога після знищення."""
        if self.enemy_type != "splitter" or self.split_done:
            return []
        self.split_done = True
        cx = self.x + self.width / 2
        e1 = AdvancedEnemy(cx - 18, self.y, "drone", self.biome)
        e2 = AdvancedEnemy(cx + 10, self.y, "drone", self.biome)
        return [e1, e2]

    def update(self, dt: float, player_pos: tuple = None) -> list[Bullet] | None:
        """Оновлює стан ворога та повертає постріли при готовності."""
        self.time_alive += dt
        self.time_since_last_shot += dt

        # Stealth: ховається кожні 3 сек на 1.5 сек
        if self.enemy_type == "stealth":
            self.stealth_timer += dt
            if self.stealth_timer > 4.5:
                self.stealth_timer = 0.0
            self.stealth_active = self.stealth_timer > 3.0

        # Kamikaze: летить прямо на гравця
        if self.enemy_type == "kamikaze" and player_pos:
            px, py = player_pos
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            dx, dy = px - cx, py - cy
            dist = max(1.0, math.hypot(dx, dy))
            self.x += (dx / dist) * self.speed * dt
            self.y += (dy / dist) * self.speed * dt
        else:
            # Рух вниз + зигзаг для drone
            self.y -= self.speed * dt
            if self.enemy_type == "drone":
                self.x = self.spawn_x + math.sin(self.time_alive * 5.5) * 40.0
            elif self.enemy_type == "healer":
                self.x = self.spawn_x + math.sin(self.time_alive * 1.8) * 25.0

        # Пострілги
        shots = None
        if self.time_since_last_shot >= self.fire_cooldown and self.enemy_type != "kamikaze":
            self.time_since_last_shot = 0.0
            self.fire_cooldown = random.uniform(
                self.fire_cooldown * 0.8, self.fire_cooldown * 1.2
            )
            shots = self.shoot(player_pos)

        self.redraw()
        return shots

    def take_damage(self, amount: int):
        """Зменшує HP з урахуванням щита."""
        if self.shield > 0:
            absorbed = min(self.shield, amount)
            self.shield -= absorbed
            amount -= absorbed
        self.hp = max(0, self.hp - amount)

    def is_out_of_bounds(self) -> bool:
        return self.y < -self.height - 30

    def redraw(self):
        self.canvas.clear()
        if not self.is_visible or (self.stealth_active and self.enemy_type == "stealth"):
            return

        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0

        with self.canvas:
            t = self.enemy_type

            if t == "drone":
                # Швидкий тактичний розвідувальний дрон MK-II
                # Полум'я мікродвигунів
                Color(1.0, 0.65, 0.15, 0.85)
                Triangle(points=[
                    cx - 4, self.y + self.height,
                    cx, self.y + self.height + 6,
                    cx + 4, self.y + self.height,
                ])
                # Гранований аеродинамічний корпус
                Color(0.16, 0.20, 0.28, 1.0)
                Triangle(points=[
                    self.x, cy,
                    cx, self.y + self.height,
                    self.x + self.width, cy,
                ])
                Triangle(points=[
                    self.x + 3, cy,
                    cx, self.y + 2,
                    self.x + self.width - 3, cy,
                ])
                # Золотисті кромки крил
                Color(0.95, 0.72, 0.20, 0.95)
                Line(points=[self.x, cy, cx, self.y + 2, self.x + self.width, cy], width=1.5)
                # Сенсорне фотонне око
                Color(0.2, 0.9, 1.0, 0.95)
                Ellipse(pos=(cx - 3.5, cy - 3.5), size=(7, 7))

            elif t == "turret":
                # Важка орбітальна автоматична турель
                # Броньована опора
                Color(0.18, 0.22, 0.28, 1.0)
                RoundedRectangle(pos=(self.x + 2, self.y + 4), size=(self.width - 4, self.height - 8), radius=[6])
                # Внутрішня поворотна тумба
                Color(0.28, 0.35, 0.44, 1.0)
                Ellipse(pos=(cx - 12, cy - 10), size=(24, 24))
                # Неоновий прицільний блок
                Color(0.2, 1.0, 0.45, 0.95)
                Rectangle(pos=(cx - 6, cy - 4), size=(12, 4))
                # Спарені гарматні стволи з полум'ягасниками
                Color(0.45, 0.55, 0.65, 1.0)
                Line(points=[cx - 6, cy, cx - 6, self.y - 12], width=2.8)
                Line(points=[cx + 6, cy, cx + 6, self.y - 12], width=2.8)
                Color(0.2, 1.0, 0.45, 0.8)
                Ellipse(pos=(cx - 8, self.y - 13), size=(4, 4))
                Ellipse(pos=(cx + 4, self.y - 13), size=(4, 4))

            elif t == "shielder":
                # Захисний фрегат з дефлекторним щитом
                Color(0.15, 0.22, 0.35, 1.0)
                Triangle(points=[
                    self.x + 4, self.y + 8,
                    cx, self.y + self.height,
                    self.x + self.width - 4, self.y + 8,
                ])
                # Броньові щитки
                Color(0.35, 0.55, 0.85, 1.0)
                Triangle(points=[
                    self.x + 10, self.y + 16,
                    cx, self.y + self.height - 4,
                    self.x + self.width - 10, self.y + 16,
                ])
                # Енергетичний реактор щита
                Color(0.3, 0.85, 1.0, 0.95)
                Ellipse(pos=(cx - 5, cy - 4), size=(10, 10))
                if self.shield > 0:
                    shield_r = self.width * 0.68
                    # Багатошаровий дефлекторний бар'єр
                    Color(0.3, 0.85, 1.0, 0.20)
                    Ellipse(
                        pos=(cx - shield_r, cy - shield_r),
                        size=(shield_r * 2, shield_r * 2)
                    )
                    Color(0.4, 0.95, 1.0, 0.85)
                    Line(circle=(cx, cy, shield_r), width=2.2)
                    Color(0.2, 0.7, 1.0, 0.5)
                    Line(circle=(cx, cy, shield_r - 4), width=1.0)

            elif t == "kamikaze":
                # Швидкісний перехоплювач-камікадзе
                # Вогненний реактивний факел
                Color(1.0, 0.45, 0.05, 0.9)
                Triangle(points=[
                    cx - 5, self.y + self.height,
                    cx, self.y + self.height + 12,
                    cx + 5, self.y + self.height,
                ])
                Color(1.0, 0.9, 0.2, 1.0)
                Triangle(points=[
                    cx - 2, self.y + self.height,
                    cx, self.y + self.height + 6,
                    cx + 2, self.y + self.height,
                ])
                # Стрілоподібні хижі крила
                Color(0.65, 0.12, 0.12, 1.0)
                Triangle(points=[cx, self.y + self.height, self.x, cy, cx, self.y])
                Triangle(points=[cx, self.y + self.height, self.x + self.width, cy, cx, self.y])
                # Перевантажене плазмове ядро
                Color(1.0, 0.85, 0.2, 0.95)
                Ellipse(pos=(cx - 6, cy - 6), size=(12, 12))
                Color(1.0, 1.0, 0.9, 1.0)
                Ellipse(pos=(cx - 2.5, cy - 2.5), size=(5, 5))

            elif t == "healer":
                # Ремонтний нано-фрегат
                Color(0.14, 0.26, 0.22, 1.0)
                RoundedRectangle(pos=(self.x + 4, self.y + 4), size=(self.width - 8, self.height - 8), radius=[6])
                # Медичний смарагдовий хрест
                Color(0.25, 0.95, 0.55, 0.95)
                Rectangle(pos=(cx - 4, self.y + 6), size=(8, self.height - 12))
                Rectangle(pos=(self.x + 6, cy - 4), size=(self.width - 12, 8))
                # Фотонний випромінювач нанітів
                Color(0.7, 1.0, 0.85, 1.0)
                Ellipse(pos=(cx - 4, cy - 4), size=(8, 8))

            elif t == "stealth":
                # Стелс-шпигун з оптичним маскуванням
                alpha = 0.25 if self.stealth_active else 0.88
                Color(0.25, 0.28, 0.38, alpha)
                Triangle(points=[
                    self.x + 3, self.y + 4,
                    cx, self.y + self.height,
                    self.x + self.width - 3, self.y + 4,
                ])
                # Грані антирадарної геометрії
                Color(0.55, 0.65, 0.9, alpha)
                Line(points=[self.x + 3, self.y + 4, cx, self.y + 4, cx, self.y + self.height], width=1.5)
                # Голковий квантовий приціл
                Color(0.4, 0.85, 1.0, alpha)
                Line(points=[cx, cy, cx, self.y - 6], width=2.0)

            elif t == "splitter":
                # Подвійний кластерний фрегат
                Color(0.45, 0.18, 0.55, 1.0)
                Triangle(points=[
                    self.x, self.y + self.height,
                    cx - 3, self.y + 4,
                    cx - 3, self.y + self.height,
                ])
                Triangle(points=[
                    cx + 3, self.y + self.height,
                    cx + 3, self.y + 4,
                    self.x + self.width, self.y + self.height,
                ])
                # Плазмова перемичка розщеплення
                Color(0.9, 0.4, 1.0, 0.95)
                Line(points=[cx - 4, cy, cx + 4, cy], width=3.0)
                Ellipse(pos=(cx - 3, cy - 3), size=(6, 6))

            elif t == "titan":
                # Важкий флагманський дредноут
                Color(0.18, 0.20, 0.28, 1.0)
                RoundedRectangle(pos=(self.x + 4, self.y + 6), size=(self.width - 8, self.height - 12), radius=[8])
                Color(0.32, 0.38, 0.50, 1.0)
                Triangle(points=[
                    self.x + 6, self.y + 18,
                    cx, self.y + self.height - 4,
                    self.x + self.width - 6, self.y + 18,
                ])
                # Важкі подвійні рейкотрони
                Color(0.5, 0.6, 0.75, 1.0)
                Line(points=[self.x + 10, cy, self.x + 10, self.y - 14], width=3.5)
                Line(points=[self.x + self.width - 10, cy, self.x + self.width - 10, self.y - 14], width=3.5)
                # Масивне термоядерне ядро
                Color(0.3, 0.75, 1.0, 0.95)
                Ellipse(pos=(cx - 9, cy - 9), size=(18, 18))
                Color(0.9, 0.95, 1.0, 1.0)
                Ellipse(pos=(cx - 4, cy - 4), size=(8, 8))

            # Військова тактична рамка смужки міцності (HUD Health Bracket)
            if self.hp < self.max_hp:
                bar_w = self.width + 4
                bar_h = 4.0
                bar_x = self.x - 2
                bar_y = self.y + self.height + 4
                Color(0.04, 0.08, 0.14, 0.85)
                RoundedRectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h), radius=[2])
                ratio = max(0.0, self.hp / self.max_hp)
                hp_color = (0.2, 0.95, 0.4, 0.95) if ratio > 0.5 else (1.0, 0.25, 0.25, 0.95)
                Color(*hp_color)
                RoundedRectangle(pos=(bar_x, bar_y), size=(bar_w * ratio, bar_h), radius=[2])
                Color(0.3, 0.75, 1.0, 0.6)
                Line(rounded_rectangle=[bar_x, bar_y, bar_w, bar_h, 2], width=0.8)


# ─── Таблиці появи ворогів за біомом ─────────────────────────────────────────

BIOME_ENEMY_WEIGHTS: dict[str, list[tuple[str, float]]] = {
    "space":       [("fighter", 0.35), ("scout", 0.25), ("sniper", 0.20), ("bomber", 0.10), ("cruiser", 0.10)],
    "lava":        [("fighter", 0.25), ("bomber", 0.30), ("kamikaze", 0.25), ("titan", 0.12), ("sniper", 0.08)],
    "water":       [("fighter", 0.25), ("scout", 0.30), ("shielder", 0.20), ("cruiser", 0.15), ("splitter", 0.10)],
    "cyber_storm": [("turret", 0.30), ("fighter", 0.20), ("drone", 0.25), ("stealth", 0.15), ("shielder", 0.10)],
    "ice":         [("fighter", 0.25), ("sniper", 0.25), ("splitter", 0.20), ("bomber", 0.15), ("titan", 0.15)],
    "toxic":       [("drone", 0.30), ("healer", 0.25), ("fighter", 0.20), ("splitter", 0.15), ("scout", 0.10)],
    "gravity":     [("titan", 0.25), ("kamikaze", 0.25), ("cruiser", 0.20), ("bomber", 0.15), ("shielder", 0.15)],
    "void":        [("stealth", 0.30), ("titan", 0.20), ("drone", 0.25), ("healer", 0.15), ("sniper", 0.10)],
    "nebula":      [("healer", 0.20), ("bomber", 0.25), ("shielder", 0.20), ("splitter", 0.20), ("cruiser", 0.15)],
}

# Які типи ADVANCED (не base Enemy)
ADVANCED_TYPES = {"drone", "turret", "shielder", "kamikaze", "healer", "stealth", "splitter", "titan"}
# Які типи BASE Enemy
BASE_TYPES = {"fighter", "scout", "sniper", "bomber", "cruiser"}


def pick_enemy_type(biome_id: str) -> str:
    """Обирає тип ворога з ваговою таблицею відповідно до біому."""
    table = BIOME_ENEMY_WEIGHTS.get(biome_id, BIOME_ENEMY_WEIGHTS["space"])
    rng = random.random()
    cumulative = 0.0
    for enemy_type, weight in table:
        cumulative += weight
        if rng <= cumulative:
            return enemy_type
    return table[-1][0]


def spawn_enemy_for_biome(x: float, y: float, biome_id: str, score: int = 0):
    """Породжує ворога відповідного типу для поточного біому та складності.

    Повертає або Enemy (з entities), або AdvancedEnemy.
    """
    from game.entities import Enemy
    enemy_type = pick_enemy_type(biome_id)

    # Масштабування складності відповідно до рахунку
    difficulty = max(1.0, 1.0 + score / 10000.0)

    if enemy_type in ADVANCED_TYPES:
        e = AdvancedEnemy(x=x, y=y, enemy_type=enemy_type, biome=biome_id)
        e.hp = int(e.hp * difficulty)
        e.max_hp = int(e.max_hp * difficulty)
        return e
    else:
        e = Enemy(x=x, y=y, enemy_type=enemy_type, biome=biome_id)
        e.hp = int(e.hp * difficulty)
        e.max_hp = int(e.max_hp * difficulty)
        return e


# ─── Елітний Бос-флагман ─────────────────────────────────────────────────────

class EliteBoss(Widget):
    """Надскладний елітний флагман для рівнів 5+.

    Має 4 фази бою, змінює тактику при зниженні HP.
    Відрізняється від звичайного Boss масивнішим HP, унікальними атаками
    та аурою біому.
    """

    PHASE_THRESHOLDS = [0.75, 0.50, 0.25]  # HP% для зміни фази

    def __init__(
        self,
        x: float,
        y: float,
        boss_level: int = 5,
        biome: str = "space",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.boss_level = boss_level
        self.biome = biome
        self.width = 140
        self.height = 95
        self.x = x
        self.y = y
        self.target_y = 0.0
        self.entered = False
        self.phase = 0  # 0, 1, 2, 3
        self.time_alive = 0.0
        self.move_dir = 1

        # Масштабування HP та швидкості
        self.max_hp = 6000 + (boss_level - 5) * 2000
        self.hp = self.max_hp
        self.speed = 65.0 + min(100.0, (boss_level - 4) * 15.0)
        self.score_value = 5000 + boss_level * 2000

        # Атаки
        self.attack_mode = 0
        self.fire_cooldown = max(0.65, 1.50 - (boss_level - 4) * 0.12)
        self.time_since_last_shot = 0.0

        self.engine_particles: list[Particle] = []
        self.redraw()

    @property
    def hazard_type(self) -> str:
        from game.biomes import get_biome_config
        return get_biome_config(self.biome).hazard_type

    def _get_phase(self) -> int:
        ratio = self.hp / self.max_hp
        if ratio <= 0.25:
            return 3
        elif ratio <= 0.50:
            return 2
        elif ratio <= 0.75:
            return 1
        return 0

    def update(
        self, dt: float, player_pos: tuple, screen_w: float, screen_h: float
    ) -> list[Bullet]:
        """Оновлює рух та атаки елітного боса."""
        self.time_alive += dt
        self.time_since_last_shot += dt
        self.target_y = screen_h - 165.0
        self.phase = self._get_phase()

        if not self.entered:
            self.y -= 110.0 * dt
            if self.y <= self.target_y:
                self.y = self.target_y
                self.entered = True
        else:
            # Фаза 2+: рух по синусоїді (агресивніший)
            if self.phase >= 2:
                self.x = (screen_w / 2) + math.sin(self.time_alive * 1.8) * (screen_w * 0.38)
            else:
                self.x += self.move_dir * self.speed * dt
                if self.x <= 12.0:
                    self.x = 12.0
                    self.move_dir = 1
                elif self.x >= screen_w - self.width - 12.0:
                    self.x = screen_w - self.width - 12.0
                    self.move_dir = -1

        # Часточки двигунів
        self._emit_engine_particles()
        alive_p = [p for p in self.engine_particles if not p.is_dead]
        for p in alive_p:
            p.update(dt)
        self.engine_particles = [p for p in alive_p if not p.is_dead]

        # Постріли (прискорюються з фазами)
        bullets = []
        cooldown_mult = max(0.5, 1.0 - self.phase * 0.15)
        if self.entered and self.time_since_last_shot >= self.fire_cooldown * cooldown_mult:
            self.time_since_last_shot = 0.0
            bullets = self._execute_attack(player_pos, screen_w)
            self.attack_mode = (self.attack_mode + 1) % (4 + self.phase)

        self.redraw()
        return bullets

    def _execute_attack(self, player_pos: tuple, screen_w: float) -> list[Bullet]:
        """Виконує атаку відповідно до поточної фази боса."""
        bullets = []
        cx = self.x + self.width / 2.0
        cy = self.y
        haz = self.hazard_type

        hazard_colors = {
            "burn": (1.0, 0.35, 0.05, 1.0),
            "slow": (0.15, 0.90, 0.95, 1.0),
            "emp": (0.85, 0.25, 1.0, 1.0),
            "freeze": (0.50, 0.90, 1.0, 1.0),
            "toxin": (0.35, 1.0, 0.10, 1.0),
            "gravity": (0.7, 0.5, 1.0, 1.0),
            "dark": (0.6, 0.2, 0.9, 1.0),
            "void": (1.0, 0.3, 0.8, 1.0),
        }
        col = hazard_colors.get(haz, (1.0, 0.2, 0.3, 1.0))

        mode = self.attack_mode % max(1, 4 + self.phase)

        if mode == 0:
            # 7-кульовий веєр
            angles_vx = [-190, -120, -55, 0, 55, 120, 190]
            for vx in angles_vx:
                bullets.append(Bullet(cx - 3, cy - 14, is_player=False,
                                      damage=14 + self.phase * 4,
                                      vx=vx, vy=-290.0, color=col, hazard_type=haz))

        elif mode == 1:
            # Прицільний подвійний залп
            px, py = player_pos if player_pos else (cx, 0)
            dx, dy = px - cx, py - cy
            dist = max(1.0, math.hypot(dx, dy))
            vx_n = (dx / dist) * 440.0
            vy_n = (dy / dist) * 440.0
            for offset in [-18, 18]:
                bullets.append(Bullet(cx + offset, cy - 12, is_player=False,
                                      damage=20 + self.phase * 5,
                                      vx=vx_n, vy=vy_n, color=col, hazard_type=haz))

        elif mode == 2:
            # Вертикальний зливний дощ (5 колонок)
            for col_x in [cx - 55, cx - 27, cx, cx + 27, cx + 55]:
                bullets.append(Bullet(col_x, cy - 10, is_player=False,
                                      damage=12 + self.phase * 3,
                                      vx=0, vy=-340.0, color=col, hazard_type=haz))

        elif mode == 3:
            # Круговий залп 360° (фаза 1+)
            angles = [i * (360 / 12) for i in range(12)]
            for angle in angles:
                rad = math.radians(angle)
                vx = math.sin(rad) * 320.0
                vy = math.cos(rad) * 320.0 - 100.0
                bullets.append(Bullet(cx - 3, cy - 8, is_player=False,
                                      damage=10 + self.phase * 4,
                                      vx=vx, vy=vy, color=col, hazard_type=haz))

        elif mode >= 4:
            # Спарений прицільний + веєр одночасно (лише фаза 2+)
            px, py = player_pos if player_pos else (cx, 0)
            dx, dy = px - cx, py - cy
            dist = max(1.0, math.hypot(dx, dy))
            vx_n = (dx / dist) * 480.0
            vy_n = (dy / dist) * 480.0
            bullets.append(Bullet(cx - 3, cy - 14, is_player=False,
                                  damage=25 + self.phase * 6,
                                  vx=vx_n, vy=vy_n, color=col, hazard_type=haz))
            for vx in [-140, 0, 140]:
                bullets.append(Bullet(cx - 3, cy - 14, is_player=False,
                                      damage=14,
                                      vx=vx, vy=-300.0, color=col, hazard_type=haz))

        return bullets

    def _emit_engine_particles(self):
        cx = self.x + self.width / 2.0
        for _ in range(3):
            self.engine_particles.append(Particle(
                cx + random.uniform(-22, 22),
                self.y + 2,
                random.uniform(-25, 25),
                random.uniform(-160, -80),
                random.uniform(3.0, 7.0),
                random.uniform(0.25, 0.5),
                (1.0, 0.5 + random.random() * 0.4, 0.1, 0.9),
            ))

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def is_defeated(self) -> bool:
        return self.hp <= 0

    def redraw(self):
        self.canvas.clear()
        cx = self.x + self.width / 2.0
        cy = self.y

        with self.canvas:
            # 1. Аура фази боса (енергетичний щитовий ореол)
            phase_colors = [
                (0.2, 0.6, 1.0, 0.16),   # Фаза 0 — синій іонний щит
                (1.0, 0.7, 0.1, 0.18),   # Фаза 1 — перевантаження плазми (янтар)
                (1.0, 0.25, 0.1, 0.22),  # Фаза 2 — критичний стан (червоний)
                (0.8, 0.1, 1.0, 0.26),   # Фаза 3 — темна сингулярність (фіолетовий)
            ]
            aura = phase_colors[min(self.phase, 3)]
            Color(*aura)
            Ellipse(
                pos=(cx - self.width * 0.75, cy - 15),
                size=(self.width * 1.5, self.height + 30)
            )

            # 2. Факели маршових термоядерних двигунів
            Color(1.0, 0.6, 0.15, 0.9)
            Triangle(points=[
                cx - 36, cy + self.height - 10,
                cx - 30, cy + self.height + 16,
                cx - 24, cy + self.height - 10,
            ])
            Triangle(points=[
                cx + 24, cy + self.height - 10,
                cx + 30, cy + self.height + 16,
                cx + 36, cy + self.height - 10,
            ])
            # Білі ядра полум'я
            Color(1.0, 1.0, 0.8, 1.0)
            Triangle(points=[
                cx - 33, cy + self.height - 10,
                cx - 30, cy + self.height + 8,
                cx - 27, cy + self.height - 10,
            ])
            Triangle(points=[
                cx + 27, cy + self.height - 10,
                cx + 30, cy + self.height + 8,
                cx + 33, cy + self.height - 10,
            ])

            # 3. Важкий титановий корпус флагмана
            Color(0.12, 0.14, 0.22, 1.0)
            RoundedRectangle(pos=(self.x + 8, cy + 12), size=(self.width - 16, self.height - 24), radius=[10])

            # 4. Броньові накладки та стрілоподібні спонсони
            Color(0.26, 0.30, 0.44, 1.0)
            Triangle(points=[
                self.x + 10, cy + 22,
                cx, cy + self.height - 2,
                self.x + self.width - 10, cy + 22,
            ])

            # 5. Бокові важкі крила-консолі
            Color(0.20, 0.22, 0.34, 1.0)
            Triangle(points=[cx - 25, cy + 18, self.x, cy + 8, cx - 10, cy + 34])
            Triangle(points=[cx + 25, cy + 18, self.x + self.width, cy + 8, cx + 10, cy + 34])
            Color(0.35, 0.7, 1.0, 0.7)
            Line(points=[self.x, cy + 8, cx - 25, cy + 18], width=1.5)
            Line(points=[self.x + self.width, cy + 8, cx + 25, cy + 18], width=1.5)

            # 6. Важкі батареї знарядь та головний калібр
            Color(0.55, 0.62, 0.78, 1.0)
            Line(points=[self.x + 16, cy + 10, self.x + 16, cy - 20], width=4.0)
            Line(points=[self.x + self.width - 16, cy + 10, self.x + self.width - 16, cy - 20], width=4.0)
            Line(points=[cx, cy + 12, cx, cy - 28], width=4.5)

            # 7. Плазмове ядро з магнітними кільцями стримування
            phase_core = [
                (0.3, 0.75, 1.0, 0.95),
                (1.0, 0.75, 0.1, 0.95),
                (1.0, 0.25, 0.1, 0.95),
                (0.85, 0.15, 1.0, 0.95),
            ]
            core_col = phase_core[min(self.phase, 3)]
            core_r = 18 + self.phase * 3
            Color(*core_col)
            Ellipse(pos=(cx - core_r / 2, cy + self.height / 2 - core_r / 2), size=(core_r, core_r))
            Color(1.0, 1.0, 1.0, 0.9)
            Ellipse(pos=(cx - core_r / 4, cy + self.height / 2 - core_r / 4), size=(core_r / 2, core_r / 2))
            Color(core_col[0], core_col[1], core_col[2], 0.65)
            Line(circle=(cx, cy + self.height / 2, core_r + 4), width=1.6)

            # 8. Тактичний бойовий індикатор міцності (HUD Boss Dreadnought Bar)
            bar_w = self.width + 36
            bar_h = 8.0
            bar_x = cx - bar_w / 2
            bar_y = cy + self.height + 10

            Color(0.04, 0.08, 0.15, 0.95)
            RoundedRectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h), radius=[3])

            ratio = max(0.0, self.hp / self.max_hp)
            if ratio > 0.5:
                Color(0.2, 0.95, 0.4, 0.95)
            elif ratio > 0.25:
                Color(1.0, 0.75, 0.1, 0.95)
            else:
                Color(1.0, 0.2, 0.2, 0.95)
            RoundedRectangle(pos=(bar_x, bar_y), size=(bar_w * ratio, bar_h), radius=[3])

            Color(0.2, 0.8, 1.0, 0.85)
            Line(rounded_rectangle=[bar_x, bar_y, bar_w, bar_h, 3], width=1.2)
