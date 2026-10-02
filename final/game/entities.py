"""Ігрові сутності: Гравець, Вороги, Кулі та Часточки."""

import random
from kivy.uix.widget import Widget
from kivy.graphics import (
    Color,
    Rectangle,
    Ellipse,
    Triangle,
    Line,
)
from game.constants import (
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
    PLAYER_MAX_HP,
    PLAYER_SPEED,
    PLAYER_FIRE_COOLDOWN,
    ENEMY_WIDTH,
    ENEMY_HEIGHT,
    ENEMY_DEFAULT_HP,
    ENEMY_SPEED_MIN,
    ENEMY_SPEED_MAX,
    ENEMY_FIRE_INTERVAL_MIN,
    ENEMY_FIRE_INTERVAL_MAX,
    BULLET_WIDTH,
    BULLET_HEIGHT,
    BULLET_PLAYER_SPEED,
    BULLET_ENEMY_SPEED,
    BULLET_PLAYER_DAMAGE,
    BULLET_ENEMY_DAMAGE,
    COLOR_PLAYER_PRIMARY,
    COLOR_PLAYER_SECONDARY,
    COLOR_PLAYER_ACCENT,
    COLOR_ENEMY_PRIMARY,
    COLOR_ENEMY_SECONDARY,
    COLOR_BULLET_PLAYER,
    COLOR_BULLET_ENEMY,
)


