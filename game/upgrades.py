"""Модуль системи карток покращень (Upgrades) для Galaxy Defender."""

import random
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText


_upgrade_applied_counts: dict[str, int] = {}


def reset_upgrade_counts():
    """Resets the applied counts — call at the start of each new game."""
    global _upgrade_applied_counts
    _upgrade_applied_counts.clear()


def record_upgrade_applied(uid: str):
    """Records that an upgrade was applied — increments its stack counter."""
    _upgrade_applied_counts[uid] = _upgrade_applied_counts.get(uid, 0) + 1


class Upgrade:
    """Модель конкретного покращення корабля гравця."""

    def __init__(
        self,
        uid: str,
        title: str,
        desc: str,
        icon: str,
        color: tuple,
        apply_fn,
        tier: int = 1,
        max_stack: int = 3,
    ):
        self.uid = uid
        self.title = title
        self.desc = desc
        self.icon = icon
        self.color = color  # RGBA
        self.apply_fn = apply_fn
        self.tier = tier
        self.max_stack = max_stack

    def apply(self, player):
        """Застосовує ефект покращення до сутності гравця."""
        self.apply_fn(player)


def get_random_upgrades(player, count: int = 3) -> list[Upgrade]:
    """Генерує список із випадкових доступних покращень відповідно до поточного стану гравця."""
    available: list[Upgrade] = []

    # 1. Мульти-лазер (Подвійний або Потрійний)
    if player.shot_level == 1:
        available.append(
            Upgrade(
                uid="multi_shot_2",
                title="Подвійний лазер",
                desc="Залп 2 паралельними лазерами одночасно",
                icon="💥",
                color=(1.0, 0.35, 0.8, 1.0),
                apply_fn=lambda p: setattr(p, "shot_level", 2),
                tier=2,
                max_stack=1,
            )
        )
    elif player.shot_level == 2:
        available.append(
            Upgrade(
                uid="multi_shot_3",
                title="Потрійний лазер",
                desc="Віяловий залп 3 лазерами по фронту",
                icon="✨",
                color=(1.0, 0.3, 0.9, 1.0),
                apply_fn=lambda p: setattr(p, "shot_level", 3),
                tier=3,
                max_stack=1,
            )
        )

    # 2. Швидкострільність
    available.append(
        Upgrade(
            uid="rapid_fire",
            title="Швидкострільність",
            desc="+30% до темпу стрільби лазерами",
            icon="⚡",
            color=(0.2, 0.9, 1.0, 1.0),
            apply_fn=lambda p: setattr(
                p, "fire_cooldown", max(0.08, p.fire_cooldown * 0.72)
            ),
        )
    )

    # 3. Потужність снарядів
    available.append(
        Upgrade(
            uid="damage_boost",
            title="Потужні заряди",
            desc="+18 до шкоди кожного лазерного влучання",
            icon="☄️",
            color=(1.0, 0.5, 0.15, 1.0),
            apply_fn=lambda p: setattr(p, "bullet_damage", p.bullet_damage + 18),
        )
    )

    # 4. Енергетичний силовий щит
    available.append(
        Upgrade(
            uid="energy_shield",
            title="Енергощит (+2)",
            desc="+2 заряди силового поля (поглинає удари)",
            icon="🛡️",
            color=(0.25, 0.75, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "shield", p.shield + 2),
                p.redraw(),
            ),
        )
    )

    # 5. Нано-броня та відновлення HP
    available.append(
        Upgrade(
            uid="nano_armor",
            title="Нано-броня & Ремонт",
            desc="+25 до макс. HP та повне відновлення здоров'я",
            icon="❤️",
            color=(0.2, 1.0, 0.45, 1.0),
            apply_fn=lambda p: (
                setattr(p, "max_hp", p.max_hp + 25),
                setattr(p, "hp", p.max_hp),
            ),
        )
    )

    # 6. Турбодвигуни
    available.append(
        Upgrade(
            uid="warp_speed",
            title="Турбодвигуни",
            desc="+25% до швидкості та маневреності корабля",
            icon="🚀",
            color=(1.0, 0.85, 0.2, 1.0),
            apply_fn=lambda p: setattr(
                p, "speed", min(580.0, p.speed * 1.25)
            ),
        )
    )

    # 7. Гіперзвуковий лазер
    available.append(
        Upgrade(
            uid="hyper_laser",
            title="Гіперзвуковий лазер",
            desc="+35% до швидкості польоту куль та +8 шкоди",
            icon="🎯",
            color=(0.7, 0.45, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "bullet_speed", min(1200.0, p.bullet_speed * 1.35)),
                setattr(p, "bullet_damage", p.bullet_damage + 8),
            ),
        )
    )

    # 8. Плазмове насичення
    available.append(
        Upgrade(
            uid="plasma_infusion",
            title="Плазмове насичення",
            desc="+16 шкоди та +40 до швидкості куль",
            icon="🔥",
            color=(1.0, 0.42, 0.18, 1.0),
            apply_fn=lambda p: (
                setattr(p, "bullet_damage", p.bullet_damage + 16),
                setattr(p, "bullet_speed", min(1200.0, p.bullet_speed + 40)),
            ),
        )
    )

    # 9. Кріогенне гартування
    available.append(
        Upgrade(
            uid="cryo_rounds",
            title="Кріогенне гартування",
            desc="+12 шкоди та +30 до швидкості куль",
            icon="❄️",
            color=(0.45, 0.85, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "bullet_damage", p.bullet_damage + 12),
                setattr(p, "bullet_speed", min(1200.0, p.bullet_speed + 30)),
            ),
        )
    )

    # 10. Квантовий оверклокінг
    available.append(
        Upgrade(
            uid="quantum_overclock",
            title="Квантовий оверклокінг",
            desc="-35% перезарядки + +10% швидкості корабля",
            icon="⚛️",
            color=(0.55, 0.95, 0.4, 1.0),
            apply_fn=lambda p: (
                setattr(p, "fire_cooldown", max(0.06, p.fire_cooldown * 0.65)),
                setattr(p, "speed", min(580.0, p.speed * 1.10)),
            ),
        )
    )

    # 11. Важкий калібр
    available.append(
        Upgrade(
            uid="heavy_calibre",
            title="Важкий калібр",
            desc="+28 до шкоди кожного влучання",
            icon="💣",
            color=(1.0, 0.62, 0.1, 1.0),
            apply_fn=lambda p: setattr(p, "bullet_damage", p.bullet_damage + 28),
        )
    )

    # 12. Перевантаження Егіди
    available.append(
        Upgrade(
            uid="aegis_overcharge",
            title="Перевантаження Егіди",
            desc="+3 заряди щита — пасивний захист",
            icon="🛡️",
            color=(0.2, 0.6, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "shield", p.shield + 3),
                p.redraw(),
            ),
        )
    )

    # 13. Наніти-ремонтники
    available.append(
        Upgrade(
            uid="nanite_repair",
            title="Наніти-ремонтники",
            desc="+35 до макс. HP та повне відновлення",
            icon="🧬",
            color=(0.15, 1.0, 0.55, 1.0),
            apply_fn=lambda p: (
                setattr(p, "max_hp", p.max_hp + 35),
                setattr(p, "hp", p.max_hp),
            ),
        )
    )

    # 14. Імпульсний форсаж
    available.append(
        Upgrade(
            uid="impulse_afterburner",
            title="Імпульсний форсаж",
            desc="+35% до швидкості корабля (max 580)",
            icon="💨",
            color=(0.35, 0.95, 0.75, 1.0),
            apply_fn=lambda p: setattr(p, "speed", min(580.0, p.speed * 1.35)),
        )
    )

    # 15. Тахіонний прискорювач
    available.append(
        Upgrade(
            uid="tachyon_accelerator",
            title="Тахіонний прискорювач",
            desc="+45% швидкості куль та +12 шкоди",
            icon="💫",
            color=(0.75, 0.55, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "bullet_speed", min(1200.0, p.bullet_speed * 1.45)),
                setattr(p, "bullet_damage", p.bullet_damage + 12),
            ),
        )
    )

    # 16. Матриця критичного фокусу
    available.append(
        Upgrade(
            uid="critical_matrix",
            title="Матриця критичного фокусу",
            desc="+22 шкоди та -15% перезарядки",
            icon="🎯",
            color=(1.0, 0.35, 0.6, 1.0),
            apply_fn=lambda p: (
                setattr(p, "bullet_damage", p.bullet_damage + 22),
                setattr(p, "fire_cooldown", max(0.06, p.fire_cooldown * 0.85)),
            ),
        )
    )

    # 17. Антиматеріальний заряд
    available.append(
        Upgrade(
            uid="antimatter_warhead",
            title="Антиматеріальний заряд",
            desc="+36 до шкоди — найпотужніший удар",
            icon="☢️",
            color=(1.0, 0.22, 0.22, 1.0),
            apply_fn=lambda p: setattr(p, "bullet_damage", p.bullet_damage + 36),
        )
    )

    # 18. Хроно-стабілізатор систем
    available.append(
        Upgrade(
            uid="chrono_stabilizer",
            title="Хроно-стабілізатор",
            desc="-15% перезарядки, +15% швидкості, +15 HP",
            icon="⏳",
            color=(0.85, 0.75, 0.25, 1.0),
            apply_fn=lambda p: (
                setattr(p, "fire_cooldown", max(0.06, p.fire_cooldown * 0.85)),
                setattr(p, "speed", min(580.0, p.speed * 1.15)),
                setattr(p, "max_hp", p.max_hp + 15),
                setattr(p, "hp", min(p.max_hp, p.hp + 15)),
            ),
        )
    )

    # 19. Ядро Зоряного Фенікса
    available.append(
        Upgrade(
            uid="stellar_phoenix_core",
            title="Ядро Зоряного Фенікса",
            desc="+2 щита, +20 HP, +14 шкоди — легендарний",
            icon="🌟",
            color=(1.0, 0.88, 0.22, 1.0),
            apply_fn=lambda p: (
                setattr(p, "shield", p.shield + 2),
                p.redraw(),
                setattr(p, "max_hp", p.max_hp + 20),
                setattr(p, "hp", min(p.max_hp, p.hp + 20)),
                setattr(p, "bullet_damage", p.bullet_damage + 14),
            ),
        )
    )

    # 20. Нейронна синхронізація
    available.append(
        Upgrade(
            uid="neural_sync",
            title="Нейронна синхронізація",
            desc="-20% перезарядки, +8 шкоди, +10% швидкості",
            icon="🧠",
            color=(0.5, 0.85, 1.0, 1.0),
            apply_fn=lambda p: (
                setattr(p, "fire_cooldown", max(0.06, p.fire_cooldown * 0.80)),
                setattr(p, "bullet_damage", p.bullet_damage + 8),
                setattr(p, "speed", min(580.0, p.speed * 1.10)),
            ),
        )
    )

    pick_count = min(count, len(available))
    return random.sample(available, pick_count)


