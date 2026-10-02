"""Рухомий паралакс-фон із двома незалежними шарами зірок."""

import random
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from game.constants import (
    BG_LAYER1_STARS_COUNT,
    BG_LAYER1_SPEED,
    BG_LAYER2_STARS_COUNT,
    BG_LAYER2_SPEED,
    COLOR_BG_SPACE,
    COLOR_STAR_FAR,
    COLOR_STAR_NEAR,
)


class Star:
    """Окрема зірка у шарі фону."""

    def __init__(self, x: float, y: float, size: float, speed: float, color: tuple):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color


class ParallaxBackground(Widget):
    """Віджет двошарового рухомого зоряного фону."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layer1_stars: list[Star] = []
        self.layer2_stars: list[Star] = []
        self.initialized = False

        self.bind(size=self._on_size_change, pos=self._on_size_change)

    def _init_stars(self):
        """Створює зірки для двох шарів відповідно до поточного розміру екрана."""
        width = max(self.width, 100.0)
        height = max(self.height, 100.0)

        # Шар 1: Далекі маленькі зорі (повільні, щільніші)
        self.layer1_stars.clear()
        for _ in range(BG_LAYER1_STARS_COUNT):
            star = Star(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                size=random.uniform(1.5, 2.5),
                speed=BG_LAYER1_SPEED * random.uniform(0.85, 1.15),
                color=COLOR_STAR_FAR,
            )
            self.layer1_stars.append(star)

        # Шар 2: Близькі більші та яскравіші зорі (швидкі)
        self.layer2_stars.clear()
        for _ in range(BG_LAYER2_STARS_COUNT):
            star = Star(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                size=random.uniform(3.0, 4.5),
                speed=BG_LAYER2_SPEED * random.uniform(0.9, 1.2),
                color=COLOR_STAR_NEAR,
            )
            self.layer2_stars.append(star)

        self.initialized = True
        self.redraw()

    def _on_size_change(self, *args):
        """Обробник зміни розмірів екрану/вікна."""
        if not self.initialized and self.width > 10 and self.height > 10:
            self._init_stars()
        else:
            self.redraw()

    def update(self, dt: float):
        """Оновлює положення зірок у двох шарах."""
        if not self.initialized:
            if self.width > 10 and self.height > 10:
                self._init_stars()
            return

        width = self.width
        height = self.height

        # Оновлення шару 1
        for star in self.layer1_stars:
            star.y -= star.speed * dt
            if star.y < -5:
                star.y = height + random.uniform(2, 20)
                star.x = random.uniform(0, width)

        # Оновлення шару 2
        for star in self.layer2_stars:
            star.y -= star.speed * dt
            if star.y < -5:
                star.y = height + random.uniform(2, 20)
                star.x = random.uniform(0, width)

        self.redraw()

    def redraw(self):
        """Перемальовує космічний простір та обидва шари зірок."""
        self.canvas.clear()
        with self.canvas:
            # Глибокий космос (базовий фон)
            Color(*COLOR_BG_SPACE)
            Rectangle(pos=self.pos, size=self.size)

            # Шар 1 (Далекі зорі)
            for star in self.layer1_stars:
                Color(*star.color)
                Ellipse(
                    pos=(self.x + star.x, self.y + star.y),
                    size=(star.size, star.size),
                )

            # Шар 2 (Близькі зорі)
            for star in self.layer2_stars:
                Color(*star.color)
                Ellipse(
                    pos=(self.x + star.x, self.y + star.y),
                    size=(star.size, star.size),
                )
