"""Екран ангару кораблів гравця (Hangar / Ship Shop)."""

import math
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse, Triangle
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

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
    """Живий графічний прев'ю-віджет корабля на полотні ангара."""

    def __init__(self, ship_id: str = "striker", **kwargs):
        super().__init__(**kwargs)
        self.ship_id = ship_id
        self.time_alive = 0.0
        self.size_hint = (None, None)
        self.size = (180, 150)
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
        cy = self.y + self.height / 2.0 - 10.0
        w = cfg.width * 1.7
        h = cfg.height * 1.7

        with self.canvas:
            pulse = 1.0 + 0.08 * math.sin(self.time_alive * 6.0)

            # 1. Сяйво енергетичного постаменту під кораблем
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.22 * pulse)
            Ellipse(pos=(cx - 65, cy - 25), size=(130, 42))
            Color(cfg.accent_color[0], cfg.accent_color[1], cfg.accent_color[2], 0.6)
            Line(ellipse=(cx - 65, cy - 25, 130, 42), width=1.5)

            # 2. Полум'я реактивних двигунів
            flame_len = 22.0 * (0.8 + 0.3 * math.sin(self.time_alive * 18.0))
            Color(1.0, 0.65, 0.15, 0.85)
            Triangle(
                points=[
                    cx - 10, cy - h / 2.0 + 8,
                    cx, cy - h / 2.0 - flame_len,
                    cx + 10, cy - h / 2.0 + 8,
                ]
            )
            Color(1.0, 0.95, 0.4, 0.95)
            Triangle(
                points=[
                    cx - 5, cy - h / 2.0 + 8,
                    cx, cy - h / 2.0 - flame_len * 0.6,
                    cx + 5, cy - h / 2.0 + 8,
                ]
            )

            # 3. Корпус корабля залежно від класу
            if self.ship_id == "beam_titan":
                # Важкий променевий крейсер
                Color(*cfg.secondary_color)
                Rectangle(pos=(cx - w * 0.45, cy - h * 0.3), size=(w * 0.9, h * 0.6))
                Triangle(points=[cx - w * 0.5, cy, cx, cy + h * 0.5, cx + w * 0.5, cy])
                Color(*cfg.primary_color)
                Rectangle(pos=(cx - w * 0.28, cy - h * 0.38), size=(w * 0.56, h * 0.76))
                # Фокусуюча квантова призма на носі
                Color(*cfg.accent_color)
                Ellipse(pos=(cx - 12, cy + h * 0.35), size=(24, 24))
                Color(1.0, 1.0, 1.0, 0.95)
                Ellipse(pos=(cx - 6, cy + h * 0.35 + 6), size=(12, 12))

            elif self.ship_id == "plasma_vanguard":
                # Масивний дредноут
                Color(*cfg.secondary_color)
                Rectangle(pos=(cx - w * 0.48, cy - h * 0.38), size=(w * 0.96, h * 0.68))
                Color(*cfg.primary_color)
                Triangle(
                    points=[
                        cx - w * 0.38, cy - h * 0.38,
                        cx, cy + h * 0.48,
                        cx + w * 0.38, cy - h * 0.38,
                    ]
                )
                # Плазмовий реактор
                Color(1.0, 0.35, 0.1, 0.9)
                Ellipse(pos=(cx - 14, cy - 6), size=(28, 28))
                Color(1.0, 0.9, 0.2, 1.0)
                Ellipse(pos=(cx - 7, cy + 1), size=(14, 14))

            elif self.ship_id == "storm_valkyrie":
                # Стрілоподібний перехоплювач
                Color(*cfg.secondary_color)
                Triangle(
                    points=[
                        cx - w * 0.55, cy - h * 0.15,
                        cx, cy + h * 0.55,
                        cx + w * 0.55, cy - h * 0.15,
                    ]
                )
                Color(*cfg.primary_color)
                Triangle(
                    points=[
                        cx - w * 0.28, cy - h * 0.38,
                        cx, cy + h * 0.52,
                        cx + w * 0.28, cy - h * 0.38,
                    ]
                )
                # Неонові стабілізатори
                Color(*cfg.accent_color)
                Line(points=[cx - w * 0.45, cy - h * 0.1, cx - w * 0.2, cy + h * 0.2], width=2.0)
                Line(points=[cx + w * 0.45, cy - h * 0.1, cx + w * 0.2, cy + h * 0.2], width=2.0)
                # Кабіна
                Color(0.2, 0.9, 1.0, 0.95)
                Ellipse(pos=(cx - 6, cy + 6), size=(12, 20))

            else:
                # Класичний штурмовик «Фенікс»
                Color(*cfg.secondary_color)
                Triangle(
                    points=[
                        cx - w * 0.5, cy - h * 0.25,
                        cx, cy + h * 0.35,
                        cx + w * 0.5, cy - h * 0.25,
                    ]
                )
                Color(*cfg.primary_color)
                Triangle(
                    points=[
                        cx - w * 0.3, cy - h * 0.35,
                        cx, cy + h * 0.5,
                        cx + w * 0.3, cy - h * 0.35,
                    ]
                )
                Color(*cfg.accent_color)
                Ellipse(pos=(cx - 6, cy + 2), size=(12, 18))


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
            text="🚀 АНГАР КОРАБЛІВ",
            font_style="Title",
            role="large",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            size_hint=(0.55, 1),
        )
        top_bar.add_widget(self.title_label)

        self.credits_label = MDLabel(
            text=f"🪙 {get_credits():,}",
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

        # Селектор навігації (< Назва Корабля >)
        nav_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=46,
            spacing=8,
        )
        self.prev_btn = MDButton(
            MDButtonText(text="<", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(None, 1),
            width=46,
            theme_bg_color="Custom",
            md_bg_color=(0.15, 0.25, 0.45, 0.85),
        )
        self.prev_btn.bind(on_release=self._prev_ship)
        nav_box.add_widget(self.prev_btn)

        ship_header_box = BoxLayout(orientation="vertical", size_hint=(1, 1), spacing=1)
        self.ship_name_label = MDLabel(
            text="«ФЕНІКС»",
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
            text="Швидкісний Штурмовик",
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
            MDButtonText(text=">", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(None, 1),
            width=46,
            theme_bg_color="Custom",
            md_bg_color=(0.15, 0.25, 0.45, 0.85),
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
            text="Збалансований класичний винищувач Альянсу.",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.85, 0.9, 0.98, 0.9),
            size_hint=(1, 1),
        )
        self.weapon_desc_label = MDLabel(
            text="⚔️ Зброя: Здвоєні плазмові лазери",
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
            text="🛡️ Броня: 100 HP",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.3, 1.0, 0.5, 1.0),
            size_hint=(1, None),
            height=20,
        )
        self.speed_stat_label = MDLabel(
            text="⚡ Швидкість: 360",
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            size_hint=(1, None),
            height=20,
        )
        self.special_stat_label = MDLabel(
            text="✨ Особливість: Легкий ухил",
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
            MDButtonText(text="ОБРАТИ", font_style="Title", role="medium", bold=True),
            style="filled",
            size_hint=(1, None),
            height=50,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.7, 0.45, 1.0),
        )
        self.action_btn.bind(on_release=self._on_action_click)
        bottom_box.add_widget(self.action_btn)

        self.back_btn = MDButton(
            MDButtonText(text="← НАЗАД ДО МЕНЮ", font_style="Title", role="small"),
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

        self.credits_label.text = f"🪙 {credits:,}"
        self.ship_name_label.text = cfg.name
        self.ship_name_label.text_color = cfg.accent_color
        self.ship_class_label.text = cfg.class_name
        self.ship_desc_label.text = cfg.description
        self.weapon_desc_label.text = f"⚔️ {cfg.weapon_desc}"
        self.hp_stat_label.text = f"🛡️ Броня: {cfg.max_hp} HP"
        self.speed_stat_label.text = f"⚡ Швидкість: {int(cfg.speed)}"

        if cfg.initial_shield > 0:
            self.special_stat_label.text = f"✨ Щит: +{cfg.initial_shield} стартовий енергощит"
        elif cfg.attack_type == "beam":
            self.special_stat_label.text = "✨ Атака: Довгий квантовий промінь (2.2с)"
        elif cfg.attack_type == "charge":
            self.special_stat_label.text = "✨ Атака: Зарядна мега-плазмова сфера"
        elif cfg.attack_type == "missile":
            self.special_stat_label.text = "✨ Атака: Самонавідна ракета (великий вибух)"
        elif cfg.attack_type == "dual_beam":
            self.special_stat_label.text = "✨ Атака: Подвійний безперервний лазер"
        elif cfg.attack_type == "spread":
            self.special_stat_label.text = "✨ Атака: Багатопроменевий віяловий залп"
        else:
            self.special_stat_label.text = "✨ Атака: Швидкісні подвійні лазери"

        self.ship_preview.set_ship(ship_id)

        # Оновлення стану кнопки дії
        is_owned = ship_id in get_unlocked_ships() or ship_id in get_crafted_ships()
        is_active = ship_id == selected
        is_craft_only = ship_id in CRAFT_ONLY_SHIPS

        # Очищуємо дітей кнопки дії
        self.action_btn.clear_widgets()

        if is_active:
            btn_text = MDButtonText(
                text="✅ ОБРАНО ДЛЯ БОЮ",
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
                text="⚡ ОБРАТИ КОРАБЕЛЬ",
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
                    text=f"⚗️ СТВОРИТИ КОРАБЕЛЬ",
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
                req_text = "🔒 КРАФТ: Потрібні рідкісні матеріали з босів"
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
                    req_text = "⚗️ " + "  ".join(parts[:3])
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
                    text=f"🪙 КУПИТИ ЗА {cfg.cost:,} ОЧОК",
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
                    text=f"🔒 ПОТРІБНО {cfg.cost:,} 🪙 (БРАКУЄ {needed:,})",
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