class UpgradeCard(BoxLayout):
    """Візуальна інтерактивна картка покращення."""

    def __init__(self, upgrade: Upgrade, on_select, **kwargs):
        super().__init__(**kwargs)
        self.upgrade = upgrade
        self.on_select = on_select
        self.orientation = "horizontal"
        self.size_hint = (1, None)
        self.height = 94
        self.padding = [14, 6, 12, 6]
        self.spacing = 10

        # Напівпрозорий темний фон картки з неоновим обрамленням та акцентною смужкою
        with self.canvas.before:
            Color(0.04, 0.07, 0.15, 0.94)
            self.bg_rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[12]
            )
            r, g, b, _ = upgrade.color
            # Акцентна неонова енергетична смужка зліва
            Color(r, g, b, 0.95)
            self.accent_bar = RoundedRectangle(
                pos=(self.x + 4, self.y + 8),
                size=(4, max(1, self.height - 16)),
                radius=[2],
            )
            # Неонова рамка
            Color(r, g, b, 0.75)
            self.border_line = Line(
                rounded_rectangle=[self.x, self.y, self.width, self.height, 12],
                width=1.5,
            )

        self.bind(pos=self._update_canvas, size=self._update_canvas)

        # 1. Значок / Іконка
        self.icon_label = MDLabel(
            text=upgrade.icon,
            halign="center",
            valign="center",
            size_hint=(None, 1),
            width=44,
            font_style="Headline",
            role="medium",
        )
        self.add_widget(self.icon_label)

        # 2. Текстовий блок (Назва + Опис)
        text_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=2,
            padding=[4, 2, 4, 2],
        )
        self.title_label = MDLabel(
            text=upgrade.title,
            bold=True,
            font_style="Title",
            role="medium",
            theme_text_color="Custom",
            text_color=upgrade.color,
            size_hint=(1, None),
            height=26,
        )
        self.desc_label = MDLabel(
            text=upgrade.desc,
            font_style="Body",
            role="small",
            theme_text_color="Custom",
            text_color=(0.82, 0.88, 0.95, 0.9),
            size_hint=(1, 1),
        )
        text_box.add_widget(self.title_label)
        text_box.add_widget(self.desc_label)
        self.add_widget(text_box)

        # 3. Кнопка «УСТАНОВИТИ»
        self.select_btn = MDButton(
            MDButtonText(
                text="🚀 УСТАНОВИТИ",
                font_style="Label",
                role="large",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 1.0, 1.0, 1.0),
            ),
            style="filled",
            size_hint=(None, None),
            size=(96, 42),
            pos_hint={"center_y": 0.5},
            theme_bg_color="Custom",
            md_bg_color=upgrade.color,
        )
        self.select_btn.bind(on_release=lambda *args: self.on_select(self.upgrade))
        self.add_widget(self.select_btn)

    def on_touch_down(self, touch):
        """Дозволяє вибрати покращення натисканням у будь-яку область картки."""
        if self.collide_point(*touch.pos):
            if self.select_btn.collide_point(*touch.pos):
                return super().on_touch_down(touch)
            self.on_select(self.upgrade)
            return True
        return super().on_touch_down(touch)

    def _update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.accent_bar.pos = (self.x + 4, self.y + 8)
        self.accent_bar.size = (4, max(1, self.height - 16))
        self.border_line.rounded_rectangle = [
            self.x,
            self.y,
            self.width,
            self.height,
            12,
        ]