class Particle:
    """Часточка для анімації полум'я двигунів та вибухів."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        size: float,
        max_life: float,
        color: tuple,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.initial_size = size
        self.life = 0.0
        self.max_life = max_life
        self.color = color  # (r, g, b, a)
        self.is_dead = False

    def update(self, dt: float):
        self.life += dt
        if self.life >= self.max_life:
            self.is_dead = True
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Зменшення розміру та згасання прозорості з часом
        progress = self.life / self.max_life
        self.size = max(0.5, self.initial_size * (1.0 - progress))


class Bullet(Widget):
    """Окремий клас для куль гравця та ворогів."""

    def __init__(self, x: float, y: float, is_player: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.is_player = is_player
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.x = x
        self.y = y

        if is_player:
            self.vy = BULLET_PLAYER_SPEED
            self.damage = BULLET_PLAYER_DAMAGE
            self.color = COLOR_BULLET_PLAYER
        else:
            self.vy = BULLET_ENEMY_SPEED
            self.damage = BULLET_ENEMY_DAMAGE
            self.color = COLOR_BULLET_ENEMY

        self.redraw()

    def update(self, dt: float):
        """Переміщує кулю у відповідному напрямку."""
        self.y += self.vy * dt
        self.redraw()

    def is_out_of_bounds(self, screen_height: float) -> bool:
        """Перевіряє, чи вилетіла куля за межі ігрового поля."""
        return self.y > screen_height + 50 or self.y < -50

    def redraw(self):
        """Омальовує кулю з неоновим сяйвом."""
        self.canvas.clear()
        with self.canvas:
            # Зовнішнє сяйво
            glow_color = (self.color[0], self.color[1], self.color[2], 0.35)
            Color(*glow_color)
            Rectangle(
                pos=(self.x - 2, self.y - 2),
                size=(self.width + 4, self.height + 4),
            )
            # Ядро лазера
            Color(*self.color)
            Rectangle(
                pos=(self.x, self.y),
                size=(self.width, self.height),
            )


class PlayerShip(Widget):
    """Космічний корабель гравця з анімацією часточок двигуна."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.speed = PLAYER_SPEED
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN
        self.time_since_last_shot = self.fire_cooldown

        # Напрямок руху: -1 = ліворуч, 1 = праворуч, 0 = нерухомий
        self.move_direction = 0

        # Система часточок для анімації реактивного двигуна
        self.engine_particles: list[Particle] = []

        self.redraw()

    def set_move_direction(self, direction: int):
        """Встановлює напрямок горизонтального руху (-1, 0, 1)."""
        self.move_direction = direction

    def move_to_x(self, target_x: float, screen_width: float):
        """Плавне або пряме переміщення корабля пальцем (сенсорне керування)."""
        self.x = max(0.0, min(target_x - self.width / 2.0, screen_width - self.width))
        self.redraw()

    def update(self, dt: float, screen_width: float):
        """Оновлює стан корабля: рух, кулдаун стрільби, часточки."""
        self.time_since_last_shot += dt

        # Горизонтальний рух за кнопками або стрілками
        if self.move_direction != 0:
            self.x += self.move_direction * self.speed * dt
            self.x = max(0.0, min(self.x, screen_width - self.width))

        # Генерація часточок полум'я двигуна (анімація корабля)
        self._emit_engine_particles()

        # Оновлення існуючих часточок полум'я
        alive_particles = []
        for p in self.engine_particles:
            p.update(dt)
            if not p.is_dead:
                alive_particles.append(p)
        self.engine_particles = alive_particles

        self.redraw()

    def _emit_engine_particles(self):
        """Генерує нові часточки вихлопу з сопла двигуна."""
        engine_x = self.x + self.width / 2.0
        engine_y = self.y + 4.0

        for _ in range(2):
            vx = random.uniform(-18.0, 18.0)
            vy = random.uniform(-90.0, -160.0)
            size = random.uniform(3.5, 6.5)
            life = random.uniform(0.18, 0.35)

            # Перехід кольорів від полум'яно-жовтого до червоного
            r = 1.0
            g = random.uniform(0.35, 0.95)
            b = 0.1
            color = (r, g, b, 0.85)

            self.engine_particles.append(
                Particle(engine_x, engine_y, vx, vy, size, life, color)
            )

    def can_shoot(self) -> bool:
        """Перевіряє, чи завершився кулдаун для наступного пострілу."""
        return self.time_since_last_shot >= self.fire_cooldown

    def shoot(self) -> Bullet:
        """Створює кулю з центру корабля та скидає таймер кулдауну."""
        self.time_since_last_shot = 0.0
        bullet_x = self.x + self.width / 2.0 - BULLET_WIDTH / 2.0
        bullet_y = self.y + self.height
        return Bullet(bullet_x, bullet_y, is_player=True)

    def take_damage(self, amount: int):
        """Зменшує здоров'я гравця."""
        self.hp = max(0, self.hp - amount)

    def redraw(self):
        """Малює стилізований футуристичний корабель та полум'я часточок."""
        self.canvas.clear()
        with self.canvas:
            # 1. Часточки полум'я двигунів
            for p in self.engine_particles:
                alpha = p.color[3] * (1.0 - p.life / p.max_life)
                Color(p.color[0], p.color[1], p.color[2], alpha)
                Ellipse(pos=(p.x - p.size / 2.0, p.y - p.size / 2.0), size=(p.size, p.size))

            # 2. Корпус корабля (векторна графіка на Canvas)
            cx = self.x + self.width / 2.0
            cy = self.y

            # Крила (ліве і праве)
            Color(*COLOR_PLAYER_SECONDARY)
            Triangle(
                points=[
                    self.x, self.y + 10,
                    cx, self.y + self.height - 12,
                    self.x + self.width, self.y + 10,
                ]
            )

            # Основний фюзеляж (трикутник носової частини)
            Color(*COLOR_PLAYER_PRIMARY)
            Triangle(
                points=[
                    self.x + 8, self.y + 14,
                    cx, self.y + self.height,
                    self.x + self.width - 8, self.y + 14,
                ]
            )

            # Кабіна пілота (світіння ліхтаря)
            Color(*COLOR_PLAYER_ACCENT)
            Ellipse(
                pos=(cx - 4.5, self.y + self.height / 2.0),
                size=(9.0, 14.0),
            )

            # Сопло двигуна
            Color(0.8, 0.8, 0.8, 1.0)
            Rectangle(
                pos=(cx - 5.0, self.y + 2.0),
                size=(10.0, 6.0),
            )


