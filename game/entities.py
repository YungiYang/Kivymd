"""Ігрові сутності: Гравець, Вороги, Кулі та Часточки."""

import random
import math
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
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
    """Окремий клас для куль гравця та ворогів з підтримкою спрямованих траєкторій (vx, vy)."""

    def __init__(
        self,
        x: float,
        y: float,
        is_player: bool = True,
        damage: int = None,
        speed: float = None,
        vx: float = 0.0,
        vy: float = None,
        color: tuple = None,
        width: float = None,
        height: float = None,
        hazard_type: str = "none",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.is_player = is_player
        self.hazard_type = hazard_type  # "none", "burn", "slow", "emp", "freeze"
        self.width = width if width is not None else BULLET_WIDTH
        self.height = height if height is not None else BULLET_HEIGHT
        self.x = x
        self.y = y
        self.vx = vx

        if is_player:
            default_vy = speed if speed is not None else BULLET_PLAYER_SPEED
            self.vy = vy if vy is not None else default_vy
            self.damage = damage if damage is not None else BULLET_PLAYER_DAMAGE
            self.color = color if color is not None else COLOR_BULLET_PLAYER
        else:
            default_vy = speed if speed is not None else BULLET_ENEMY_SPEED
            self.vy = vy if vy is not None else default_vy
            self.damage = damage if damage is not None else BULLET_ENEMY_DAMAGE
            self.color = color if color is not None else COLOR_BULLET_ENEMY

        self.redraw()

    def update(self, dt: float):
        """Переміщує кулю у відповідному напрямку (X та Y)."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.redraw()

    def is_out_of_bounds(self, screen_height: float) -> bool:
        """Перевіряє, чи вилетіла куля за межі ігрового поля."""
        return self.y > screen_height + 60 or self.y < -60 or self.x < -60 or self.x > 800

    def redraw(self):
        """Омальовує кулю з неоновим сяйвом або елементальним ефектом біому."""
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0
            cy = self.y + self.height / 2.0

            if self.hazard_type == "burn":
                # Вогняна куля лавового рівня
                Color(1.0, 0.35, 0.05, 0.45)
                Ellipse(pos=(cx - 8.0, cy - 8.0), size=(16.0, 16.0))
                Color(1.0, 0.75, 0.1, 0.95)
                Ellipse(pos=(cx - 4.5, cy - 5.0), size=(9.0, 10.0))
                Color(1.0, 1.0, 0.8, 1.0)
                Ellipse(pos=(cx - 2.0, cy - 2.0), size=(4.0, 4.0))

            elif self.hazard_type == "slow":
                # Гідро-торпеда водного рівня
                Color(0.1, 0.85, 0.95, 0.45)
                Ellipse(pos=(cx - 7.0, cy - 7.0), size=(14.0, 14.0))
                Color(0.2, 0.95, 0.8, 0.9)
                Ellipse(pos=(cx - 4.0, cy - 4.0), size=(8.0, 8.0))
                Color(1.0, 1.0, 1.0, 0.95)
                Ellipse(pos=(cx - 1.5, cy + 1.0), size=(3.0, 3.0))

            elif self.hazard_type == "emp":
                # Електрична кібер-іскра
                Color(0.85, 0.25, 1.0, 0.45)
                Ellipse(pos=(cx - 7.0, cy - 7.0), size=(14.0, 14.0))
                Color(0.9, 0.4, 1.0, 0.95)
                Line(points=[cx - 4, cy - 6, cx + 2, cy, cx - 2, cy + 2, cx + 4, cy + 6], width=2.0)

            elif self.hazard_type == "freeze":
                # Крижаний кристал
                Color(0.4, 0.85, 1.0, 0.45)
                Ellipse(pos=(cx - 7.0, cy - 7.0), size=(14.0, 14.0))
                Color(0.8, 0.95, 1.0, 0.95)
                Line(points=[cx, cy - 7, cx + 4, cy, cx, cy + 7, cx - 4, cy, cx, cy - 7], width=1.5)

            else:
                # Стандартний лазер
                glow_color = (self.color[0], self.color[1], self.color[2], 0.35)
                Color(*glow_color)
                Rectangle(
                    pos=(self.x - 2, self.y - 2),
                    size=(self.width + 4, self.height + 4),
                )
                Color(*self.color)
                Rectangle(
                    pos=(self.x, self.y),
                    size=(self.width, self.height),
                )


class LaserBeam(Widget):
    """Довгий безперервний фотонний лазер для корабля «Геліос»."""

    def __init__(
        self,
        x: float,
        y: float,
        height: float,
        damage_dps: int = 180,
        width: float = 20.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.damage_dps = damage_dps
        self.damage = int(damage_dps * 0.016)
        self.is_player = True
        self.is_beam = True
        self.time_alive = 0.0
        self.redraw()

    def update_beam(
        self, dt: float, player_cx: float, player_top: float, screen_height: float
    ):
        self.time_alive += dt
        self.x = player_cx - self.width / 2.0
        self.y = player_top
        self.height = max(100.0, screen_height - self.y + 40.0)
        self.damage = max(1, int(self.damage_dps * dt))
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            pulse = 0.85 + 0.15 * math.sin(self.time_alive * 28.0)
            glow_w = self.width * 1.9 * pulse
            cx = self.x + self.width / 2.0

            # 1. Зовнішній бірюзовий неоновий ареол
            Color(0.1, 0.95, 0.8, 0.30 * pulse)
            Rectangle(pos=(cx - glow_w / 2.0, self.y), size=(glow_w, self.height))

            # 2. Основний плазмовий промінь
            Color(0.2, 1.0, 0.75, 0.82)
            Rectangle(
                pos=(cx - self.width / 2.0, self.y),
                size=(self.width, self.height),
            )

            # 3. Білосніжне високотемпературне ядро
            Color(1.0, 1.0, 1.0, 0.95)
            core_w = max(4.0, self.width * 0.36)
            Rectangle(pos=(cx - core_w / 2.0, self.y), size=(core_w, self.height))


class PlasmaOrb(Widget):
    """Велика заряджена термоядерна сфера для корабля «Вулкан»."""

    def __init__(
        self,
        x: float,
        y: float,
        damage: int = 160,
        speed: float = 520.0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.width = 38.0
        self.height = 38.0
        self.x = x - self.width / 2.0
        self.y = y
        self.damage = damage
        self.speed = speed
        self.is_player = True
        self.is_plasma_orb = True
        self.time_alive = 0.0
        self.trail_particles: list[Particle] = []
        self.redraw()

    def update(self, dt: float):
        self.time_alive += dt
        self.y += self.speed * dt

        # Часточки плазмового шлейфу
        cx = self.x + self.width / 2.0
        cy = self.y + self.height / 2.0
        p = Particle(
            x=cx + random.uniform(-6.0, 6.0),
            y=cy - 10.0,
            vx=random.uniform(-20.0, 20.0),
            vy=random.uniform(-70.0, -160.0),
            size=random.uniform(5.0, 9.0),
            max_life=0.22,
            color=(1.0, random.uniform(0.4, 0.85), 0.1, 0.9),
        )
        self.trail_particles.append(p)
        alive = []
        for tp in self.trail_particles:
            tp.update(dt)
            if not tp.is_dead:
                alive.append(tp)
        self.trail_particles = alive
        self.redraw()

    def is_out_of_bounds(self, screen_height: float) -> bool:
        return self.y > screen_height + 50 or self.y < -50

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0
            cy = self.y + self.height / 2.0

            # Часточки шлейфу
            for tp in self.trail_particles:
                alpha = tp.color[3] * (1.0 - tp.life / tp.max_life)
                Color(tp.color[0], tp.color[1], tp.color[2], alpha)
                Ellipse(
                    pos=(tp.x - tp.size / 2.0, tp.y - tp.size / 2.0),
                    size=(tp.size, tp.size),
                )

            pulse = 1.0 + 0.12 * math.sin(self.time_alive * 20.0)
            r_glow = self.width * 1.35 * pulse

            # 1. Зовнішня плазмова корона
            Color(1.0, 0.45, 0.05, 0.45)
            Ellipse(pos=(cx - r_glow / 2.0, cy - r_glow / 2.0), size=(r_glow, r_glow))

            # 2. Гаряча плазмова оболонка
            Color(1.0, 0.75, 0.15, 0.85)
            Ellipse(
                pos=(cx - self.width / 2.0, cy - self.height / 2.0),
                size=(self.width, self.height),
            )

            # 3. Біле термоядерне ядро
            Color(1.0, 1.0, 0.9, 0.98)
            core_r = 16.0
            Ellipse(pos=(cx - core_r / 2.0, cy - core_r / 2.0), size=(core_r, core_r))


class PlayerShip(Widget):
    """Космічний корабель гравця з підтримкою різних конфігурацій, атак та анімацій."""

    def __init__(self, ship_id: str = "striker", **kwargs):
        super().__init__(**kwargs)
        self.ship_id = ship_id
        self.attack_type = "blaster"  # "blaster", "beam", "charge", "spread"
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.speed = PLAYER_SPEED
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN
        self.time_since_last_shot = self.fire_cooldown

        # Атрибути покращень (Upgrades)
        self.bullet_damage = BULLET_PLAYER_DAMAGE
        self.bullet_speed = BULLET_PLAYER_SPEED
        self.shot_level = 1
        self.shield = 0

        # Кольори оформлення
        self.primary_color = COLOR_PLAYER_PRIMARY
        self.secondary_color = COLOR_PLAYER_SECONDARY
        self.accent_color = COLOR_PLAYER_ACCENT

        # Спеціальні механіки атак
        self.is_beam_active = False
        self.beam_timer = 0.0
        self.beam_duration = 2.3
        self.charge_progress = 0.0

        # Напрямок руху: -1 = ліворуч, 1 = праворуч, 0 = нерухомий
        self.move_direction = 0

        # Система часточок для анімації реактивного двигуна
        self.engine_particles: list[Particle] = []
        self.burn_particles: list[Particle] = []

        # Статусні ефекти від біомів
        self.is_burning = False
        self.burn_timer = 0.0
        self.burn_tick_timer = 0.0

        self.is_slowed = False
        self.slow_timer = 0.0

        self.is_emp = False
        self.emp_timer = 0.0

        self.is_frozen = False
        self.freeze_timer = 0.0

        self.apply_ship_id(ship_id)
        self.redraw()

    def apply_burn(self, duration: float = 3.0):
        """Накладає ефект підпалу (DoT шкода щопівсекунди)."""
        self.is_burning = True
        self.burn_timer = max(self.burn_timer, duration)

    def apply_slow(self, duration: float = 2.5):
        """Накладає ефект водяного сповільнення (-35% швидкості)."""
        self.is_slowed = True
        self.slow_timer = max(self.slow_timer, duration)

    def apply_emp(self, duration: float = 1.8):
        """Накладає EMP-шок (порушує роботу гармат)."""
        self.is_emp = True
        self.emp_timer = max(self.emp_timer, duration)

    def apply_freeze(self, duration: float = 2.0):
        """Накладає ефект крижаної заморозки (-50% швидкості)."""
        self.is_frozen = True
        self.freeze_timer = max(self.freeze_timer, duration)

    def clear_status_effects(self):
        """Знімає всі активні аномальні статуси."""
        self.is_burning = False
        self.burn_timer = 0.0
        self.burn_tick_timer = 0.0
        self.is_slowed = False
        self.slow_timer = 0.0
        self.is_emp = False
        self.emp_timer = 0.0
        self.is_frozen = False
        self.freeze_timer = 0.0
        self.burn_particles.clear()

    def apply_ship_id(self, ship_id: str):
        """Застосовує параметри обраного корабля з каталогу."""
        from game.ships import get_ship_config

        cfg = get_ship_config(ship_id)
        self.ship_id = cfg.ship_id
        self.attack_type = cfg.attack_type
        self.width = cfg.width
        self.height = cfg.height
        self.max_hp = cfg.max_hp
        self.hp = cfg.max_hp
        self.speed = cfg.speed
        self.fire_cooldown = cfg.fire_cooldown
        self.bullet_damage = cfg.bullet_damage
        self.bullet_speed = cfg.bullet_speed
        self.shield = cfg.initial_shield
        self.primary_color = cfg.primary_color
        self.secondary_color = cfg.secondary_color
        self.accent_color = cfg.accent_color
        self.is_beam_active = False
        self.beam_timer = 0.0
        self.time_since_last_shot = cfg.fire_cooldown
        self.charge_progress = 0.0
        self.clear_status_effects()
        self.redraw()

    def reset_stats(self, ship_id: str | None = None):
        """Скидає всі характеристики гравця відповідно до поточного корабля."""
        target_ship = ship_id if ship_id is not None else self.ship_id
        self.apply_ship_id(target_ship)
        self.shot_level = 1
        self.time_since_last_shot = self.fire_cooldown
        self.move_direction = 0
        self.engine_particles.clear()
        self.clear_status_effects()
        self.redraw()

    def set_move_direction(self, direction: int):
        """Встановлює напрямок горизонтального руху (-1, 0, 1)."""
        self.move_direction = direction

    def move_to_x(self, target_x: float, screen_width: float):
        """Плавне або пряме переміщення корабля пальцем (сенсорне керування)."""
        self.x = max(0.0, min(target_x - self.width / 2.0, screen_width - self.width))
        self.redraw()

    def update(self, dt: float, screen_width: float):
        """Оновлює стан корабля: рух, кулдаун стрільби, статусні ефекти та часточки."""
        self.time_since_last_shot += dt

        # Оновлення статусних ефектів
        if self.is_burning:
            self.burn_timer -= dt
            self.burn_tick_timer += dt
            if self.burn_tick_timer >= 0.5:
                self.burn_tick_timer = 0.0
                self.hp = max(0, self.hp - 2)
            if self.burn_timer <= 0.0:
                self.is_burning = False
            self._emit_burn_particles()

        if self.is_slowed:
            self.slow_timer -= dt
            if self.slow_timer <= 0.0:
                self.is_slowed = False

        if self.is_emp:
            self.emp_timer -= dt
            if self.emp_timer <= 0.0:
                self.is_emp = False

        if self.is_frozen:
            self.freeze_timer -= dt
            if self.freeze_timer <= 0.0:
                self.is_frozen = False

        # Оновлення променя
        if self.attack_type == "beam" and self.is_beam_active:
            self.beam_timer -= dt
            if self.beam_timer <= 0.0:
                self.is_beam_active = False
                self.time_since_last_shot = 0.0

        # Оновлення заряджання плазмової сфери
        if self.attack_type == "charge":
            self.charge_progress = min(1.0, self.charge_progress + dt / 1.35)

        # Горизонтальний рух з урахуванням сповільнення або заморожування
        current_speed = self.speed
        if self.is_slowed:
            current_speed *= 0.65
        if self.is_frozen:
            current_speed *= 0.50

        if self.move_direction != 0:
            self.x += self.move_direction * current_speed * dt
            self.x = max(0.0, min(self.x, screen_width - self.width))

        # Генерація часточок двигуна
        self._emit_engine_particles()

        # Оновлення часточок полум'я
        alive_particles = []
        for p in self.engine_particles:
            p.update(dt)
            if not p.is_dead:
                alive_particles.append(p)
        self.engine_particles = alive_particles

        # Оновлення часточок підпалу
        alive_burn = []
        for p in self.burn_particles:
            p.update(dt)
            if not p.is_dead:
                alive_burn.append(p)
        self.burn_particles = alive_burn

        self.redraw()

    def _emit_burn_particles(self):
        """Генерує язики полум'я та іскри на палаючому кораблі."""
        cx = self.x + random.uniform(4.0, self.width - 4.0)
        cy = self.y + random.uniform(8.0, self.height)
        p = Particle(
            x=cx,
            y=cy,
            vx=random.uniform(-30.0, 30.0),
            vy=random.uniform(50.0, 120.0),
            size=random.uniform(3.5, 7.5),
            max_life=0.24,
            color=(1.0, random.uniform(0.2, 0.7), 0.05, 0.95),
        )
        self.burn_particles.append(p)

    def _emit_engine_particles(self):
        """Генерує нові часточки вихлопу з сопел двигуна відповідно до класу корабля."""
        cx = self.x + self.width / 2.0
        engine_y = self.y + 4.0

        r = self.accent_color[0]
        g = self.accent_color[1]
        b = self.accent_color[2]

        for _ in range(2):
            vx = random.uniform(-16.0, 16.0)
            vy = random.uniform(-90.0, -170.0)
            size = random.uniform(3.5, 6.5)
            life = random.uniform(0.18, 0.32)
            color = (r, g, b, 0.85)
            self.engine_particles.append(
                Particle(cx, engine_y, vx, vy, size, life, color)
            )

    def can_shoot(self) -> bool:
        """Перевіряє готовність до атаки."""
        if self.attack_type == "beam":
            return not self.is_beam_active and self.time_since_last_shot >= self.fire_cooldown
        return self.time_since_last_shot >= self.fire_cooldown

    def shoot_bullets(self) -> list[Bullet | PlasmaOrb]:
        """Створює снаряди відповідно до класу корабля та активних покращень."""
        cx = self.x + self.width / 2.0
        by = self.y + self.height

        # 1. Променевий корабель «Геліос»
        if self.attack_type == "beam":
            if not self.is_beam_active:
                self.is_beam_active = True
                self.beam_timer = self.beam_duration
                self.time_since_last_shot = 0.0
            return []

        # 2. Плазмовий дредноут «Вулкан» (великий заряд)
        if self.attack_type == "charge":
            if self.charge_progress >= 0.95:
                self.charge_progress = 0.0
                self.time_since_last_shot = 0.0
                orb = PlasmaOrb(
                    cx,
                    by,
                    damage=self.bullet_damage + (self.shot_level - 1) * 35,
                    speed=self.bullet_speed,
                )
                return [orb]
            else:
                # Допоміжні легкі лазери під час заряджання
                self.time_since_last_shot = 0.0
                b1 = Bullet(
                    self.x + 8.0,
                    by,
                    is_player=True,
                    damage=14,
                    speed=self.bullet_speed,
                    color=(1.0, 0.8, 0.2, 1.0),
                )
                b2 = Bullet(
                    self.x + self.width - 14.0,
                    by,
                    is_player=True,
                    damage=14,
                    speed=self.bullet_speed,
                    color=(1.0, 0.8, 0.2, 1.0),
                )
                return [b1, b2]

        # 3. Штормовий перехоплювач «Валькірія» (віяловий залп)
        if self.attack_type == "spread":
            self.time_since_last_shot = 0.0
            b1 = Bullet(
                cx - 3.0,
                by + 4.0,
                is_player=True,
                damage=self.bullet_damage,
                vx=0.0,
                vy=self.bullet_speed,
                color=self.accent_color,
            )
            b2 = Bullet(
                cx - 8.0,
                by,
                is_player=True,
                damage=self.bullet_damage,
                vx=-90.0,
                vy=self.bullet_speed * 0.95,
                color=self.accent_color,
            )
            b3 = Bullet(
                cx + 2.0,
                by,
                is_player=True,
                damage=self.bullet_damage,
                vx=90.0,
                vy=self.bullet_speed * 0.95,
                color=self.accent_color,
            )
            if self.shot_level >= 2:
                b4 = Bullet(
                    cx - 12.0,
                    by - 6.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    vx=-170.0,
                    vy=self.bullet_speed * 0.90,
                    color=self.accent_color,
                )
                b5 = Bullet(
                    cx + 6.0,
                    by - 6.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    vx=170.0,
                    vy=self.bullet_speed * 0.90,
                    color=self.accent_color,
                )
                return [b1, b2, b3, b4, b5]
            return [b1, b2, b3]

        # 4. Самонавідна ракета для «Нова» (missile)
        if self.attack_type == "missile":
            self.time_since_last_shot = 0.0
            b1 = Bullet(
                cx - 6.0,
                by,
                is_player=True,
                damage=self.bullet_damage,
                speed=self.bullet_speed,
                color=(1.0, 0.35, 0.15, 1.0),
                width=12.0,
                height=22.0,
            )
            if self.shot_level >= 2:
                b2 = Bullet(
                    self.x + 2.0,
                    by - 8.0,
                    is_player=True,
                    damage=self.bullet_damage // 2,
                    speed=self.bullet_speed,
                    vx=-60.0,
                    color=(1.0, 0.6, 0.2, 1.0),
                    width=8.0,
                    height=16.0,
                )
                b3 = Bullet(
                    self.x + self.width - 10.0,
                    by - 8.0,
                    is_player=True,
                    damage=self.bullet_damage // 2,
                    speed=self.bullet_speed,
                    vx=60.0,
                    color=(1.0, 0.6, 0.2, 1.0),
                    width=8.0,
                    height=16.0,
                )
                return [b1, b2, b3]
            return [b1]

        # 5. Дуальний квантовий лазер для «Тінь» (dual_beam)
        if self.attack_type == "dual_beam":
            self.time_since_last_shot = 0.0
            b1 = Bullet(
                self.x + 6.0,
                by,
                is_player=True,
                damage=self.bullet_damage,
                speed=self.bullet_speed,
                color=(0.7, 0.4, 1.0, 1.0),
                width=5.0,
                height=24.0,
            )
            b2 = Bullet(
                self.x + self.width - 11.0,
                by,
                is_player=True,
                damage=self.bullet_damage,
                speed=self.bullet_speed,
                color=(0.7, 0.4, 1.0, 1.0),
                width=5.0,
                height=24.0,
            )
            if self.shot_level >= 2:
                b3 = Bullet(
                    cx - 3.0,
                    by + 6.0,
                    is_player=True,
                    damage=self.bullet_damage + 10,
                    speed=self.bullet_speed * 1.1,
                    color=(0.95, 0.6, 1.0, 1.0),
                    width=6.0,
                    height=28.0,
                )
                return [b1, b2, b3]
            return [b1, b2]

        # 6. Базовий штурмовик «Фенікс» (blaster)
        self.time_since_last_shot = 0.0
        bullets = []
        if self.shot_level == 1:
            bx = cx - BULLET_WIDTH / 2.0
            bullets.append(
                Bullet(
                    bx,
                    by,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
        elif self.shot_level == 2:
            bx1 = self.x + 8.0
            bx2 = self.x + self.width - 8.0 - BULLET_WIDTH
            bullets.append(
                Bullet(
                    bx1,
                    by - 4.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
            bullets.append(
                Bullet(
                    bx2,
                    by - 4.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
        else:
            bx1 = self.x + 4.0
            bx2 = cx - BULLET_WIDTH / 2.0
            bx3 = self.x + self.width - 4.0 - BULLET_WIDTH
            bullets.append(
                Bullet(
                    bx1,
                    by - 6.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
            bullets.append(
                Bullet(
                    bx2,
                    by,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
            bullets.append(
                Bullet(
                    bx3,
                    by - 6.0,
                    is_player=True,
                    damage=self.bullet_damage,
                    speed=self.bullet_speed,
                )
            )
        return bullets

    def shoot(self) -> Bullet:
        """Створює кулю з центру корабля (для зворотної сумісності з тестами)."""
        bullets = self.shoot_bullets()
        if bullets:
            return bullets[0]
        return Bullet(
            self.x + self.width / 2.0 - BULLET_WIDTH / 2.0,
            self.y + self.height,
            is_player=True,
            damage=self.bullet_damage,
            speed=self.bullet_speed,
        )

    def take_damage(self, amount: int) -> bool:
        """Зменшує HP або поглинає удар щитом."""
        if self.shield > 0:
            self.shield -= 1
            self.redraw()
            return True
        self.hp = max(0, self.hp - amount)
        return False

    def redraw(self):
        """Малює індивідуальну модель корабля залежно від ship_id."""
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0
            cy = self.y

            # 1. Часточки полум'я двигунів
            for p in self.engine_particles:
                alpha = p.color[3] * (1.0 - p.life / p.max_life)
                Color(p.color[0], p.color[1], p.color[2], alpha)
                Ellipse(
                    pos=(p.x - p.size / 2.0, p.y - p.size / 2.0),
                    size=(p.size, p.size),
                )

            # 2. Корпус корабля за класами
            if self.ship_id == "beam_titan":
                # Фотонний крейсер «Геліос»
                Color(*self.secondary_color)
                Rectangle(
                    pos=(self.x + 4.0, cy + 6.0),
                    size=(self.width - 8.0, self.height - 18.0),
                )
                Color(*self.primary_color)
                Triangle(
                    points=[
                        self.x + 2.0, cy + 12.0,
                        cx, cy + self.height,
                        self.x + self.width - 2.0, cy + 12.0,
                    ]
                )
                # Квантова фокусуюча лінза
                Color(*self.accent_color)
                Ellipse(pos=(cx - 8.0, cy + self.height - 14.0), size=(16.0, 16.0))
                Color(1.0, 1.0, 1.0, 0.95)
                Ellipse(pos=(cx - 4.0, cy + self.height - 10.0), size=(8.0, 8.0))

            elif self.ship_id == "plasma_vanguard":
                # Дредноут «Вулкан»
                Color(*self.secondary_color)
                Rectangle(
                    pos=(self.x + 2.0, cy + 6.0),
                    size=(self.width - 4.0, self.height - 18.0),
                )
                Color(*self.primary_color)
                Triangle(
                    points=[
                        self.x + 6.0, cy + 8.0,
                        cx, cy + self.height - 4.0,
                        self.x + self.width - 6.0, cy + 8.0,
                    ]
                )
                # Пульсуючий плазмовий заряд на носі (росте під час заряджання!)
                core_size = 8.0 + 14.0 * self.charge_progress
                Color(1.0, 0.45, 0.1, 0.85)
                Ellipse(
                    pos=(cx - core_size / 2.0, cy + self.height - core_size + 2.0),
                    size=(core_size, core_size),
                )
                Color(1.0, 0.9, 0.25, 1.0)
                Ellipse(
                    pos=(cx - core_size * 0.25, cy + self.height - core_size * 0.75),
                    size=(core_size * 0.5, core_size * 0.5),
                )

            elif self.ship_id == "storm_valkyrie":
                # Перехоплювач «Валькірія»
                Color(*self.secondary_color)
                Triangle(
                    points=[
                        self.x, cy + 14.0,
                        cx, cy + self.height,
                        self.x + self.width, cy + 14.0,
                    ]
                )
                Color(*self.primary_color)
                Triangle(
                    points=[
                        self.x + 8.0, cy + 8.0,
                        cx, cy + self.height - 2.0,
                        self.x + self.width - 8.0, cy + 8.0,
                    ]
                )
                # Неонові стабілізатори
                Color(*self.accent_color)
                Line(points=[self.x + 2.0, cy + 8.0, cx, cy + self.height * 0.6], width=1.5)
                Line(points=[self.x + self.width - 2.0, cy + 8.0, cx, cy + self.height * 0.6], width=1.5)
                # Кабіна
                Color(0.2, 0.95, 1.0, 0.95)
                Ellipse(pos=(cx - 4.0, cy + self.height * 0.4), size=(8.0, 14.0))

            else:
                # Базовий штурмовик «Фенікс»
                Color(*self.secondary_color)
                Triangle(
                    points=[
                        self.x, cy + 10.0,
                        cx, cy + self.height - 12.0,
                        self.x + self.width, cy + 10.0,
                    ]
                )
                Color(*self.primary_color)
                Triangle(
                    points=[
                        self.x + 8.0, cy + 14.0,
                        cx, cy + self.height,
                        self.x + self.width - 8.0, cy + 14.0,
                    ]
                )
                Color(*self.accent_color)
                Ellipse(pos=(cx - 4.5, cy + self.height / 2.0), size=(9.0, 14.0))
                Color(0.8, 0.8, 0.8, 1.0)
                Rectangle(pos=(cx - 5.0, cy + 2.0), size=(10.0, 6.0))

            # 3. Енергетичний силовий щит (якщо є активні заряди)
            if self.shield > 0:
                shield_radius = self.width * 0.72
                Color(0.2, 0.85, 1.0, 0.5)
                Line(circle=(cx, cy + self.height / 2.0, shield_radius), width=2.0)
                Color(0.2, 0.85, 1.0, 0.12)
                Ellipse(
                    pos=(cx - shield_radius, cy + self.height / 2.0 - shield_radius),
                    size=(shield_radius * 2.0, shield_radius * 2.0),
                )

            # 4. Ефекти статусів (підпал, заморозка, сповільнення)
            if self.is_burning:
                for bp in self.burn_particles:
                    alpha = bp.color[3] * (1.0 - bp.life / bp.max_life)
                    Color(bp.color[0], bp.color[1], bp.color[2], alpha)
                    Ellipse(pos=(bp.x - bp.size / 2.0, bp.y - bp.size / 2.0), size=(bp.size, bp.size))
                Color(1.0, 0.35, 0.05, 0.35)
                Line(rounded_rectangle=[self.x - 4, cy - 4, self.width + 8, self.height + 8, 8], width=2.0)

            if self.is_frozen:
                Color(0.4, 0.9, 1.0, 0.40)
                Line(rounded_rectangle=[self.x - 3, cy - 3, self.width + 6, self.height + 6, 6], width=2.0)

            if self.is_slowed:
                Color(0.1, 0.85, 0.95, 0.30)
                Line(rounded_rectangle=[self.x - 2, cy - 2, self.width + 4, self.height + 4, 4], width=1.5)


class FloatingText(Widget):
    """Спливаючий текст для відображення шкоди, очок та комбо."""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        color: tuple = (1.0, 1.0, 0.2, 1.0),
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (150, 24)
        self.x = x - 75.0
        self.y = y
        self.pos = (self.x, self.y)
        self.life = 0.0
        self.max_life = 0.75
        self.vy = 75.0
        self.is_dead = False
        self.base_color = color

        self.label = MDLabel(
            text=text,
            halign="center",
            bold=True,
            theme_text_color="Custom",
            text_color=color,
            font_style="Title",
            role="small",
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self.label)

    def update(self, dt: float):
        self.life += dt
        if self.life >= self.max_life:
            self.is_dead = True
            return
        self.y += self.vy * dt
        self.pos = (self.x, self.y)
        self.label.pos = self.pos
        progress = self.life / self.max_life
        alpha = max(0.0, 1.0 - progress)
        self.label.text_color = (
            self.base_color[0],
            self.base_color[1],
            self.base_color[2],
            self.base_color[3] * alpha,
        )


class Enemy(Widget):
    """Корабель ворога: підтримує типи 'fighter', 'scout', 'sniper', 'bomber', 'cruiser' та 5 біомів."""

    def __init__(
        self,
        x: float,
        y: float,
        enemy_type: str = "fighter",
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

        if enemy_type == "scout":
            self.width = 36
            self.height = 36
            self.max_hp = 20
            self.hp = 20
            self.speed = random.uniform(210.0, 270.0)
            self.score_value = 150
            self.fire_cooldown = random.uniform(2.0, 3.5)
        elif enemy_type == "sniper":
            self.width = 44
            self.height = 46
            self.max_hp = 30
            self.hp = 30
            self.speed = random.uniform(90.0, 125.0)
            self.score_value = 220
            self.fire_cooldown = random.uniform(2.2, 3.2)
        elif enemy_type == "bomber":
            self.width = 52
            self.height = 48
            self.max_hp = 55
            self.hp = 55
            self.speed = random.uniform(95.0, 135.0)
            self.score_value = 280
            self.fire_cooldown = random.uniform(1.8, 2.8)
        elif enemy_type == "cruiser":
            self.width = 64
            self.height = 58
            self.max_hp = 90
            self.hp = 90
            self.speed = random.uniform(65.0, 95.0)
            self.score_value = 380
            self.fire_cooldown = random.uniform(1.3, 2.0)
        else:
            self.enemy_type = "fighter"
            self.width = ENEMY_WIDTH
            self.height = ENEMY_HEIGHT
            self.max_hp = ENEMY_DEFAULT_HP
            self.hp = ENEMY_DEFAULT_HP
            self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
            self.score_value = 100
            self.fire_cooldown = random.uniform(
                ENEMY_FIRE_INTERVAL_MIN, ENEMY_FIRE_INTERVAL_MAX
            )

        self.time_since_last_shot = random.uniform(0.0, self.fire_cooldown * 0.7)
        self.redraw()

    @property
    def hazard_type(self) -> str:
        """Повертає тип аномального статусу відповідно до поточного біому."""
        from game.biomes import get_biome_config
        return get_biome_config(self.biome).hazard_type

    def shoot(self, player_pos: tuple = None) -> list[Bullet]:
        """Публічний метод виклику пострілу ворога (повертає список куль)."""
        res = self._shoot(player_pos)
        return res if isinstance(res, list) else [res]

    def update(self, dt: float, player_pos: tuple = None) -> list[Bullet] | Bullet | None:
        """Переміщує ворога відповідно до патерну та генерує постріли."""
        self.y -= self.speed * dt
        self.time_alive += dt
        self.time_since_last_shot += dt

        # Зигзагоподібний маневр для швидких розвідників
        if self.enemy_type == "scout":
            self.x = self.spawn_x + math.sin(self.time_alive * 4.2) * 55.0

        shots = None
        if self.time_since_last_shot >= self.fire_cooldown:
            self.time_since_last_shot = 0.0
            if self.enemy_type == "cruiser":
                self.fire_cooldown = random.uniform(1.3, 2.0)
            elif self.enemy_type == "sniper":
                self.fire_cooldown = random.uniform(2.2, 3.2)
            elif self.enemy_type == "bomber":
                self.fire_cooldown = random.uniform(1.8, 2.8)
            elif self.enemy_type == "scout":
                self.fire_cooldown = random.uniform(2.0, 3.5)
            else:
                self.fire_cooldown = random.uniform(
                    ENEMY_FIRE_INTERVAL_MIN, ENEMY_FIRE_INTERVAL_MAX
                )
            shots = self._shoot(player_pos)

        self.redraw()
        return shots

    def _shoot(self, player_pos: tuple = None) -> list[Bullet] | Bullet:
        """Створює різні типи атак залежно від класу ворога та активного біому."""
        cx = self.x + self.width / 2.0
        cy = self.y - BULLET_HEIGHT

        # Аномальні ефекти куль відповідно до біому
        hazard = "none"
        b_color = None
        if self.biome == "lava":
            hazard = "burn"
            b_color = (1.0, 0.40, 0.05, 1.0)
        elif self.biome == "water":
            hazard = "slow"
            b_color = (0.15, 0.90, 0.95, 1.0)
        elif self.biome == "cyber_storm":
            hazard = "emp"
            b_color = (0.85, 0.25, 1.0, 1.0)
        elif self.biome == "ice":
            hazard = "freeze"
            b_color = (0.50, 0.90, 1.0, 1.0)

        if self.enemy_type == "sniper":
            # Снайпер: прицільний постріл безпосередньо у гравця
            px, py = player_pos if player_pos else (cx, 0.0)
            dx = px - cx
            dy = py - cy
            dist = max(1.0, math.hypot(dx, dy))
            vx = (dx / dist) * 440.0
            vy = (dy / dist) * 440.0
            col = b_color if b_color else (1.0, 0.2, 0.35, 1.0)
            return Bullet(
                cx - 3.0,
                cy,
                is_player=False,
                damage=20,
                vx=vx,
                vy=vy,
                color=col,
                hazard_type=hazard,
            )
        elif self.enemy_type == "bomber":
            # Бомбардувальник: 3-променевий віяловий залп
            col = b_color if b_color else (1.0, 0.55, 0.1, 1.0)
            b1 = Bullet(
                cx - 3.0, cy, is_player=False, damage=14, vx=-110.0, vy=-280.0, color=col, hazard_type=hazard
            )
            b2 = Bullet(
                cx - 3.0, cy, is_player=False, damage=14, vx=0.0, vy=-300.0, color=col, hazard_type=hazard
            )
            b3 = Bullet(
                cx - 3.0, cy, is_player=False, damage=14, vx=110.0, vy=-280.0, color=col, hazard_type=hazard
            )
            return [b1, b2, b3]
        elif self.enemy_type == "cruiser":
            # Крейсер: спарений важкий плазмовий залп
            col = b_color if b_color else COLOR_BULLET_ENEMY
            b1 = Bullet(self.x + 8.0, cy, is_player=False, damage=22, speed=-380.0, color=col, hazard_type=hazard)
            b2 = Bullet(self.x + self.width - 14.0, cy, is_player=False, damage=22, speed=-380.0, color=col, hazard_type=hazard)
            return [b1, b2]
        elif self.enemy_type == "scout":
            # Розвідник: легка швидка куля
            col = b_color if b_color else (1.0, 0.9, 0.2, 1.0)
            return Bullet(cx - 2.0, cy, is_player=False, damage=10, speed=-440.0, color=col, hazard_type=hazard)
        else:
            # Винищувач: стандартний постріл
            col = b_color if b_color else COLOR_BULLET_ENEMY
            return Bullet(cx - BULLET_WIDTH / 2.0, cy, is_player=False, color=col, hazard_type=hazard)

    def take_damage(self, amount: int):
        """Зменшує HP ворога."""
        self.hp = max(0, self.hp - amount)

    def is_out_of_bounds(self) -> bool:
        """Перевіряє, чи ворог вийшов за нижній край екрана."""
        return self.y < -self.height - 20

    def redraw(self):
        """Малює ворожий корабель відповідно до його класу."""
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0

            if self.enemy_type == "scout":
                # Швидкий розвідник (золотаво-помаранчевий)
                Color(1.0, 0.45, 0.1, 1.0)
                Triangle(
                    points=[
                        self.x, self.y + self.height - 4,
                        cx, self.y,
                        self.x + self.width, self.y + self.height - 4,
                    ]
                )
                Color(1.0, 0.85, 0.2, 1.0)
                Triangle(
                    points=[
                        self.x + 6, self.y + self.height,
                        cx, self.y + 6,
                        self.x + self.width - 6, self.y + self.height,
                    ]
                )
                Color(0.2, 0.95, 1.0, 0.95)
                Ellipse(pos=(cx - 3.0, self.y + 12.0), size=(6.0, 6.0))

            elif self.enemy_type == "sniper":
                # Снайпер (видовжений бірюзово-фіолетовий корпус з лазерним прицілом)
                Color(0.2, 0.75, 0.85, 1.0)
                Triangle(
                    points=[
                        self.x + 4, self.y + self.height,
                        cx, self.y,
                        self.x + self.width - 4, self.y + self.height,
                    ]
                )
                Color(0.65, 0.15, 0.85, 1.0)
                Rectangle(pos=(cx - 4.0, self.y + 10.0), size=(8.0, self.height - 14.0))
                Color(1.0, 0.1, 0.3, 1.0)
                Ellipse(pos=(cx - 3.5, self.y + 6.0), size=(7.0, 7.0))

            elif self.enemy_type == "bomber":
                # Бомбардувальник (широкі помаранчеві крила)
                Color(1.0, 0.45, 0.15, 1.0)
                Triangle(
                    points=[
                        self.x, self.y + self.height - 6,
                        cx, self.y + 6,
                        self.x + self.width, self.y + self.height - 6,
                    ]
                )
                Color(0.9, 0.75, 0.1, 1.0)
                Rectangle(pos=(self.x + 10, self.y + 12), size=(self.width - 20, 16))
                Color(1.0, 0.1, 0.1, 1.0)
                Ellipse(pos=(cx - 5.0, self.y + 14.0), size=(10.0, 10.0))

            elif self.enemy_type == "cruiser":
                # Важкий броньований крейсер (темно-фіолетовий з червоними гарматами)
                Color(0.9, 0.2, 0.35, 1.0)
                Triangle(
                    points=[
                        self.x, self.y + self.height - 10,
                        cx, self.y + 2,
                        self.x + self.width, self.y + self.height - 10,
                    ]
                )
                Color(0.45, 0.15, 0.65, 1.0)
                Rectangle(
                    pos=(self.x + 12, self.y + 8),
                    size=(self.width - 24, self.height - 14),
                )
                Color(1.0, 0.15, 0.15, 1.0)
                Ellipse(pos=(cx - 6.0, self.y + 16.0), size=(12.0, 12.0))
                Color(1.0, 0.8, 0.2, 1.0)
                Ellipse(pos=(cx - 3.0, self.y + 19.0), size=(6.0, 6.0))

            else:
                # Стандартний винищувач (червоно-помаранчевий)
                Color(*COLOR_ENEMY_SECONDARY)
                Triangle(
                    points=[
                        self.x, self.y + self.height - 8,
                        cx, self.y + 4,
                        self.x + self.width, self.y + self.height - 8,
                    ]
                )
                Color(*COLOR_ENEMY_PRIMARY)
                Triangle(
                    points=[
                        self.x + 8, self.y + self.height - 12,
                        cx, self.y,
                        self.x + self.width - 8, self.y + self.height - 12,
                    ]
                )
                Color(1.0, 1.0, 0.2, 0.9)
                Ellipse(
                    pos=(cx - 4.0, self.y + self.height / 2.0 - 4.0),
                    size=(8.0, 8.0),
                )

            # Міні смужка HP над ворогом (якщо пошкоджений або для важких кораблів)
            if self.hp < self.max_hp or self.enemy_type in ("cruiser", "bomber"):
                bar_w = self.width
                bar_h = 4.0
                bar_x = self.x
                bar_y = self.y + self.height + 4.0

                Color(0.12, 0.16, 0.25, 0.85)
                Rectangle(pos=(bar_x, bar_y), size=(bar_w, bar_h))

                ratio = max(0.0, min(1.0, self.hp / self.max_hp))
                if ratio > 0.5:
                    Color(0.2, 0.95, 0.35, 0.95)
                elif ratio > 0.25:
                    Color(1.0, 0.85, 0.2, 0.95)
                else:
                    Color(1.0, 0.25, 0.25, 0.95)
                Rectangle(pos=(bar_x, bar_y), size=(bar_w * ratio, bar_h))


class Boss(Widget):
    """Гігантський флагман-бос із фазами бою, біомними атаками та масштабуванням складності."""

    def __init__(
        self,
        x: float,
        y: float,
        boss_level: int = 1,
        biome: str = "space",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.boss_level = boss_level
        self.biome = biome
        self.width = 114
        self.height = 76
        self.x = x
        self.y = y
        self.target_y = 0.0
        self.entered = False

        # Масштабування характеристик відповідно до рівня боса
        self.max_hp = 300 + (boss_level - 1) * 200
        self.hp = self.max_hp
        self.speed = 75.0 + min(65.0, boss_level * 15.0)
        self.score_value = 1200 + boss_level * 600
        self.move_dir = 1
        self.time_alive = 0.0

        # Атакуючі патерни (чергування 3 режимів)
        self.attack_mode = 0
        self.fire_cooldown = max(0.85, 1.85 - boss_level * 0.14)
        self.time_since_last_shot = 0.0

        # Система часточок двигунів боса
        self.engine_particles: list[Particle] = []
        self.redraw()

    @property
    def hazard_type(self) -> str:
        """Повертає тип аномального статусу відповідно до поточного біому."""
        from game.biomes import get_biome_config
        return get_biome_config(self.biome).hazard_type

    def shoot_fan(self) -> list[Bullet]:
        """Допоміжний метод віялового залпу боса."""
        self.attack_mode = 0
        return self._execute_attack(None)

    def update(
        self, dt: float, player_pos: tuple, screen_w: float, screen_h: float
    ) -> list[Bullet]:
        """Оновлює рух боса, анімацію двигунів та генерує атаки."""
        self.time_alive += dt
        self.time_since_last_shot += dt
        self.target_y = screen_h - 148.0

        # Фаза появи: плавний спуск зверху
        if not self.entered:
            self.y -= 120.0 * dt
            if self.y <= self.target_y:
                self.y = self.target_y
                self.entered = True
        else:
            # Фаза бою: горизонтальне патрулювання
            self.x += self.move_dir * self.speed * dt
            if self.x <= 12.0:
                self.x = 12.0
                self.move_dir = 1
            elif self.x >= screen_w - self.width - 12.0:
                self.x = screen_w - self.width - 12.0
                self.move_dir = -1

        # Часточки двигунів боса
        self._emit_engine_particles()
        alive_p = []
        for p in self.engine_particles:
            p.update(dt)
            if not p.is_dead:
                alive_p.append(p)
        self.engine_particles = alive_p

        # Постріли
        bullets = []
        if self.entered and self.time_since_last_shot >= self.fire_cooldown:
            self.time_since_last_shot = 0.0
            bullets = self._execute_attack(player_pos)
            self.attack_mode = (self.attack_mode + 1) % 3

        self.redraw()
        return bullets

    def _execute_attack(self, player_pos: tuple) -> list[Bullet]:
        bullets = []
        cx = self.x + self.width / 2.0
        cy = self.y

        hazard = "none"
        b_color = None
        if self.biome == "lava":
            hazard = "burn"
            b_color = (1.0, 0.35, 0.05, 1.0)
        elif self.biome == "water":
            hazard = "slow"
            b_color = (0.15, 0.90, 0.95, 1.0)
        elif self.biome == "cyber_storm":
            hazard = "emp"
            b_color = (0.85, 0.25, 1.0, 1.0)
        elif self.biome == "ice":
            hazard = "freeze"
            b_color = (0.50, 0.90, 1.0, 1.0)

        if self.attack_mode == 0:
            # Режим 1: 5-променевий віяловий залп
            angles = [-160.0, -80.0, 0.0, 80.0, 160.0]
            col = b_color if b_color else (1.0, 0.25, 0.25, 1.0)
            for vx in angles:
                bullets.append(
                    Bullet(
                        cx - 3.0,
                        cy - 12.0,
                        is_player=False,
                        damage=16,
                        vx=vx,
                        vy=-300.0,
                        color=col,
                        hazard_type=hazard,
                    )
                )
        elif self.attack_mode == 1:
            # Режим 2: Прицільний подвійний вогонь по гравцеві
            px, py = player_pos if player_pos else (cx, 0.0)
            dx = px - cx
            dy = py - cy
            dist = max(1.0, math.hypot(dx, dy))
            vx = (dx / dist) * 420.0
            vy = (dy / dist) * 420.0
            col = b_color if b_color else (1.0, 0.15, 0.8, 1.0)
            bullets.append(
                Bullet(
                    self.x + 16.0,
                    cy - 10.0,
                    is_player=False,
                    damage=22,
                    vx=vx,
                    vy=vy,
                    color=col,
                    hazard_type=hazard,
                )
            )
            bullets.append(
                Bullet(
                    self.x + self.width - 22.0,
                    cy - 10.0,
                    is_player=False,
                    damage=22,
                    vx=vx,
                    vy=vy,
                    color=col,
                    hazard_type=hazard,
                )
            )
        else:
            # Режим 3: Плазмовий шквал з гармат крил
            col = b_color if b_color else (1.0, 0.8, 0.2, 1.0)
            center_col = b_color if b_color else (1.0, 0.3, 0.1, 1.0)
            bullets.append(
                Bullet(
                    self.x + 8.0,
                    cy - 10.0,
                    is_player=False,
                    damage=18,
                    vx=-40.0,
                    vy=-360.0,
                    color=col,
                    hazard_type=hazard,
                )
            )
            bullets.append(
                Bullet(
                    cx - 3.0,
                    cy - 14.0,
                    is_player=False,
                    damage=24,
                    vx=0.0,
                    vy=-380.0,
                    color=center_col,
                    hazard_type=hazard,
                )
            )
            bullets.append(
                Bullet(
                    self.x + self.width - 14.0,
                    cy - 10.0,
                    is_player=False,
                    damage=18,
                    vx=40.0,
                    vy=-360.0,
                    color=col,
                    hazard_type=hazard,
                )
            )
        return bullets

    def _emit_engine_particles(self):
        engine_y = self.y + self.height - 6.0
        for ex in [self.x + 24.0, self.x + self.width - 24.0]:
            p = Particle(
                x=ex,
                y=engine_y,
                vx=random.uniform(-15.0, 15.0),
                vy=random.uniform(70.0, 130.0),
                size=random.uniform(4.0, 7.0),
                max_life=0.25,
                color=(1.0, random.uniform(0.2, 0.7), 0.1, 0.85),
            )
            self.engine_particles.append(p)

    def take_damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            cx = self.x + self.width / 2.0
            cy = self.y

            # Часточки полум'я важких двигунів
            for p in self.engine_particles:
                alpha = p.color[3] * (1.0 - p.life / p.max_life)
                Color(p.color[0], p.color[1], p.color[2], alpha)
                Ellipse(pos=(p.x - p.size / 2, p.y - p.size / 2), size=(p.size, p.size))

            # 1. Важка броньована основа (крила та фюзеляж)
            Color(0.25, 0.08, 0.32, 1.0)
            Triangle(
                points=[
                    self.x, cy + self.height - 10,
                    cx, cy + 4,
                    self.x + self.width, cy + self.height - 10,
                ]
            )

            # 2. Основна надбудова корпусу
            Color(0.55, 0.12, 0.45, 1.0)
            Rectangle(
                pos=(self.x + 18, cy + 18),
                size=(self.width - 36, self.height - 30),
            )

            # 3. Бортові гарматні батареї
            Color(0.85, 0.15, 0.25, 1.0)
            Rectangle(pos=(self.x + 8, cy + 8), size=(10, 24))
            Rectangle(pos=(self.x + self.width - 18, cy + 8), size=(10, 24))

            # 4. Командний місток і термоядерний реактор (пульсуюче ядро)
            Color(1.0, 0.2, 0.2, 0.95)
            Ellipse(pos=(cx - 10.0, cy + 28.0), size=(20.0, 20.0))
            Color(1.0, 0.9, 0.2, 1.0)
            Ellipse(pos=(cx - 5.0, cy + 33.0), size=(10.0, 10.0))

            # 5. Рамка та неонові щитові лінії
            Color(1.0, 0.3, 0.6, 0.75)
            Line(rectangle=(self.x + 18, cy + 18, self.width - 36, self.height - 30), width=1.5)


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
