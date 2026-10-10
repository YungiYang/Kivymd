"""Рухомий паралакс-фон із підтримкою 9 унікальних біомів та ефектом гіперстрибка."""

import random
import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from game.biomes import get_biome_config


class BiomeParticle:
    """Часточка фону (зірка, попіл, бульбашка, кібер-іскра, сніжинка, спора, уламок, тінь або хвиля небули)."""

    def __init__(
        self,
        x: float,
        y: float,
        size: float,
        speed_x: float,
        speed_y: float,
        color: tuple,
        pulse_speed: float = 0.0,
        is_flare: bool = False,
    ):
        self.x = x
        self.y = y
        self.size = size
        self.base_size = size
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.color = color
        self.time = random.uniform(0.0, 10.0)
        self.pulse_speed = pulse_speed
        self.is_flare = is_flare


class NebulaCloud:
    """Процедурна космічна хмара небули з м'яким градієнтним світінням."""

    def __init__(self, x: float, y: float, w: float, h: float, color: tuple, speed_y: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.speed_y = speed_y
        self.time = random.uniform(0.0, 20.0)


class ParallaxBackground(Widget):
    """Віджет динамічного фону з процедурною зміною біомів, небулами, тактичною сіткою та ефектом гіперстрибка."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_biome_id = "space"
        self.particles: list[BiomeParticle] = []
        self.nebulae: list[NebulaCloud] = []
        self.grid_offset_y = 0.0
        self.initialized = False
        self.warp_timer = 0.0
        self.warp_active = False

        self.bind(size=self._on_size_change, pos=self._on_size_change)
        if self.width > 10 and self.height > 10:
            self._init_particles()

    @property
    def layer1_stars(self) -> list:
        """Зворотна сумісність для тестів: перший шар часточок."""
        return [p for i, p in enumerate(self.particles) if i % 2 == 0]

    @property
    def layer2_stars(self) -> list:
        """Зворотна сумісність для тестів: другий шар часточок."""
        return [p for i, p in enumerate(self.particles) if i % 2 == 1]

    def set_biome(self, biome_id: str, trigger_warp: bool = True):
        """Змінює поточний біом та запускає ефект гіперстрибка."""
        self.current_biome_id = biome_id
        if trigger_warp:
            self.warp_timer = 1.4
            self.warp_active = True
        self._init_particles()
        self.redraw()

    def _init_particles(self):
        """Створює часточки та небули відповідного біому відповідно до розміру вікна."""
        width = max(self.width, 100.0)
        height = max(self.height, 100.0)
        cfg = get_biome_config(self.current_biome_id)

        self.particles.clear()
        self.nebulae.clear()
        count = 72

        # 1. Процедурні космічні небули (глибокий атмосферний шар)
        nb_colors = [
            (cfg.accent_color[0] * 0.4, cfg.accent_color[1] * 0.4, cfg.accent_color[2] * 0.5, 0.09),
            (cfg.bg_color[0] * 1.8, cfg.bg_color[1] * 1.8, cfg.bg_color[2] * 2.2, 0.12),
            (cfg.accent_color[0] * 0.2, cfg.accent_color[1] * 0.3, cfg.accent_color[2] * 0.6, 0.08),
        ]
        for i in range(3):
            nw = width * random.uniform(0.7, 1.2)
            nh = height * random.uniform(0.35, 0.6)
            nx = random.uniform(-width * 0.2, width * 0.3)
            ny = random.uniform(0, height)
            self.nebulae.append(
                NebulaCloud(nx, ny, nw, nh, nb_colors[i % len(nb_colors)], speed_y=-18.0 - i * 8.0)
            )

        # 2. Зоряні часточки та біомні ефекти
        for i in range(count):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            is_flare = False

            if cfg.particle_type == "embers":
                size = random.uniform(2.5, 5.5)
                speed_x = random.uniform(-18.0, 18.0)
                speed_y = random.uniform(45.0, 120.0)
                r = 1.0
                g = random.uniform(0.25, 0.75)
                b = 0.05
                a = random.uniform(0.65, 0.98)
                color = (r, g, b, a)

            elif cfg.particle_type == "bubbles":
                size = random.uniform(3.0, 7.5)
                speed_x = random.uniform(-14.0, 14.0)
                speed_y = random.uniform(40.0, 105.0)
                color = (0.2, 0.88, 1.0, random.uniform(0.45, 0.85))

            elif cfg.particle_type == "cyber":
                size = random.uniform(2.0, 5.0)
                speed_x = random.uniform(-35.0, 35.0)
                speed_y = random.uniform(-140.0, -50.0)
                color = (
                    random.choice([0.9, 0.15]),
                    random.choice([0.2, 0.98]),
                    1.0,
                    random.uniform(0.7, 0.98),
                )

            elif cfg.particle_type == "snow":
                size = random.uniform(2.5, 6.0)
                speed_x = random.uniform(-25.0, 25.0)
                speed_y = random.uniform(-80.0, -40.0)
                color = (0.8, 0.94, 1.0, random.uniform(0.6, 0.95))

            elif cfg.particle_type == "spores":
                size = random.uniform(3.0, 6.5)
                speed_x = random.uniform(-15.0, 15.0)
                speed_y = random.uniform(25.0, 70.0)
                color = (0.35, 1.0, 0.2, random.uniform(0.55, 0.88))

            elif cfg.particle_type == "debris":
                size = random.uniform(2.2, 5.2)
                speed_x = random.uniform(-28.0, 28.0)
                speed_y = random.uniform(-70.0, -25.0)
                color = (0.68, 0.45, 1.0, random.uniform(0.65, 0.95))

            elif cfg.particle_type == "shadows":
                size = random.uniform(4.5, 9.5)
                speed_x = random.uniform(-10.0, 10.0)
                speed_y = random.uniform(-35.0, -12.0)
                color = (0.25, 0.08, 0.42, random.uniform(0.35, 0.65))

            elif cfg.particle_type == "void_ripples":
                size = random.uniform(2.5, 5.5)
                speed_x = random.uniform(-22.0, 22.0)
                speed_y = random.uniform(-55.0, -18.0)
                color = (1.0, 0.35, 0.85, random.uniform(0.55, 0.9))

            else:
                # Глибокий космос: багаторівневий зоряний пил + яскраві зорі з променями
                if i % 7 == 0:
                    # Велика яскрава зірка з променями (дифракційний спалах)
                    size = random.uniform(3.8, 5.8)
                    speed_x = 0.0
                    speed_y = random.uniform(-110.0, -60.0)
                    color = (0.9, 0.96, 1.0, 0.98)
                    is_flare = True
                elif i % 2 == 0:
                    # Середній шар
                    size = random.uniform(2.2, 3.4)
                    speed_x = 0.0
                    speed_y = random.uniform(-65.0, -35.0)
                    color = (0.75, 0.88, 1.0, random.uniform(0.65, 0.92))
                else:
                    # Глибокий мікро-пил
                    size = random.uniform(1.2, 2.2)
                    speed_x = 0.0
                    speed_y = random.uniform(-30.0, -16.0)
                    color = (0.55, 0.72, 0.95, random.uniform(0.4, 0.75))

            p = BiomeParticle(
                x=x,
                y=y,
                size=size,
                speed_x=speed_x,
                speed_y=speed_y,
                color=color,
                pulse_speed=random.uniform(1.8, 5.0),
                is_flare=is_flare,
            )
            self.particles.append(p)

        self.initialized = True
        self.redraw()

    def _on_size_change(self, *args):
        if not self.initialized and self.width > 10 and self.height > 10:
            self._init_particles()
        else:
            self.redraw()

    def update(self, dt: float):
        """Оновлює рух часточок фону з урахуванням ефекту гіперстрибка."""
        if not self.initialized:
            if self.width > 10 and self.height > 10:
                self._init_particles()
            return

        width = max(self.width, 100.0)
        height = max(self.height, 100.0)

        # Оновлення таймера гіперстрибка
        warp_multiplier = 1.0
        if self.warp_active:
            self.warp_timer -= dt
            if self.warp_timer > 0.0:
                warp_multiplier = 1.0 + 8.5 * math.sin(math.pi * (self.warp_timer / 1.4))
            else:
                self.warp_active = False

        # Оновлення тактичної сітки
        self.grid_offset_y = (self.grid_offset_y - 28.0 * warp_multiplier * dt) % 60.0

        # Оновлення небул
        for nb in self.nebulae:
            nb.time += dt
            nb.y += nb.speed_y * warp_multiplier * dt
            if nb.y < -nb.h:
                nb.y = height + 20.0
                nb.x = random.uniform(-width * 0.2, width * 0.3)

        for p in self.particles:
            p.time += dt
            p.x += p.speed_x * dt
            p.y += p.speed_y * warp_multiplier * dt

            # Коливання бульбашок та попелу
            if p.speed_y > 0:  # Рух вгору (лава, вода)
                p.x += math.sin(p.time * p.pulse_speed) * 16.0 * dt
                if p.y > height + 20:
                    p.y = -10.0
                    p.x = random.uniform(0, width)
            else:  # Рух вниз (космос, сніг, кібер)
                if p.y < -20:
                    p.y = height + 10.0
                    p.x = random.uniform(0, width)

            if p.x < -15:
                p.x = width + 10
            elif p.x > width + 15:
                p.x = -10

        self.redraw()

    def redraw(self):
        """Омальовує процедурний фон відповідно до біому та стану гіперстрибка."""
        self.canvas.clear()
        cfg = get_biome_config(self.current_biome_id)

        with self.canvas:
            # 1. Глибокий градієнтний базовий колір біому
            Color(*cfg.bg_color)
            Rectangle(pos=self.pos, size=self.size)

            # 2. М'які атмосферні хмари небули (космічний об'єм)
            for nb in self.nebulae:
                Color(*nb.color)
                Ellipse(pos=(self.x + nb.x, self.y + nb.y), size=(nb.w, nb.h))

            # 3. Тонка тактична навігаційна сітка (AAA sci-fi vector grid)
            Color(0.12, 0.35, 0.55, 0.05)
            # Горизонтальні лінії сітки
            gy = self.y + self.grid_offset_y
            while gy < self.y + self.height:
                Line(points=[self.x, gy, self.x + self.width, gy], width=1.0)
                gy += 60.0

            # 4. Часточки та зірки
            for p in self.particles:
                # Мерехтіння яскравості
                twinkle = 0.85 + 0.15 * math.sin(p.time * p.pulse_speed)
                r, g, b, a = p.color
                Color(r, g, b, min(1.0, a * twinkle))

                if self.warp_active and self.warp_timer > 0.0:
                    # Ефект витягнутих променів світла (гіперпростір)
                    line_len = p.size * 9.0 * min(3.5, (1.0 + self.warp_timer * 3.5))
                    Line(
                        points=[
                            self.x + p.x,
                            self.y + p.y,
                            self.x + p.x,
                            self.y + p.y - line_len,
                        ],
                        width=max(1.4, p.size * 0.7),
                    )
                    # Спалах на початку лінії
                    Color(1.0, 1.0, 1.0, 0.8)
                    Ellipse(pos=(self.x + p.x - 1.5, self.y + p.y - 1.5), size=(3.0, 3.0))
                else:
                    px = self.x + p.x
                    py = self.y + p.y
                    # Якщо зірка з променями — малюємо хрестоподібний оптичний спалах
                    if p.is_flare:
                        flare_len = p.size * 2.2
                        Color(r, g, b, a * 0.5 * twinkle)
                        Line(points=[px - flare_len, py, px + flare_len, py], width=1.0)
                        Line(points=[px, py - flare_len, px, py + flare_len], width=1.0)
                        # Зовнішнє м'яке гало
                        Color(r, g, b, a * 0.35 * twinkle)
                        Ellipse(pos=(px - p.size, py - p.size), size=(p.size * 2.0, p.size * 2.0))

                    # Основне ядро зірки
                    Color(r, g, b, min(1.0, a * twinkle))
                    Ellipse(
                        pos=(px - p.size / 2.0, py - p.size / 2.0),
                        size=(p.size, p.size),
                    )