class Enemy(Widget):
    """Корабель ворога: рухається вниз, стріляє та має HP."""

    def __init__(self, x: float, y: float, **kwargs):
        super().__init__(**kwargs)
        self.width = ENEMY_WIDTH
        self.height = ENEMY_HEIGHT
        self.x = x
        self.y = y
        self.max_hp = ENEMY_DEFAULT_HP
        self.hp = ENEMY_DEFAULT_HP
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)

        # Таймер стрільби
        self.fire_cooldown = random.uniform(
            ENEMY_FIRE_INTERVAL_MIN, ENEMY_FIRE_INTERVAL_MAX
        )
        self.time_since_last_shot = random.uniform(0.0, self.fire_cooldown * 0.7)

        self.redraw()

    def update(self, dt: float) -> Bullet | None:
        """Переміщує ворога вниз і перевіряє можливість пострілу."""
        self.y -= self.speed * dt
        self.time_since_last_shot += dt

        bullet = None
        if self.time_since_last_shot >= self.fire_cooldown:
            self.time_since_last_shot = 0.0
            self.fire_cooldown = random.uniform(
                ENEMY_FIRE_INTERVAL_MIN, ENEMY_FIRE_INTERVAL_MAX
            )
            bullet = self._shoot()

        self.redraw()
        return bullet

    def _shoot(self) -> Bullet:
        """Створює кулю ворога, спрямовану вниз."""
        bullet_x = self.x + self.width / 2.0 - BULLET_WIDTH / 2.0
        bullet_y = self.y - BULLET_HEIGHT
        return Bullet(bullet_x, bullet_y, is_player=False)

    def take_damage(self, amount: int):
        """Зменшує HP ворога."""
        self.hp = max(0, self.hp - amount)

    def is_out_of_bounds(self) -> bool:
        """Перевіряє, чи ворог вийшов за нижній край екрана."""
        return self.y < -self.height - 20

    def redraw(self):
        """Малює ворожий винищувач."""
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0

            # Крила ворога (спрямовані вперед/вниз)
            Color(*COLOR_ENEMY_SECONDARY)
            Triangle(
                points=[
                    self.x, self.y + self.height - 8,
                    cx, self.y + 4,
                    self.x + self.width, self.y + self.height - 8,
                ]
            )

            # Головний корпус
            Color(*COLOR_ENEMY_PRIMARY)
            Triangle(
                points=[
                    self.x + 8, self.y + self.height - 12,
                    cx, self.y,
                    self.x + self.width - 8, self.y + self.height - 12,
                ]
            )

            # Око / енергетичне ядро ворога
            Color(1.0, 1.0, 0.2, 0.9)
            Ellipse(
                pos=(cx - 4.0, self.y + self.height / 2.0 - 4.0),
                size=(8.0, 8.0),
            )

            # Міні смужка HP над ворогом (якщо отримав пошкодження)
            if self.hp < self.max_hp:
                bar_w = self.width
                bar_h = 3.0
                bar_x = self.x
                bar_y = self.y + self.height + 4.0

                # Фон смужки
                Color(0.2, 0.2, 0.2, 0.8)
                Rectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h))

                # Поточне здоров'я
                ratio = self.hp / self.max_hp
                Color(0.1, 0.9, 0.2, 0.9)
                Rectangle(pos=(bar_x, bar_y), size=(bar_w * ratio, bar_h))


def check_collision(rect_a: Widget, rect_b: Widget) -> bool:
    """Перевіряє перетин двох прямокутників (AABB Collision)."""
    return not (
        rect_a.x + rect_a.width < rect_b.x
        or rect_a.x > rect_b.x + rect_b.width
        or rect_a.y + rect_a.height < rect_b.y
        or rect_a.y > rect_b.y + rect_b.height
    )


def create_explosion(
    x: float, y: float, count: int = 24, base_color: tuple = (1.0, 0.5, 0.1, 1.0)
) -> list[Particle]:
    """Створює спалах часточок вибуху."""
    particles = []
    for _ in range(count):
        angle_speed = random.uniform(60.0, 240.0)
        angle = random.uniform(0.0, 6.28318)
        vx = angle_speed * random.uniform(0.5, 1.2) * (1 if random.random() > 0.5 else -1)
        vy = angle_speed * random.uniform(0.5, 1.2) * (1 if random.random() > 0.5 else -1)
        size = random.uniform(3.0, 7.0)
        life = random.uniform(0.25, 0.55)

        r = min(1.0, base_color[0] + random.uniform(-0.1, 0.1))
        g = min(1.0, max(0.0, base_color[1] + random.uniform(-0.2, 0.2)))
        b = min(1.0, max(0.0, base_color[2] + random.uniform(-0.1, 0.1)))
        color = (r, g, b, 0.95)

        particles.append(Particle(x, y, vx, vy, size, life, color))
    return particles
