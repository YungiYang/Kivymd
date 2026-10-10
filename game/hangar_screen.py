"""Екран ангару кораблів гравця (Hangar / Ship Shop)."""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse, Triangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

from kivy.clock import Clock
from game.background import ParallaxBackground
from game.ships import SHIPS_CATALOG, ORDERED_SHIP_IDS, CRAFT_ONLY_SHIPS, get_ship_config
from game.storage import (
    get_credits,
    spend_credits,
    get_unlocked_ships,
    unlock_ship,
    get_selected_ship,
    set_selected_ship,
    get_crafted_ships,
    get_materials,
)
from game.materials import CRAFT_RECIPES, can_craft
from game.audio import get_audio_manager


class HangarShipPreview(Widget):
    """Живий графічний прев'ю-віджет корабля на голографічному постаменті ангара (AAA Dry-Dock)."""

    def __init__(self, ship_id: str = "striker", **kwargs):
        super().__init__(**kwargs)
        self.ship_id = ship_id
        self.time_alive = 0.0
        self.size_hint = (None, None)
        self.size = (200, 155)
        self.bind(pos=self._redraw, size=self._redraw)

    def set_ship(self, ship_id: str):
        self.ship_id = ship_id
        self._redraw()

    def update_anim(self, dt: float):
        self.time_alive += dt
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        cfg = get_ship_config(self.ship_id)
        cx = self.x + self.width / 2.0
        # Плавне ширяння корабля в повітрі (Hover oscillation)
        hover_y = 4.5 * math.sin(self.time_alive * 3.5)
        cy = self.y + self.height / 2.0 - 6.0 + hover_y
        w = cfg.width * 1.65
        h = cfg.height * 1.65
        t = self.time_alive

        with self.canvas:
            pulse = 1.0 + 0.1 * math.sin(t * 5.0)

            # 1. Голографічний постамент верфі (3D Perspective Hologram Dock)
            dock_y = self.y + 16.0
            # Зовнішнє неонове кільце
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.16 * pulse)
            Ellipse(pos=(cx - 75.0, dock_y - 20.0), size=(150.0, 40.0))
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.65)
            Line(ellipse=(cx - 75.0, dock_y - 20.0, 150.0, 40.0), width=1.5)
            # Внутрішнє фокусуюче кільце
            Color(0.2, 0.9, 1.0, 0.45)
            Line(ellipse=(cx - 48.0, dock_y - 13.0, 96.0, 26.0), width=1.0)
            # Радіальні направляючі промені
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.25)
            Line(points=[cx - 68.0, dock_y - 12.0, cx - 35.0, dock_y - 6.0], width=1.0)
            Line(points=[cx + 68.0, dock_y - 12.0, cx + 35.0, dock_y - 6.0], width=1.0)

            # Вертикальний лазерний сканер діагностики (проходить вгору-вниз)
            scan_prog = (math.sin(t * 2.5) + 1.0) / 2.0
            scan_y = cy - h * 0.4 + scan_prog * (h * 0.9)
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.3)
            Line(points=[cx - w * 0.6, scan_y, cx + w * 0.6, scan_y], width=1.5)

            # 2. Подвійні реактивні факели сопел
            flame_len = 18.0 * (0.8 + 0.3 * math.sin(t * 22.0))
            for noz_x in [cx - w * 0.22, cx + w * 0.22]:
                Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.35)
                Triangle(points=[noz_x - 7.0, cy - h * 0.42, noz_x, cy - h * 0.42 - flame_len * 1.2, noz_x + 7.0, cy - h * 0.42])
                Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.9)
                Triangle(points=[noz_x - 4.5, cy - h * 0.42, noz_x, cy - h * 0.42 - flame_len, noz_x + 4.5, cy - h * 0.42])
                Color(1.0, 1.0, 0.9, 0.98)
                Triangle(points=[noz_x - 2.0, cy - h * 0.42, noz_x, cy - h * 0.42 - flame_len * 0.55, noz_x + 2.0, cy - h * 0.42])

            # 3. Навігаційні стробоскопи на крилах
            strobe_on = math.sin(t * 7.5) > 0.0
            Color(1.0, 0.15, 0.15, 0.95 if strobe_on else 0.25)
            Ellipse(pos=(cx - w * 0.5 + 2.0, cy - h * 0.2), size=(4.0, 4.0))
            Color(0.15, 1.0, 0.35, 0.95 if strobe_on else 0.25)
            Ellipse(pos=(cx + w * 0.5 - 6.0, cy - h * 0.2), size=(4.0, 4.0))

            # 4. Високодеталізовані моделі кораблів
            if self.ship_id == "beam_titan":
                # ── КВАНТОВИЙ КРЕЙСЕР «ГЕЛІОС» ──
                Color(*cfg.secondary_color)
                Rectangle(pos=(cx - w * 0.45, cy - h * 0.25), size=(w * 0.9, h * 0.5))
                Triangle(points=[cx - w * 0.5, cy - h * 0.1, cx, cy + h * 0.5, cx + w * 0.5, cy - h * 0.1])
                Color(*cfg.primary_color)
                Rectangle(pos=(cx - w * 0.28, cy - h * 0.32), size=(w * 0.56, h * 0.68))
                # Магнітні рейки
                Color(0.18, 0.24, 0.35, 1.0)
                Rectangle(pos=(cx - w * 0.25, cy + h * 0.1), size=(w * 0.14, h * 0.42))
                Rectangle(pos=(cx + w * 0.11, cy + h * 0.1), size=(w * 0.14, h * 0.42))
                # Обертова призма
                Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.35)
                Ellipse(pos=(cx - 14.0, cy + h * 0.32), size=(28.0, 28.0))
                Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.95)
                Ellipse(pos=(cx - 6.0, cy + h * 0.32 + 8.0), size=(12.0, 12.0))
                Color(1.0, 1.0, 1.0, 0.98)
                Ellipse(pos=(cx - 3.0, cy + h * 0.32 + 11.0), size=(6.0, 6.0))
                Color(0.2, 0.85, 0.95, 0.7)
                Line(rectangle=[cx - w * 0.28, cy - h * 0.32, w * 0.56, h * 0.68], width=1.2)

            elif self.ship_id == "plasma_vanguard":
                # ── ДРЕДНОУТ «ВУЛКАН» ──
                Color(*cfg.secondary_color)
                Rectangle(pos=(cx - w * 0.44, cy - h * 0.32), size=(w * 0.88, h * 0.5))
                Triangle(points=[cx - w * 0.48, cy - h * 0.2, cx, cy + h * 0.38, cx + w * 0.48, cy - h * 0.2])
                Color(*cfg.primary_color)
                Triangle(points=[cx - w * 0.32, cy - h * 0.28, cx, cy + h * 0.48, cx + w * 0.32, cy - h * 0.28])
                # Реактор на носі
                Color(1.0, 0.35, 0.05, 0.45)
                Ellipse(pos=(cx - 15.0, cy + h * 0.24), size=(30.0, 30.0))
                Color(1.0, 0.65, 0.1, 0.95)
                Ellipse(pos=(cx - 9.0, cy + h * 0.24 + 6.0), size=(18.0, 18.0))
                Color(1.0, 0.95, 0.3, 1.0)
                Ellipse(pos=(cx - 4.5, cy + h * 0.24 + 10.5), size=(9.0, 9.0))

            elif self.ship_id == "storm_valkyrie":
                # ── ПЕРЕХОПЛЮВАЧ «ВАЛЬКІРІЯ» ──
                Color(*cfg.secondary_color)
                Triangle(points=[cx - w * 0.5, cy - h * 0.2, cx, cy + h * 0.5, cx, cy - h * 0.3])
                Triangle(points=[cx + w * 0.5, cy - h * 0.2, cx, cy + h * 0.5, cx, cy - h * 0.3])
                Color(*cfg.primary_color)
                Triangle(points=[cx - w * 0.28, cy - h * 0.25, cx, cy + h * 0.52, cx + w * 0.28, cy - h * 0.25])
                Color(*cfg.accent_color)
                Line(points=[cx - w * 0.44, cy - h * 0.15, cx, cy + h * 0.35], width=1.5)
                Line(points=[cx + w * 0.44, cy - h * 0.15, cx, cy + h * 0.35], width=1.5)
                Color(0.2, 0.92, 1.0, 0.95)
                Ellipse(pos=(cx - 5.0, cy + 2.0), size=(10.0, 18.0))
                Color(1.0, 1.0, 1.0, 0.85)
                Line(points=[cx - 2.0, cy + 10.0, cx + 1.5, cy + 16.0], width=1.2)

            elif self.ship_id == "nova_hunter":
                # ── МИСЛИВЕЦЬ «НОВА» ──
                Color(*cfg.secondary_color)
                Triangle(points=[cx - w * 0.48, cy - h * 0.28, cx, cy + h * 0.48, cx + w * 0.48, cy - h * 0.28])
                Color(*cfg.primary_color)
                Triangle(points=[cx - w * 0.32, cy - h * 0.22, cx, cy + h * 0.42, cx + w * 0.32, cy - h * 0.22])
                Color(0.2, 0.22, 0.28, 1.0)
                Rectangle(pos=(cx - w * 0.36, cy - 4.0), size=(7.0, 18.0))
                Rectangle(pos=(cx + w * 0.36 - 7.0, cy - 4.0), size=(7.0, 18.0))
                Color(1.0, 0.3, 0.1, 1.0)
                Ellipse(pos=(cx - w * 0.36 + 1.0, cy + 12.0), size=(5.0, 6.0))
                Ellipse(pos=(cx + w * 0.36 - 6.0, cy + 12.0), size=(5.0, 6.0))
                Color(1.0, 0.15, 0.2, 0.95)
                Ellipse(pos=(cx - 4.0, cy + h * 0.12), size=(8.0, 12.0))

            elif self.ship_id == "phantom_shade":
                # ── ФАНТОМНИЙ КОРВЕТ «ТІНЬ» ──
                Color(*cfg.secondary_color)
                Triangle(points=[cx - w * 0.46, cy - h * 0.1, cx, cy + h * 0.52, cx + w * 0.46, cy - h * 0.1])
                Triangle(points=[cx - w * 0.46, cy - h * 0.1, cx, cy - h * 0.35, cx + w * 0.46, cy - h * 0.1])
                Color(*cfg.primary_color)
                Triangle(points=[cx - w * 0.3, cy - h * 0.1, cx, cy + h * 0.45, cx + w * 0.3, cy - h * 0.1])
                Color(*cfg.accent_color)
                Line(points=[cx - w * 0.4, cy - h * 0.1, cx, cy + h * 0.25, cx + w * 0.4, cy - h * 0.1], width=1.5)
                Color(0.85, 0.45, 1.0, 0.95)
                Ellipse(pos=(cx - 4.5, cy + 2.0), size=(9.0, 14.0))

            else:
                # ── АПЕКС-ШТУРМОВИК «ФЕНІКС» ──
                Color(*cfg.secondary_color)
                Triangle(points=[cx - w * 0.5, cy - h * 0.28, cx, cy + h * 0.38, cx + w * 0.5, cy - h * 0.28])
                Color(*cfg.primary_color)
                Triangle(points=[cx - w * 0.38, cy - h * 0.22, cx, cy + h * 0.5, cx + w * 0.38, cy - h * 0.22])
                # Гармати
                Color(0.25, 0.32, 0.45, 1.0)
                Rectangle(pos=(cx - w * 0.34, cy - 2.0), size=(4.0, 20.0))
                Rectangle(pos=(cx + w * 0.34 - 4.0, cy - 2.0), size=(4.0, 20.0))
                Color(*cfg.accent_color)
                Ellipse(pos=(cx - w * 0.34 - 0.5, cy + 17.0), size=(5.0, 6.0))
                Ellipse(pos=(cx + w * 0.34 - 4.5, cy + 17.0), size=(5.0, 6.0))
                # Кіль
                Color(cfg.primary_color[0] * 1.2, cfg.primary_color[1] * 1.2, cfg.primary_color[2] * 1.2, 1.0)
                Triangle(points=[cx - 8.0, cy - h * 0.24, cx, cy + h * 0.52, cx + 8.0, cy - h * 0.24])
                # Кабіна
                Color(0.12, 0.88, 1.0, 0.95)
                Ellipse(pos=(cx - 5.0, cy + 4.0), size=(10.0, 18.0))
                Color(1.0, 1.0, 1.0, 0.85)
                Line(points=[cx - 2.0, cy + 12.0, cx + 1.5, cy + 18.0], width=1.4)
                Color(*cfg.accent_color)
                Line(points=[cx - w * 0.32, cy - h * 0.16, cx, cy + h * 0.22], width=1.2)
                Line(points=[cx + w * 0.32, cy - h * 0.16, cx, cy + h * 0.22], width=1.2)