class UpgradeOverlay(FloatLayout):
    """Оверлей вибору карток покращень (пауза гри при досягненні 1000 очок)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)

        # Напівпрозоре затемнення ігрового поля
        with self.canvas.before:
            Color(0.01, 0.03, 0.07, 0.90)
            self.dim_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda *a: setattr(self.dim_rect, "pos", self.pos),
            size=lambda *a: setattr(self.dim_rect, "size", self.size),
        )

        # Головний модальний контейнер
        self.card_container = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            size=(380, 470),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[16, 16, 16, 16],
            spacing=8,
        )
        with self.card_container.canvas.before:
            Color(0.03, 0.06, 0.13, 0.98)
            self.modal_bg = RoundedRectangle(
                pos=self.card_container.pos,
                size=self.card_container.size,
                radius=[18],
            )
            Color(0.18, 0.75, 1.0, 0.85)
            self.modal_border = Line(
                rounded_rectangle=[
                    self.card_container.x,
                    self.card_container.y,
                    self.card_container.width,
                    self.card_container.height,
                    18,
                ],
                width=2.0,
            )
        self.card_container.bind(
            pos=self._update_modal_canvas,
            size=self._update_modal_canvas,
        )

        # Заголовок
        self.title_label = MDLabel(
            text="[ ТАКТИЧНА МОДЕРНІЗАЦІЯ // UPGRADE ]",
            halign="center",
            bold=True,
            font_style="Title",
            role="large",
            theme_text_color="Custom",
            text_color=(1.0, 0.82, 0.25, 1.0),
            size_hint=(1, None),
            height=34,
        )
        self.card_container.add_widget(self.title_label)

        # Підзаголовок з досягнутим рахунком
        self.subtitle_label = MDLabel(
            text="⚡ ДОСЯГНУТО РУБІЖ // ОБЕРІТЬ ПРОТОКОЛ:",
            halign="center",
            font_style="Body",
            role="medium",
            theme_text_color="Custom",
            text_color=(0.7, 0.88, 1.0, 0.95),
            size_hint=(1, None),
            height=26,
        )
        self.card_container.add_widget(self.subtitle_label)

        # Список карток
        self.cards_list = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            spacing=8,
        )
        self.card_container.add_widget(self.cards_list)
        self.current_cards: list[UpgradeCard] = []

        self.add_widget(self.card_container)
        self.bind(size=self._on_overlay_resize)

    def _on_overlay_resize(self, *args):
        if self.width > 50 and self.height > 50:
            self.card_container.width = min(380, max(280, self.width - 24))
            self.card_container.height = min(470, max(360, self.height - 30))

    def _update_modal_canvas(self, *args):
        self.modal_bg.pos = self.card_container.pos
        self.modal_bg.size = self.card_container.size
        self.modal_border.rounded_rectangle = [
            self.card_container.x,
            self.card_container.y,
            self.card_container.width,
            self.card_container.height,
            18,
        ]

    def show_cards(
        self,
        upgrades: list[Upgrade],
        score: int,
        on_select,
        upgrade_level: int = 1,
        next_cost: int = 1500,
    ):
        """Очищує старі картки та наповнює контейнер новим вибором."""
        self.cards_list.clear_widgets()
        self.current_cards.clear()
        self.subtitle_label.text = (
            f"ПРОТОКОЛ #{upgrade_level} ({score} оч.) | Наступний: +{next_cost} очок"
        )
        for u in upgrades:
            card = UpgradeCard(upgrade=u, on_select=on_select)
            self.cards_list.add_widget(card)
            self.current_cards.append(card)

    def select_by_index(self, index: int):
        """Вибирає картку за її порядковим номером (0, 1, 2) — для швидких клавіш 1-3."""
        if 0 <= index < len(self.current_cards):
            card = self.current_cards[index]
            card.on_select(card.upgrade)
