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


class ParallaxBackground(Widget):
    """Віджет динамічного фону з процедурною зміною біомів та ефектом гіперстрибка."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_biome_id = "space"
        self.particles: list[BiomeParticle] = []
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
        """Створює часточки відповідного біому відповідно до розміру вікна."""
        width = max(self.width, 100.0)
        height = max(self.height, 100.0)
        cfg = get_biome_config(self.current_biome_id)

        self.particles.clear()
        count = 65

        for _ in range(count):
            x = random.uniform(0, width)
            y = random.uniform(0, height)

            if cfg.particle_type == "embers":
                # Лавовий попіл та іскри: піднімаються вгору або дрейфують
                size = random.uniform(2.5, 5.0)
                speed_x = random.uniform(-18.0, 18.0)
                speed_y = random.uniform(40.0, 110.0)
                r = 1.0
                g = random.uniform(0.2, 0.65)
                b = 0.05
                a = random.uniform(0.6, 0.95)
                color = (r, g, b, a)

            elif cfg.particle_type == "bubbles":
                # Водяні бульбашки: піднімаються з коливанням
                size = random.uniform(3.0, 7.0)
                speed_x = random.uniform(-12.0, 12.0)
                speed_y = random.uniform(35.0, 95.0)
                color = (0.2, 0.85, 0.95, random.uniform(0.4, 0.75))

            elif cfg.particle_type == "cyber":
                # Кібер-іскри та цифрові біти: швидкі спалахи
                size = random.uniform(2.0, 4.5)
                speed_x = random.uniform(-30.0, 30.0)
                speed_y = random.uniform(-120.0, -40.0)
                color = (
                    random.choice([0.85, 0.2]),
                    random.choice([0.2, 0.95]),
                    1.0,
                    random.uniform(0.65, 0.95),
                )

            elif cfg.particle_type == "snow":
                # Крижані сніжинки: плавно падають донизу
                size = random.uniform(2.5, 5.5)
                speed_x = random.uniform(-25.0, 25.0)
                speed_y = random.uniform(-75.0, -35.0)
                color = (0.75, 0.9, 1.0, random.uniform(0.55, 0.9))

            elif cfg.particle_type == "spores":
                # Токсичні зелені спори: повільно піднімаються вгору
                size = random.uniform(3.0, 6.0)
                speed_x = random.uniform(-15.0, 15.0)
                speed_y = random.uniform(20.0, 60.0)
                color = (0.3, 0.9, 0.1, random.uniform(0.5, 0.8))

            elif cfg.particle_type == "debris":
                # Фіолетове гравітаційне сміття: падає вниз (під тягою)
                size = random.uniform(2.0, 5.0)
                speed_x = random.uniform(-25.0, 25.0)
                speed_y = random.uniform(-60.0, -20.0)
                color = (0.6, 0.4, 1.0, random.uniform(0.6, 0.9))

            elif cfg.particle_type == "shadows":
                # Темні тіньові завихрення: повільно ковзають у пітьмі
                size = random.uniform(4.0, 9.0)
                speed_x = random.uniform(-8.0, 8.0)
                speed_y = random.uniform(-30.0, -10.0)
                color = (0.2, 0.05, 0.35, random.uniform(0.3, 0.6))

            elif cfg.particle_type == "void_ripples":
                # Рожево-малинові мерехтливі хвилі небули
                size = random.uniform(2.0, 5.0)
                speed_x = random.uniform(-20.0, 20.0)
                speed_y = random.uniform(-50.0, -15.0)
                color = (1.0, 0.3, 0.8, random.uniform(0.5, 0.85))

            else:
                # Космічні зорі за замовчуванням
                size = random.uniform(1.5, 4.0)
                speed_x = 0.0
                speed_y = random.uniform(-85.0, -25.0)
                color = (0.7, 0.85, 1.0, random.uniform(0.5, 0.95))

            p = BiomeParticle(
                x=x,
                y=y,
                size=size,
                speed_x=speed_x,
                speed_y=speed_y,
                color=color,
                pulse_speed=random.uniform(1.5, 4.0),
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

        for p in self.particles:
            p.time += dt
            # Рух
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

            # 2. Малювання часточок або ліній гіперстрибка
            for p in self.particles:
                Color(*p.color)
                if self.warp_active and self.warp_timer > 0.0:
                    # Ефект витягнутих променів світла (гіперпростір)
                    line_len = p.size * 7.0 * min(3.0, (1.0 + self.warp_timer * 3.0))
                    Line(
                        points=[
                            self.x + p.x,
                            self.y + p.y,
                            self.x + p.x,
                            self.y + p.y - line_len,
                        ],
                        width=max(1.2, p.size * 0.6),
                    )
                else:
                    Ellipse(
                        pos=(self.x + p.x - p.size / 2.0, self.y + p.y - p.size / 2.0),
                        size=(p.size, p.size),
                    )