class HangarScreen(MDScreen):
    """Екран вибору та купівлі кораблів за збережені очки (кредити)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "hangar_screen"
        self.current_idx = 0
        self._build_ui()

    def on_enter(self, *args):
        """Оновлює баланс та вибраний корабель при відкритті ангару."""
        selected = get_selected_ship()
        if selected in ORDERED_SHIP_IDS:
            self.current_idx = ORDERED_SHIP_IDS.index(selected)
        self._update_display()
        self._anim_event = Clock.schedule_interval(self._on_anim_tick, 1.0 / 30.0)
        get_audio_manager().play_menu_music()

    def on_leave(self, *args):
        if hasattr(self, "_anim_event") and self._anim_event:
            Clock.unschedule(self._anim_event)
            self._anim_event = None

    def _on_anim_tick(self, dt: float):
        if hasattr(self, "ship_preview") and self.ship_preview:
            self.ship_preview.update_anim(dt)
        if hasattr(self, "bg") and self.bg:
            self.bg.update(dt)


    def _build_ui(self):
        # 1. Зоряний фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.add_widget(self.bg)

        # 2. Головний контейнер
        self.root_box = BoxLayout(
            orientation="vertical",
            padding=[16, 18, 16, 18],
            spacing=10,
            size_hint=(1, 1),
        )

        # Верхня панель (Заголовок + Баланс кредитів)
        top_bar = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=46,
            spacing=10,
        )
        self.title_label = MDLabel(
            text="🛸  ВЕРФЬ КОРАБЛЕЙ",
            font_style="Title",
            role="large",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            size_hint=(0.55, 1),
        )
        top_bar.add_widget(self.title_label)

        self.credits_label = MDLabel(
            text=f"💠 {get_credits():,}",
            halign="right",
            font_style="Title",
            role="medium",
            bold=True,
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.25, 1.0),
            size_hint=(0.45, 1),
        )
        top_bar.add_widget(self.credits_label)
        self.root_box.add_widget(top_bar)

        # Картка вітрини корабля (Центральний блок)
        self.showcase_card = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[14, 10, 14, 12],
            spacing=8,
        )
        with self.showcase_card.canvas.before:
            Color(0.06, 0.09, 0.18, 0.88)
            self.card_bg = RoundedRectangle(
                pos=self.showcase_card.pos, size=self.showcase_card.size, radius=[14]
            )
            Color(0.18, 0.45, 0.75, 0.75)
            self.card_border = Line(
                rounded_rectangle=[
                    self.showcase_card.x,
                    self.showcase_card.y,
                    self.showcase_card.width,
                    self.showcase_card.height,
                    14,
                ],
                width=1.5,
            )
        self.showcase_card.bind(pos=self._update_card_canvas, size=self._update_card_canvas)

        # Селектор навігації (◀ Назва Корабля ▶)
        nav_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=46,
            spacing=8,
        )
        self.prev_btn = MDButton(
            MDButtonText(text="◀", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(None, 1),
            width=46,
            theme_bg_color="Custom",
            md_bg_color=(0.12, 0.22, 0.42, 0.88),
        )
        self.prev_btn.bind(on_release=self._prev_ship)
        nav_box.add_widget(self.prev_btn)

        ship_header_box = BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=1)
        self.ship_name_label = MDLabel(
            text="«ФЕНИКС»",
            halign="center",
            font_style="Headline",
            role="small",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.9, 1.0, 1.0),
            size_hint=(1, None),
            height=26,
        )
        self.ship_class_label = MDLabel(
            text="Быстрый Штурмовик",
            halign="center",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.7, 0.82, 0.95, 0.85),
            size_hint=(1, None),
            height=18,
        )
        ship_header_box.add_widget(self.ship_name_label)
        ship_header_box.add_widget(self.ship_class_label)
        nav_box.add_widget(ship_header_box)

        self.next_btn = MDButton(
            MDButtonText(text="▶", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(None, 1),
            width=46,
            theme_bg_color="Custom",
            md_bg_color=(0.12, 0.22, 0.42, 0.88),
        )
        self.next_btn.bind(on_release=self._next_ship)
        nav_box.add_widget(self.next_btn)

        self.showcase_card.add_widget(nav_box)

        # Графічний прев'ю-віджет корабля
        preview_container = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=135,
            pos_hint={"center_x": 0.5},
        )
        self.ship_preview = HangarShipPreview(ship_id="striker")
        self.ship_preview.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        preview_container.add_widget(self.ship_preview)
        self.showcase_card.add_widget(preview_container)

        # Опис та унікальна атака
        desc_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=72,
            spacing=2,
            padding=[4, 0, 4, 0],
        )
        self.ship_desc_label = MDLabel(
            text="Сбалансированный классический истребитель Альянса.",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.85, 0.9, 0.98, 0.9),
            size_hint=(1, 1),
        )
        self.weapon_desc_label = MDLabel(
            text="⚔️  Вооружение: Спаренные плазменные лазеры",
            font_style="Label",
            role="large",
            bold=True,
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.3, 1.0),
            size_hint=(1, None),
            height=20,
        )
        desc_box.add_widget(self.ship_desc_label)
        desc_box.add_widget(self.weapon_desc_label)
        self.showcase_card.add_widget(desc_box)

        # Смужки характеристик (HP, Швидкість, Шкода)
        self.stats_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=74,
            spacing=4,
            padding=[4, 2, 4, 2],
        )
        self.hp_stat_label = MDLabel(
            text="🛡️  Броня: 100 HP",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.3, 1.0, 0.5, 1.0),
            size_hint=(1, None),
            height=20,
        )
        self.speed_stat_label = MDLabel(
            text="⚡  Скорость: 360",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            size_hint=(1, None),
            height=20,
        )
        self.special_stat_label = MDLabel(
            text="✨  Особенность: Лёгкий уклон",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(1.0, 0.65, 0.95, 1.0),
            size_hint=(1, None),
            height=20,
        )
        self.stats_box.add_widget(self.hp_stat_label)
        self.stats_box.add_widget(self.speed_stat_label)
        self.stats_box.add_widget(self.special_stat_label)
        self.showcase_card.add_widget(self.stats_box)

        self.root_box.add_widget(self.showcase_card)

        # Нижня панель дій (Кнопка дії: Купити / Обрати / Обрано + Кнопка Назад)
        bottom_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=106,
            spacing=10,
        )

        self.action_btn = MDButton(
            MDButtonText(text="⚡ ВЫБРАТЬ КОРАБЛЬ", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(1, None),
            height=50,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.7, 0.45, 1.0),
        )
        self.action_btn.bind(on_release=self._on_action_click)
        bottom_box.add_widget(self.action_btn)

        self.back_btn = MDButton(
            MDButtonText(text="◀️  НАЗАД В МЕНЮ", font_style="Title", role="small"),
            style="outlined",
            size_hint=(1, None),
            height=44,
        )
        self.back_btn.bind(on_release=self._go_back)
        bottom_box.add_widget(self.back_btn)

        self.root_box.add_widget(bottom_box)
        self.add_widget(self.root_box)


    def _prev_ship(self, *args):
        self.current_idx = (self.current_idx - 1) % len(ORDERED_SHIP_IDS)
        self._update_display()

    def _next_ship(self, *args):
        self.current_idx = (self.current_idx + 1) % len(ORDERED_SHIP_IDS)
        self._update_display()

    def _update_display(self):
        ship_id = ORDERED_SHIP_IDS[self.current_idx]
        cfg = get_ship_config(ship_id)
        credits = get_credits()
        unlocked = get_unlocked_ships()
        selected = get_selected_ship()

        self.credits_label.text = f"💠 {credits:,}"
        self.ship_name_label.text = cfg.name
        self.ship_name_label.text_color = cfg.accent_color
        self.ship_class_label.text = cfg.class_name
        self.ship_desc_label.text = cfg.description
        self.weapon_desc_label.text = f"⚔️  {cfg.weapon_desc}"
        self.hp_stat_label.text = f"🛡️  Броня: {cfg.max_hp} HP"
        self.speed_stat_label.text = f"⚡  Скорость: {int(cfg.speed)}"

        if cfg.initial_shield > 0:
            self.special_stat_label.text = f"✨  Щит: +{cfg.initial_shield} стартовый энергощит"
        elif cfg.attack_type == "beam":
            self.special_stat_label.text = "✨  Атака: Квантовый луч (2.2с непрерывно)"
        elif cfg.attack_type == "charge":
            self.special_stat_label.text = "✨  Атака: Заряженная мега-плазмосфера"
        elif cfg.attack_type == "missile":
            self.special_stat_label.text = "✨  Атака: Самонаводящаяся ракета (мощный взрыв)"
        elif cfg.attack_type == "dual_beam":
            self.special_stat_label.text = "✨  Атака: Двойной непрерывный лазер"
        elif cfg.attack_type == "spread":
            self.special_stat_label.text = "✨  Атака: Многолучевой веерный залп"
        else:
            self.special_stat_label.text = "✨  Атака: Высокоскоростные спаренные лазеры"

        self.ship_preview.set_ship(ship_id)

        # Оновлення стану кнопки дії
        is_owned = ship_id in get_unlocked_ships() or ship_id in get_crafted_ships()
        is_active = ship_id == selected
        is_craft_only = ship_id in CRAFT_ONLY_SHIPS

        # Очищуємо дітей кнопки дії
        self.action_btn.clear_widgets()

        if is_active:
            btn_text = MDButtonText(
                text="✅  В БОЙ! ВЫБРАНО",
                font_style="Title",
                role="medium",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 1.0, 1.0, 1.0),
            )
            self.action_btn.add_widget(btn_text)
            self.action_btn.md_bg_color = (0.1, 0.65, 0.35, 0.7)
            self.action_btn.disabled = True
        elif is_owned:
            btn_text = MDButtonText(
                text="⚡  ВЫБРАТЬ ЭТОТ КОРАБЛЬ",
                font_style="Title",
                role="medium",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 1.0, 1.0, 1.0),
            )
            self.action_btn.add_widget(btn_text)
            self.action_btn.md_bg_color = (0.1, 0.7, 0.85, 1.0)
            self.action_btn.disabled = False
        elif is_craft_only:
            # Перевіряємо рецепт та матеріали
            recipe = next((r for r in CRAFT_RECIPES.values() if r.ship_id == ship_id), None)
            if recipe and can_craft(recipe.recipe_id, get_materials()):
                btn_text = MDButtonText(
                    text=f"⚗️  СОБРАТЬ КОРАБЛЬ",
                    font_style="Title",
                    role="medium",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(0.05, 0.08, 0.12, 1.0),
                )
                self.action_btn.add_widget(btn_text)
                self.action_btn.md_bg_color = (0.85, 0.55, 1.0, 1.0)
                self.action_btn.disabled = False
            else:
                req_text = "🔒  КРАФТ: Нужны редкие материалы из боссов"
                if recipe:
                    parts = []
                    mats = get_materials()
                    for mat_id, need in recipe.materials_required.items():
                        from game.materials import get_material
                        try:
                            mat = get_material(mat_id)
                            have = mats.get(mat_id, 0)
                            parts.append(f"{mat.icon}{mat.name} {have}/{need}")
                        except Exception:
                            parts.append(f"{mat_id}: {mats.get(mat_id,0)}/{need}")
                    req_text = "⚗️  " + "  ".join(parts[:3])
                btn_text = MDButtonText(
                    text=req_text,
                    font_style="Body",
                    role="small",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(0.75, 0.55, 1.0, 0.9),
                )
                self.action_btn.add_widget(btn_text)
                self.action_btn.md_bg_color = (0.18, 0.12, 0.28, 0.7)
                self.action_btn.disabled = True
        else:
            # Треба купити за кредити
            can_afford = credits >= cfg.cost
            if can_afford:
                btn_text = MDButtonText(
                    text=f"💠  КУПИТЬ ЗА {cfg.cost:,} КРЕДИТОВ",
                    font_style="Title",
                    role="medium",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(0.05, 0.1, 0.15, 1.0),
                )
                self.action_btn.add_widget(btn_text)
                self.action_btn.md_bg_color = (1.0, 0.85, 0.2, 1.0)
                self.action_btn.disabled = False
            else:
                needed = cfg.cost - credits
                btn_text = MDButtonText(
                    text=f"🔒  НУЖНО {cfg.cost:,} 💠 (НЕ ХВАТАЕТ {needed:,})",
                    font_style="Title",
                    role="small",
                    bold=True,
                    theme_text_color="Custom",
                    text_color=(0.7, 0.7, 0.7, 0.8),
                )
                self.action_btn.add_widget(btn_text)
                self.action_btn.md_bg_color = (0.2, 0.22, 0.3, 0.6)
                self.action_btn.disabled = True


    def _on_action_click(self, *args):
        ship_id = ORDERED_SHIP_IDS[self.current_idx]
        cfg = get_ship_config(ship_id)
        crafted = get_crafted_ships()
        unlocked = get_unlocked_ships()

        if ship_id in unlocked or ship_id in crafted:
            # Обираємо корабель
            set_selected_ship(ship_id)
            get_audio_manager().play("upgrade")
            self._update_display()
        elif ship_id in CRAFT_ONLY_SHIPS:
            # Крафтимо корабель
            from game.materials import craft_ship
            from game.storage import set_materials, add_crafted_ship
            recipe = next((r for r in CRAFT_RECIPES.values() if r.ship_id == ship_id), None)
            if recipe:
                success, new_inv = craft_ship(recipe.recipe_id, get_materials())
                if success:
                    set_materials(new_inv)
                    add_crafted_ship(ship_id)
                    unlock_ship(ship_id)
                    set_selected_ship(ship_id)
                    get_audio_manager().play("upgrade")
                    self._update_display()
        else:
            # Купуємо корабель за кредити
            if spend_credits(cfg.cost):
                unlock_ship(ship_id)
                set_selected_ship(ship_id)
                get_audio_manager().play("upgrade")
                self._update_display()

    def _go_back(self, *args):
        if self.manager:
            self.manager.current = "menu_screen"

    def _update_card_canvas(self, *args):
        if hasattr(self, "card_bg"):
            self.card_bg.pos = self.showcase_card.pos
            self.card_bg.size = self.showcase_card.size
            self.card_border.rounded_rectangle = [
                self.showcase_card.x,
                self.showcase_card.y,
                self.showcase_card.width,
                self.showcase_card.height,
                14,
            ]
