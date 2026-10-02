"""Система перешкод та небезпечних об'єктів у відкритому космосі для Galaxy Defender.

Перешкоди - статичні або рухомі об'єкти на ігровому полі, які завдають шкоди гравцю
при зіткненні. Кожен біом має свої унікальні типи перешкод.
"""

import random
import math
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color, Rectangle, Ellipse, Triangle, Line, RoundedRectangle
)


# ─── Базовий клас перешкоди ───────────────────────────────────────────────────

class Obstacle(Widget):
    """Базовий клас перешкоди. Поглинає снаряди та завдає шкоди при зіткненні."""

    def __init__(
        self,
        x: float,
        y: float,
        obstacle_type: str = "asteroid",
        biome: str = "space",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.obstacle_type = obstacle_type
        self.biome = biome
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-90.0, 90.0)
        self.hp = 1
        self.max_hp = 1
        self.contact_damage = 10
        self.is_destroyed = False
        self.time_alive = random.uniform(0.0, 6.28)
        self._configure()
        self.redraw()

    def _configure(self):
        """Налаштовує параметри відповідно до типу перешкоди."""
        t = self.obstacle_type

        if t == "asteroid":
            # Стандартний астероїд — повільно летить вниз
            size = random.uniform(28.0, 55.0)
            self.width = size
            self.height = size
            self.vx = random.uniform(-30.0, 30.0)
            self.vy = random.uniform(-90.0, -45.0)
            self.hp = random.randint(2, 5)
            self.max_hp = self.hp
            self.contact_damage = 12
            self._color = (0.55, 0.50, 0.45, 1.0)

        elif t == "meteor_lava":
            # Вулканічний метеорит — швидший, підпалює
            size = random.uniform(22.0, 42.0)
            self.width = size
            self.height = size
            self.vx = random.uniform(-55.0, 55.0)
            self.vy = random.uniform(-130.0, -70.0)
            self.hp = random.randint(2, 4)
            self.max_hp = self.hp
            self.contact_damage = 18
            self.hazard_type = "burn"
            self._color = (0.8, 0.25, 0.05, 1.0)

        elif t == "ice_shard":
            # Крижаний осколок — горизонтальний рух + freeze
            self.width = random.uniform(14.0, 28.0)
            self.height = random.uniform(32.0, 55.0)
            self.vx = random.choice([-1, 1]) * random.uniform(80.0, 150.0)
            self.vy = random.uniform(-60.0, -25.0)
            self.hp = 1
            self.max_hp = 1
            self.contact_damage = 14
            self.hazard_type = "freeze"
            self._color = (0.55, 0.90, 1.0, 0.85)

        elif t == "toxic_cloud":
            # Токсична хмара — широка, повільна, DoT
            self.width = random.uniform(55.0, 90.0)
            self.height = random.uniform(45.0, 70.0)
            self.vx = random.uniform(-20.0, 20.0)
            self.vy = random.uniform(-55.0, -30.0)
            self.hp = 3
            self.max_hp = 3
            self.contact_damage = 6  # per frame — відносно мала
            self.hazard_type = "toxin"
            self._color = (0.30, 0.85, 0.10, 0.55)

        elif t == "gravity_orb":
            # Гравітаційна куля — тягне гравця до себе
            size = random.uniform(32.0, 52.0)
            self.width = size
            self.height = size
            self.vx = random.uniform(-25.0, 25.0)
            self.vy = random.uniform(-70.0, -40.0)
            self.hp = 4
            self.max_hp = 4
            self.contact_damage = 20
            self.hazard_type = "gravity"
            self._color = (0.45, 0.15, 0.75, 0.9)

        elif t == "void_rift":
            # Розрив у просторі — поглинає снаряди, невидимий кластер
            size = random.uniform(40.0, 60.0)
            self.width = size
            self.height = size
            self.vx = random.uniform(-10.0, 10.0)
            self.vy = random.uniform(-45.0, -20.0)
            self.hp = 6
            self.max_hp = 6
            self.contact_damage = 25
            self.hazard_type = "dark"
            self._color = (0.12, 0.03, 0.22, 0.80)

        elif t == "nebula_blast":
            # Сонячний спалах туманності — блокує видимість
            size = random.uniform(50.0, 80.0)
            self.width = size
            self.height = size
            self.vx = random.uniform(-15.0, 15.0)
            self.vy = random.uniform(-50.0, -25.0)
            self.hp = 2
            self.max_hp = 2
            self.contact_damage = 8
            self.hazard_type = "void"
            self._color = (1.0, 0.35, 0.75, 0.6)

        elif t == "emp_mine":
            # EMP-міна — при зіткненні з кулею вибухає і дає EMP
            size = random.uniform(18.0, 28.0)
            self.width = size
            self.height = size
            self.vx = 0.0
            self.vy = random.uniform(-40.0, -18.0)
            self.hp = 1
            self.max_hp = 1
            self.contact_damage = 15
            self.hazard_type = "emp"
            self._color = (0.7, 0.2, 1.0, 0.9)

        else:
            # Запасний варіант
            self.width = 36.0
            self.height = 36.0
            self.vx = 0.0
            self.vy = -70.0
            self.hp = 2
            self.max_hp = 2
            self.contact_damage = 10
            self._color = (0.5, 0.5, 0.5, 1.0)

        if not hasattr(self, "hazard_type"):
            self.hazard_type = "none"

    def update(self, dt: float, player_x: float = None, player_y: float = None):
        """Оновлює позицію та поведінку перешкоди."""
        self.time_alive += dt
        self.rotation += self.rotation_speed * dt

        # Гравітаційна куля — тягнеться до гравця
        if self.obstacle_type == "gravity_orb" and player_x is not None:
            dx = player_x - (self.x + self.width / 2)
            pull = 35.0 * dt
            self.x += (1 if dx > 0 else -1) * pull

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Коливання для деяких типів
        if self.obstacle_type == "toxic_cloud":
            self.x += math.sin(self.time_alive * 1.5) * 18.0 * dt

    def take_damage(self, amount: int = 1):
        """Зменшує HP перешкоди."""
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_destroyed = True

    def is_out_of_bounds(self) -> bool:
        """Перевіряє вихід за межі екрана."""
        return self.y < -self.height - 30 or self.x < -self.width - 50 or self.x > 900

    def redraw(self):
        """Малює перешкоду відповідно до типу."""
        self.canvas.clear()
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        r, g, b, a = self._color

        with self.canvas:
            if self.obstacle_type == "asteroid":
                # Багатокутниковий астероїд з кратерами
                Color(r * 0.6, g * 0.6, b * 0.6, a)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(r, g, b, a)
                # Симуляція нерівної форми
                Triangle(points=[
                    self.x + self.width * 0.1, self.y + self.height * 0.15,
                    self.x + self.width * 0.9, self.y + self.height * 0.2,
                    self.x + self.width * 0.5, self.y + self.height * 0.9,
                ])
                # Кратери
                Color(r * 0.4, g * 0.4, b * 0.4, 0.7)
                sz = self.width * 0.25
                Ellipse(pos=(cx - sz * 1.2, cy - sz * 0.5), size=(sz, sz))
                sz2 = self.width * 0.16
                Ellipse(pos=(cx + sz * 0.3, cy + sz * 0.3), size=(sz2, sz2))

            elif self.obstacle_type == "meteor_lava":
                # Розпечений метеорит з вогняним ореолом
                Color(1.0, 0.3, 0.0, 0.45)
                glow = self.width * 1.4
                Ellipse(pos=(cx - glow / 2, cy - glow / 2), size=(glow, glow))
                Color(r, g, b, a)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(1.0, 0.9, 0.2, 0.9)
                core = self.width * 0.45
                Ellipse(pos=(cx - core / 2, cy - core / 2), size=(core, core))

            elif self.obstacle_type == "ice_shard":
                # Гострий крижаний осколок
                Color(0.75, 0.95, 1.0, 0.4)
                Ellipse(pos=(self.x - 4, self.y - 4), size=(self.width + 8, self.height + 8))
                Color(r, g, b, a)
                Triangle(points=[
                    cx, self.y + self.height,
                    self.x, self.y + self.height * 0.3,
                    self.x + self.width, self.y + self.height * 0.3,
                ])
                Triangle(points=[
                    cx, self.y,
                    self.x + self.width * 0.2, self.y + self.height * 0.35,
                    self.x + self.width * 0.8, self.y + self.height * 0.35,
                ])
                # Кристалічний блиск
                Color(1.0, 1.0, 1.0, 0.85)
                Line(points=[cx, self.y + self.height, cx - 4, self.y + self.height * 0.5], width=1.5)

            elif self.obstacle_type == "toxic_cloud":
                # Токсична хмара з кільцями
                pulse = 0.35 + 0.15 * math.sin(self.time_alive * 2.0)
                Color(r, g, b, a * pulse)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(r * 1.2, g, b * 0.5, 0.65)
                inner = self.width * 0.6
                Ellipse(pos=(cx - inner / 2, cy - inner / 2), size=(inner, inner))
                # Череп-знак
                Color(0.2, 0.8, 0.1, 0.7)
                Line(circle=(cx, cy, self.width * 0.25), width=1.2)

            elif self.obstacle_type == "gravity_orb":
                # Гравітаційна куля з кільцями тяжіння
                for ring in range(3):
                    rad = (self.width / 2) * (0.5 + ring * 0.35)
                    alpha = 0.55 - ring * 0.15
                    Color(r, g, b, alpha)
                    Line(circle=(cx, cy, rad), width=1.2)
                Color(r, g, b, 0.9)
                core = self.width * 0.4
                Ellipse(pos=(cx - core / 2, cy - core / 2), size=(core, core))
                Color(1.0, 0.8, 1.0, 0.95)
                inner = self.width * 0.2
                Ellipse(pos=(cx - inner / 2, cy - inner / 2), size=(inner, inner))

            elif self.obstacle_type == "void_rift":
                # Розрив у тканині простору — майже невидимий
                pulse = abs(math.sin(self.time_alive * 1.8))
                Color(r * 2, g, b * 3, a * (0.5 + pulse * 0.4))
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(0.7, 0.2, 1.0, 0.6)
                Line(circle=(cx, cy, self.width * 0.38), width=1.5)
                Color(0.0, 0.0, 0.0, 0.85)
                inner = self.width * 0.55
                Ellipse(pos=(cx - inner / 2, cy - inner / 2), size=(inner, inner))

            elif self.obstacle_type == "nebula_blast":
                # Спалах туманності — рожево-фіолетовий
                pulse = 0.4 + 0.3 * abs(math.sin(self.time_alive * 1.2))
                Color(r, g, b, a * pulse)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(1.0, 0.7, 0.9, 0.4)
                inner = self.width * 0.65
                Ellipse(pos=(cx - inner / 2, cy - inner / 2), size=(inner, inner))

            elif self.obstacle_type == "emp_mine":
                # EMP-міна — пульсуюча фіолетова
                pulse = abs(math.sin(self.time_alive * 3.5))
                Color(r, g, b, 0.6 + pulse * 0.35)
                Ellipse(pos=(self.x, self.y), size=(self.width, self.height))
                Color(1.0, 0.5, 1.0, 0.9)
                core = self.width * 0.4
                Ellipse(pos=(cx - core / 2, cy - core / 2), size=(core, core))
                # Кутові антени
                Color(0.9, 0.4, 1.0, 0.8)
                Line(points=[cx, cy + core / 2, cx, cy + self.height / 2 + 5], width=1.5)
                Line(points=[cx - core / 2, cy, self.x, cy], width=1.2)
                Line(points=[cx + core / 2, cy, self.x + self.width, cy], width=1.2)

            # HP-смужка (для перешкод з >1 HP)
            if self.max_hp > 1 and self.hp < self.max_hp:
                bar_w = self.width
                bar_h = 3.0
                Color(0.1, 0.1, 0.2, 0.8)
                Rectangle(pos=(self.x, self.y + self.height + 3), size=(bar_w, bar_h))
                ratio = max(0.0, self.hp / self.max_hp)
                Color(1.0, 0.55, 0.1, 0.95)
                Rectangle(pos=(self.x, self.y + self.height + 3), size=(bar_w * ratio, bar_h))


# ─── Фабрика перешкод за біомом ──────────────────────────────────────────────

# Таблиця можливих типів перешкод для кожного біому
BIOME_OBSTACLES: dict[str, list[tuple[str, float]]] = {
    "space":       [("asteroid", 0.70), ("emp_mine", 0.30)],
    "lava":        [("meteor_lava", 0.60), ("asteroid", 0.25), ("emp_mine", 0.15)],
    "water":       [("asteroid", 0.40), ("ice_shard", 0.35), ("toxic_cloud", 0.25)],
    "cyber_storm": [("emp_mine", 0.55), ("asteroid", 0.30), ("gravity_orb", 0.15)],
    "ice":         [("ice_shard", 0.55), ("asteroid", 0.35), ("gravity_orb", 0.10)],
    "toxic":       [("toxic_cloud", 0.60), ("asteroid", 0.25), ("meteor_lava", 0.15)],
    "gravity":     [("gravity_orb", 0.55), ("asteroid", 0.30), ("void_rift", 0.15)],
    "void":        [("void_rift", 0.55), ("asteroid", 0.25), ("emp_mine", 0.20)],
    "nebula":      [("nebula_blast", 0.55), ("asteroid", 0.25), ("toxic_cloud", 0.20)],
}


def spawn_obstacle(biome_id: str, screen_width: float, screen_height: float) -> Obstacle:
    """Породжує випадкову перешкоду відповідно до поточного біому."""
    table = BIOME_OBSTACLES.get(biome_id, BIOME_OBSTACLES["space"])
    rng = random.random()
    cumulative = 0.0
    chosen_type = table[0][0]
    for obstacle_type, chance in table:
        cumulative += chance
        if rng <= cumulative:
            chosen_type = obstacle_type
            break

    x = random.uniform(10.0, screen_width - 70.0)
    y = screen_height + random.uniform(20.0, 80.0)
    return Obstacle(x=x, y=y, obstacle_type=chosen_type, biome=biome_id)
