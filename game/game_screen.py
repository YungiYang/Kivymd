"""Ігровий екран із повним ігровим циклом, колізіями, HUD, звуками, кораблями, біомами та паузою."""

import random
import math
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText

from game.constants import (
    FRAME_INTERVAL,
    PLAYER_MAX_HP,
    ENEMY_SPAWN_INTERVAL,
)
from game.background import ParallaxBackground
from game.audio import get_audio_manager
from game.storage import (
    get_credits,
    add_credits,
    get_selected_ship,
    update_high_score,
    is_sound_enabled,
    is_music_enabled,
)
from game.ships import get_ship_config
from game.biomes import get_biome_config, get_next_random_biome
from game.entities import (
    PlayerShip,
    Enemy,
    Boss,
    Bullet,
    LaserBeam,
    PlasmaOrb,
    Particle,
    FloatingText,
    check_collision,
    create_explosion,
)
from game.upgrades import UpgradeOverlay, get_random_upgrades
from game.advanced_enemies import AdvancedEnemy, EliteBoss, spawn_enemy_for_biome
from game.obstacles import Obstacle, spawn_obstacle
from game.abilities import PlayerAbilities, roll_passive_drop, roll_active_drop
from game.materials import roll_drops


class GameScreen(MDScreen):
    """Головний ігровий екран із 60 FPS циклом, 9 біомами, звуками та унікальними кораблями."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game_screen"

        # Стан гри
        self.is_playing = False
        self.is_paused = False
        self.is_upgrading = False
        self.score = 0
        self.upgrade_level = 0
        self.upgrade_base_cost = 1000
        self.upgrade_cost_step = 500
        self.next_upgrade_score = 1000
        self.spawn_timer = 0.0
        self.game_clock_event = None

        # Біоми та рівні
        self.current_level = 1
        self.current_biome = "space"
        self.visited_biomes = ["space"]
        self.next_level_score = 2500
        self.level_banner_timer = 0.0
        self.level_banner_active = False

        # Бос та ескалація складності
        self.boss: Boss | None = None
        self.elite_boss: EliteBoss | None = None
        self.boss_level: int = 0
        self.next_boss_score: int = 2000
        self.boss_warning_timer: float = 0.0
        self.boss_warning_active: bool = False

        # Керування
        self.auto_fire = True
        self.is_shooting = False
        self.keys_pressed = set()

        # Списки ігрових сутностей
        self.enemies: list = []
        self.bullets: list[Bullet] = []
        self.particles: list[Particle] = []
        self.floating_texts: list[FloatingText] = []
        self.obstacles: list[Obstacle] = []

        # Здібності гравця
        self.abilities = PlayerAbilities()

        # Таймери перешкод
        self.obstacle_spawn_timer = 0.0
        self.obstacle_spawn_interval = 8.0  # секунди між появою перешкод

        # Спалах сповіщення про дроп предметів
        self.drop_notification_timer = 0.0
        self.drop_notification_text = ""

        self._build_ui()

    def _build_ui(self):
        """Створює структуру інтерфейсу гри."""
        self.root_layout = FloatLayout(size_hint=(1, 1))

        # 1. Двошаровий рухомий фон з підтримкою біомів
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.root_layout.add_widget(self.bg)

        # 2. Шар ігрового простору (де малюються кораблі та снаряди)
        self.game_area = Widget(size_hint=(1, 1))
        self.root_layout.add_widget(self.game_area)

        # 3. Шар часточок вибухів (власний Canvas)
        self.effects_widget = Widget(size_hint=(1, 1))
        self.root_layout.add_widget(self.effects_widget)

        # 4. Корабель гравця
        self.player = PlayerShip()
        self.game_area.add_widget(self.player)

        # 4.1 Фотонний лазер для променевого корабля («Геліос»)
        self.laser_beam = LaserBeam(0, 0, 0)
        self.laser_beam.opacity = 0.0
        self.game_area.add_widget(self.laser_beam)

        # 5. Верхня панель (HUD)
        self._build_hud()

        # 5.1 Панель здоров'я боса
        self._build_boss_hud()

        # 5.2 Банер попередження про наближення боса
        self._build_boss_warning()

        # 5.3 Банер оголошення переходу на новий біом/рівень
        self._build_level_banner()

        # 6. Нижні екранні кнопки керування для Android
        self._build_controls()

        # 7. Оверлей паузи
        self._build_pause_overlay()

        # 8. Оверлей вибору карток покращень (з прогресивною вартістю)
        self.upgrade_overlay = UpgradeOverlay()
        self.upgrade_overlay.opacity = 0.0
        self.upgrade_overlay.disabled = True

        self.add_widget(self.root_layout)

    def _build_hud(self):
        """Створює кіберпанк панель HUD із HP, біомом, кредитами, рахунком та кнопкою паузи."""
        self.hud_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=64,
            pos_hint={"top": 1.0, "x": 0.0},
            padding=[10, 4, 10, 4],
            spacing=8,
        )

        with self.hud_box.canvas.before:
            Color(0.04, 0.07, 0.14, 0.88)
            self.hud_bg = RoundedRectangle(
                pos=self.hud_box.pos, size=self.hud_box.size, radius=[0, 0, 8, 8]
            )
            Color(0.12, 0.45, 0.85, 0.4)
            self.hud_border = Line(
                rounded_rectangle=[
                    self.hud_box.x,
                    self.hud_box.y,
                    self.hud_box.width,
                    self.hud_box.height,
                    0,
                    0,
                    8,
                    8,
                ],
                width=1.2,
            )
        self.hud_box.bind(
            pos=self._update_hud_bg_canvas,
            size=self._update_hud_bg_canvas,
        )

        # Лівий блок: HP + Смужка життя + Назва корабля
        hp_container = BoxLayout(
            orientation="vertical",
            size_hint=(0.42, 1),
            spacing=2,
            padding=[0, 2, 0, 2],
        )
        self.hp_label = MDLabel(
            text=f"HP: {PLAYER_MAX_HP}/{PLAYER_MAX_HP}",
            theme_text_color="Custom",
            text_color=(0.2, 1.0, 0.4, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=20,
        )
        hp_container.add_widget(self.hp_label)

        self.hp_bar_widget = Widget(size_hint=(1, None), height=7)
        with self.hp_bar_widget.canvas:
            Color(0.10, 0.14, 0.22, 0.95)
            self.hp_track_rect = RoundedRectangle(
                pos=self.hp_bar_widget.pos,
                size=self.hp_bar_widget.size,
                radius=[3],
            )
            self.hp_fill_color = Color(0.2, 0.95, 0.4, 1.0)
            self.hp_fill_rect = RoundedRectangle(
                pos=self.hp_bar_widget.pos,
                size=self.hp_bar_widget.size,
                radius=[3],
            )
        self.hp_bar_widget.bind(
            pos=self._update_hp_bar_canvas,
            size=self._update_hp_bar_canvas,
        )
        hp_container.add_widget(self.hp_bar_widget)

        self.ship_name_label = MDLabel(
            text="⚡ ФЕНІКС",
            theme_text_color="Custom",
            text_color=(0.4, 0.75, 1.0, 0.8),
            font_style="Body",
            role="small",
            size_hint=(1, None),
            height=16,
        )
        hp_container.add_widget(self.ship_name_label)
        self.hud_box.add_widget(hp_container)

        # Центральний блок: Рахунок, Кредити та Біом
        score_container = BoxLayout(
            orientation="vertical",
            size_hint=(0.44, 1),
            spacing=1,
            padding=[0, 2, 0, 2],
        )
        self.score_label = MDLabel(
            text="SCORE: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=22,
        )

        sub_info_box = BoxLayout(orientation="horizontal", size_hint=(1, None), height=20, spacing=4)
        self.credits_label = MDLabel(
            text=f"🪙 {get_credits()}",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.25, 1.0),
            font_style="Body",
            role="small",
            bold=True,
            size_hint=(0.5, 1),
        )
        self.level_badge_label = MDLabel(
            text="🌌 РІВЕНЬ 1",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.5, 0.85, 1.0, 1.0),
            font_style="Body",
            role="small",
            bold=True,
            size_hint=(0.5, 1),
        )
        sub_info_box.add_widget(self.credits_label)
        sub_info_box.add_widget(self.level_badge_label)

        score_container.add_widget(self.score_label)
        score_container.add_widget(sub_info_box)
        self.hud_box.add_widget(score_container)

        # Права кнопка паузи
        self.pause_btn = MDButton(
            MDButtonText(
                text="II",
                font_style="Title",
                role="medium",
                bold=True,
                theme_text_color="Custom",
                text_color=(1.0, 1.0, 1.0, 1.0),
            ),
            style="filled",
            size_hint=(None, None),
            size=(52, 42),
            pos_hint={"center_y": 0.5},
            theme_bg_color="Custom",
            md_bg_color=(0.18, 0.32, 0.52, 0.95),
        )
        self.pause_btn.bind(on_release=self.toggle_pause)
        self.hud_box.add_widget(self.pause_btn)

        self.root_layout.add_widget(self.hud_box)

    def _update_hud_bg_canvas(self, *args):
        if hasattr(self, "hud_bg"):
            self.hud_bg.pos = self.hud_box.pos
            self.hud_bg.size = self.hud_box.size
            self.hud_border.rounded_rectangle = [
                self.hud_box.x,
                self.hud_box.y,
                self.hud_box.width,
                self.hud_box.height,
                0,
                0,
                8,
                8,
            ]

    def _build_boss_hud(self):
        """Створює верхню панель здоров'я для ворожого боса."""
        self.boss_bar_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.88, None),
            height=38,
            pos_hint={"center_x": 0.5, "top": 0.91},
            padding=[8, 2, 8, 4],
            spacing=2,
        )
        self.boss_bar_box.opacity = 0.0

        with self.boss_bar_box.canvas.before:
            Color(0.06, 0.08, 0.16, 0.88)
            self.boss_bg_rect = RoundedRectangle(
                pos=self.boss_bar_box.pos, size=self.boss_bar_box.size, radius=[6]
            )
            Color(1.0, 0.2, 0.35, 0.9)
            self.boss_border_line = Line(
                rounded_rectangle=[
                    self.boss_bar_box.x,
                    self.boss_bar_box.y,
                    self.boss_bar_box.width,
                    self.boss_bar_box.height,
                    6,
                ],
                width=1.5,
            )

        self.boss_bar_box.bind(
            pos=self._update_boss_bar_canvas,
            size=self._update_boss_bar_canvas,
        )

        self.boss_title_label = MDLabel(
            text="☠️ БОС РІВЕНЬ 1",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.35, 0.45, 1.0),
            font_style="Title",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=16,
        )
        self.boss_bar_box.add_widget(self.boss_title_label)

        self.boss_hp_widget = Widget(size_hint=(1, None), height=9)
        with self.boss_hp_widget.canvas:
            Color(0.18, 0.08, 0.14, 0.95)
            self.boss_hp_track = RoundedRectangle(
                pos=self.boss_hp_widget.pos, size=self.boss_hp_widget.size, radius=[4]
            )
            Color(1.0, 0.18, 0.32, 1.0)
            self.boss_hp_fill = RoundedRectangle(
                pos=self.boss_hp_widget.pos, size=self.boss_hp_widget.size, radius=[4]
            )

        self.boss_hp_widget.bind(
            pos=self._update_boss_hp_canvas,
            size=self._update_boss_hp_canvas,
        )
        self.boss_bar_box.add_widget(self.boss_hp_widget)
        self.root_layout.add_widget(self.boss_bar_box)

    def _build_boss_warning(self):
        """Створює банер попередження про появу боса."""
        self.boss_warning_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.94, None),
            height=54,
            pos_hint={"center_x": 0.5, "center_y": 0.58},
            padding=[10, 6, 10, 6],
        )
        self.boss_warning_box.opacity = 0.0

        with self.boss_warning_box.canvas.before:
            Color(0.08, 0.02, 0.04, 0.92)
            self.warning_bg_rect = RoundedRectangle(
                pos=self.boss_warning_box.pos,
                size=self.boss_warning_box.size,
                radius=[10],
            )
            Color(1.0, 0.25, 0.2, 0.95)
            self.warning_border_line = Line(
                rounded_rectangle=[
                    self.boss_warning_box.x,
                    self.boss_warning_box.y,
                    self.boss_warning_box.width,
                    self.boss_warning_box.height,
                    10,
                ],
                width=2.0,
            )

        self.boss_warning_box.bind(
            pos=self._update_warning_canvas,
            size=self._update_warning_canvas,
        )

        self.boss_warning_label = MDLabel(
            text="⚠️ УВАГА! НАБЛИЖАЄТЬСЯ ФЛАГМАН БОС! ⚠️",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.2, 1.0),
            font_style="Title",
            role="medium",
            bold=True,
            size_hint=(1, 1),
        )
        self.boss_warning_box.add_widget(self.boss_warning_label)
        self.root_layout.add_widget(self.boss_warning_box)

    def _build_level_banner(self):
        """Створює банер гіперстрибка на новий рівень."""
        self.level_banner_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.94, None),
            height=72,
            pos_hint={"center_x": 0.5, "center_y": 0.62},
            padding=[10, 6, 10, 6],
            spacing=3,
        )
        self.level_banner_box.opacity = 0.0

        with self.level_banner_box.canvas.before:
            Color(0.05, 0.08, 0.16, 0.94)
            self.lvl_banner_bg = RoundedRectangle(
                pos=self.level_banner_box.pos,
                size=self.level_banner_box.size,
                radius=[12],
            )
            Color(0.2, 0.85, 1.0, 0.9)
            self.lvl_banner_border = Line(
                rounded_rectangle=[
                    self.level_banner_box.x,
                    self.level_banner_box.y,
                    self.level_banner_box.width,
                    self.level_banner_box.height,
                    12,
                ],
                width=2.0,
            )

        self.level_banner_box.bind(
            pos=self._update_lvl_banner_canvas,
            size=self._update_lvl_banner_canvas,
        )

        self.level_title_label = MDLabel(
            text="🚀 РІВЕНЬ 1: ГЛИБОКИЙ КОСМОС",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.95, 1.0, 1.0),
            font_style="Title",
            role="medium",
            bold=True,
            size_hint=(1, None),
            height=28,
        )
        self.level_hazard_label = MDLabel(
            text="⚠️ НЕБЕЗПЕКА: Стандартні умови",
            halign="center",
            theme_text_color="Custom",
            text_color=(1.0, 0.85, 0.25, 0.95),
            font_style="Body",
            role="small",
            bold=True,
            size_hint=(1, None),
            height=24,
        )
        self.level_banner_box.add_widget(self.level_title_label)
        self.level_banner_box.add_widget(self.level_hazard_label)
        self.root_layout.add_widget(self.level_banner_box)

    def _update_lvl_banner_canvas(self, *args):
        if hasattr(self, "lvl_banner_bg") and hasattr(self, "level_banner_box"):
            self.lvl_banner_bg.pos = self.level_banner_box.pos
            self.lvl_banner_bg.size = self.level_banner_box.size
            self.lvl_banner_border.rounded_rectangle = [
                self.level_banner_box.x,
                self.level_banner_box.y,
                self.level_banner_box.width,
                self.level_banner_box.height,
                12,
            ]

    def _build_controls(self):
        """Створює зручні сенсорні кнопки внизу екрана для Android."""
        self.controls_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=68,
            pos_hint={"bottom": 1.0, "x": 0.0},
            padding=[20, 6, 20, 10],
            spacing=24,
        )

        self.btn_left = MDButton(
            MDButtonText(text="< ЛІВОРУЧ", font_style="Title", role="small"),
            style="elevated",
            size_hint=(0.35, 1),
            theme_bg_color="Custom",
            md_bg_color=(0.15, 0.25, 0.4, 0.7),
        )
        self.btn_left.min_state_time = 0.0
        self.btn_left.bind(
            state=lambda inst, val: self.player.set_move_direction(-1 if val == "down" else 0)
        )
        self.controls_box.add_widget(self.btn_left)

        self.btn_fire = MDButton(
            MDButtonText(text="ВОГОНЬ", font_style="Title", role="small"),
            style="filled",
            size_hint=(0.3, 1),
            theme_bg_color="Custom",
            md_bg_color=(0.95, 0.3, 0.2, 0.85),
        )
        self.btn_fire.min_state_time = 0.0
        self.btn_fire.bind(
            state=lambda inst, val: self._set_shooting(val == "down")
        )
        self.controls_box.add_widget(self.btn_fire)

        self.btn_right = MDButton(
            MDButtonText(text="ПРАВОРУЧ >", font_style="Title", role="small"),
            style="elevated",
            size_hint=(0.35, 1),
            theme_bg_color="Custom",
            md_bg_color=(0.15, 0.25, 0.4, 0.7),
        )
        self.btn_right.min_state_time = 0.0
        self.btn_right.bind(
            state=lambda inst, val: self.player.set_move_direction(1 if val == "down" else 0)
        )
        self.controls_box.add_widget(self.btn_right)

        self.root_layout.add_widget(self.controls_box)

    def _build_pause_overlay(self):
        """Створює екран паузи з перемикачами аудіо."""
        self.pause_overlay = FloatLayout(
            size_hint=(1, 1),
            pos_hint={"x": 0.0, "y": 0.0},
        )
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        with self.pause_overlay.canvas.before:
            Color(0.02, 0.04, 0.08, 0.88)
            self.overlay_rect = Rectangle(
                pos=self.pause_overlay.pos, size=self.pause_overlay.size
            )
        self.pause_overlay.bind(
            pos=lambda *args: setattr(self.overlay_rect, "pos", self.pause_overlay.pos),
            size=lambda *args: setattr(self.overlay_rect, "size", self.pause_overlay.size),
        )

        menu_card = BoxLayout(
            orientation="vertical",
            size_hint=(0.84, None),
            height=340,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[20, 20, 20, 20],
            spacing=14,
        )
        with menu_card.canvas.before:
            Color(0.08, 0.12, 0.22, 0.96)
            self.card_bg = RoundedRectangle(
                pos=menu_card.pos, size=menu_card.size, radius=[12]
            )
            Color(0.2, 0.8, 1.0, 0.5)
            self.card_border = Line(
                rounded_rectangle=[
                    menu_card.x,
                    menu_card.y,
                    menu_card.width,
                    menu_card.height,
                    12,
                ],
                width=1.5,
            )
        menu_card.bind(
            pos=lambda *args: self._update_card_canvas(menu_card),
            size=lambda *args: self._update_card_canvas(menu_card),
        )

        pause_title = MDLabel(
            text="ПАУЗА",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            font_style="Headline",
            role="medium",
            bold=True,
            size_hint=(1, None),
            height=36,
        )
        menu_card.add_widget(pause_title)

        self.resume_btn = MDButton(
            MDButtonText(text="ПРОДОВЖИТИ", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=48,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.7, 0.45, 1.0),
        )
        self.resume_btn.bind(on_release=self.resume_game)
        menu_card.add_widget(self.resume_btn)

        sound_txt = "🔊 ЗВУКИ: УВІМК" if is_sound_enabled() else "🔇 ЗВУКИ: ВИМК"
        self.pause_sound_btn = MDButton(
            MDButtonText(text=sound_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(1, None),
            height=44,
        )
        self.pause_sound_btn.bind(on_release=self._toggle_sound_pause)
        menu_card.add_widget(self.pause_sound_btn)

        music_txt = "🎵 МУЗИКА: УВІМК" if is_music_enabled() else "🔇 МУЗИКА: ВИМК"
        self.pause_music_btn = MDButton(
            MDButtonText(text=music_txt, font_style="Title", role="small"),
            style="outlined",
            size_hint=(1, None),
            height=44,
        )
        self.pause_music_btn.bind(on_release=self._toggle_music_pause)
        menu_card.add_widget(self.pause_music_btn)

        self.menu_btn = MDButton(
            MDButtonText(
                text="ГОЛОВНЕ МЕНЮ",
                font_style="Title",
                role="small",
                theme_text_color="Custom",
                text_color=(0.9, 0.4, 0.4, 1.0),
            ),
            style="outlined",
            size_hint=(1, None),
            height=44,
        )
        self.menu_btn.bind(on_release=self._quit_to_menu)
        menu_card.add_widget(self.menu_btn)

        self.pause_overlay.add_widget(menu_card)

    def _update_card_canvas(self, card):
        if hasattr(self, "card_bg"):
            self.card_bg.pos = card.pos
            self.card_bg.size = card.size
            self.card_border.rounded_rectangle = [
                card.x,
                card.y,
                card.width,
                card.height,
                12,
            ]

    def _toggle_sound_pause(self, *args):
        active = get_audio_manager().toggle_sound()
        for child in self.pause_sound_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🔊 ЗВУКИ: УВІМК" if active else "🔇 ЗВУКИ: ВИМК"

    def _toggle_music_pause(self, *args):
        active = get_audio_manager().toggle_music()
        for child in self.pause_music_btn.children:
            if isinstance(child, MDButtonText):
                child.text = "🎵 МУЗИКА: УВІМК" if active else "🔇 МУЗИКА: ВИМК"

    def _set_shooting(self, active: bool):
        self.is_shooting = active

    def start_new_game(self):
        """Ініціалізує нову гру, скидає біом на 'space' та запускає ігровий цикл."""
        self._clear_all_entities()

        self.score = 0
        self.upgrade_level = 0
        self.next_upgrade_score = 1000
        self.boss = None
        self.boss_level = 0
        self.next_boss_score = 2000
        self.boss_warning_timer = 0.0
        self.boss_warning_active = False

        # Скидання системи біомів
        self.current_level = 1
        self.current_biome = "space"
        self.visited_biomes = ["space"]
        self.next_level_score = 2500
        self.level_banner_active = False
        self.level_banner_timer = 0.0
        if hasattr(self, "level_banner_box"):
            self.level_banner_box.opacity = 0.0

        self.spawn_timer = 0.0
        self.is_paused = False
        self.is_playing = True
        self.is_shooting = False
        self.is_upgrading = False

        # Завантажуємо вибраний корабель з ангару
        equipped_ship_id = get_selected_ship()
        self.player.apply_ship_id(equipped_ship_id)
        self.player.reset_stats()

        screen_w = self.width if self.width > 50 else 420
        self.player.x = screen_w / 2.0 - self.player.width / 2.0
        self.player.y = 80.0

        self.laser_beam.opacity = 0.0
        self.laser_beam.height = 0.0

        # Встановлюємо стартовий космічний фон
        self.bg.set_biome("space", trigger_warp=False)

        # Оновлення інтерфейсу HUD
        cfg = get_ship_config(equipped_ship_id)
        self.ship_name_label.text = f"⚡ {cfg.name.split()[0].upper()}"
        self._update_hud()
        self._hide_boss_hud()
        if hasattr(self, "boss_warning_box"):
            self.boss_warning_box.opacity = 0.0

        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        if self.upgrade_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.upgrade_overlay)
        self.upgrade_overlay.opacity = 0.0
        self.upgrade_overlay.disabled = True

        # Запуск біомної музики для 'space'
        get_audio_manager().play_biome_music("space")

        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
        self.game_clock_event = Clock.schedule_interval(self.update, FRAME_INTERVAL)

    def _clear_all_entities(self):
        """Очищує всі активні сутності з поля бою."""
        if self.boss is not None:
            self.game_area.remove_widget(self.boss)
            self.boss = None
        self._hide_boss_hud()
        if hasattr(self, "boss_warning_box"):
            self.boss_warning_box.opacity = 0.0
            self.boss_warning_active = False

        for enemy in self.enemies:
            self.game_area.remove_widget(enemy)
        self.enemies.clear()

        for bullet in self.bullets:
            self.game_area.remove_widget(bullet)
        self.bullets.clear()

        for ft in self.floating_texts:
            self.game_area.remove_widget(ft)
        self.floating_texts.clear()

        for obs in self.obstacles:
            self.game_area.remove_widget(obs)
        self.obstacles.clear()
        self.abilities.reset()

        self.particles.clear()
        self.effects_widget.canvas.clear()
        self.laser_beam.opacity = 0.0

    def toggle_pause(self, *args):
        if self.is_paused:
            self.resume_game()
        else:
            self.pause_game()

    def pause_game(self, *args):
        if not self.is_playing or self.is_paused or self.is_upgrading:
            return
        self.is_paused = True

        get_audio_manager().pause_music()

        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

        if self.pause_overlay not in self.root_layout.children:
            self.root_layout.add_widget(self.pause_overlay)
        self.pause_overlay.opacity = 1.0
        self.pause_overlay.disabled = False

    def resume_game(self, *args):
        if not self.is_playing or not self.is_paused:
            return
        self.is_paused = False

        get_audio_manager().resume_music()

        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
        self.game_clock_event = Clock.schedule_interval(self.update, FRAME_INTERVAL)

    def _quit_to_menu(self, *args):
        self.is_playing = False
        self.is_paused = False
        self.is_upgrading = False
        get_audio_manager().stop_music()

        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None
        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True
        if self.upgrade_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.upgrade_overlay)
        self.upgrade_overlay.opacity = 0.0
        self.upgrade_overlay.disabled = True
        self._clear_all_entities()
        if self.manager:
            self.manager.current = "menu_screen"

    def _trigger_level_transition(self):
        """Здійснює плавний гіперстрибок на новий рівень без виходу в меню."""
        self.current_level += 1
        new_biome = get_next_random_biome(self.current_biome, self.visited_biomes)
        self.current_biome = new_biome
        self.visited_biomes.append(new_biome)

        # Новий поріг очок для наступного гіперстрибка
        self.next_level_score += 3000 + (self.current_level - 1) * 500

        cfg = get_biome_config(new_biome)

        # 1. Звук гіперстрибка
        get_audio_manager().play("warp", 0.95)

        # 2. Перемикаємо фон з ефектом витягування ліній гіперпростору
        self.bg.set_biome(new_biome, trigger_warp=True)

        # 3. Перемикаємо фонову музику на саундтрек нового біому
        get_audio_manager().play_biome_music(new_biome)

        # 4. Активуємо банер нового рівня
        self.level_banner_active = True
        self.level_banner_timer = 3.8
        self.level_banner_box.opacity = 1.0
        self.level_title_label.text = f"🚀 РІВЕНЬ {self.current_level}: {cfg.name} {cfg.icon}"
        self.level_hazard_label.text = f"⚠️ {cfg.hazard_text}"

        # 5. Спливаючий текст у центрі екрана
        screen_w = max(self.width, 100.0)
        screen_h = max(self.height, 100.0)
        self._spawn_floating_text(
            f"🚀 ГІПЕРСТРИБОК: {cfg.name}!",
            screen_w / 2.0,
            screen_h / 2.0 + 35.0,
            color=cfg.accent_color,
        )

        self._update_hud()

    def update(self, dt: float):
        """Головний ігровий цикл (Game Loop)."""
        if not self.is_playing or self.is_paused or self.is_upgrading:
            return

        screen_w = max(self.width, 100.0)
        screen_h = max(self.height, 100.0)

        # 0.1 Оновлення попередження про наближення боса
        if self.boss_warning_active:
            self.boss_warning_timer -= dt
            pulse = 0.55 + 0.45 * math.sin(self.boss_warning_timer * 14.0)
            self.boss_warning_box.opacity = max(0.0, pulse)
            if self.boss_warning_timer <= 0.0:
                self.boss_warning_active = False
                self.boss_warning_box.opacity = 0.0
                self._spawn_boss(screen_w, screen_h)

        # 0.2 Оновлення банера гіперстрибка на новий рівень
        if self.level_banner_active:
            self.level_banner_timer -= dt
            if self.level_banner_timer <= 0.0:
                self.level_banner_active = False
                self.level_banner_box.opacity = 0.0
            else:
                alpha = min(1.0, self.level_banner_timer / 0.6)
                self.level_banner_box.opacity = max(0.0, alpha)

        # 0.3 Перевірка умови переходу на новий біом/рівень за очками
        if (
            self.score >= self.next_level_score
            and not self.level_banner_active
            and self.boss is None
            and not self.boss_warning_active
        ):
            self._trigger_level_transition()

        # 1. Оновлення рухомого біомного фону
        self.bg.update(dt)

        # 2. Оновлення гравця
        self.player.update(dt, screen_w)

        # 3. Стрільба гравця
        if (self.auto_fire or self.is_shooting) and self.player.can_shoot():
            new_bullets = self.player.shoot_bullets()
            if self.player.attack_type == "beam":
                if self.player.is_beam_active:
                    get_audio_manager().play("beam", 0.75)
            else:
                for bullet in new_bullets:
                    self.bullets.append(bullet)
                    self.game_area.add_widget(bullet)
                if new_bullets:
                    if any(getattr(b, "is_plasma_orb", False) for b in new_bullets):
                        get_audio_manager().play("plasma", 0.9)
                    elif self.player.attack_type == "charge":
                        get_audio_manager().play("charge", 0.45)
                    else:
                        get_audio_manager().play("laser", 0.45)

        # 3.1 Оновлення променя («Геліос»)
        if self.player.attack_type == "beam" and self.player.is_beam_active:
            self.laser_beam.opacity = 1.0
            self.laser_beam.update_beam(
                dt,
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height,
                screen_h,
            )
            beam_dead = set()
            for enemy in self.enemies:
                if check_collision(self.laser_beam, enemy):
                    enemy.take_damage(self.laser_beam.damage)
                    self._create_hit_particles(
                        enemy.x + enemy.width / 2.0,
                        enemy.y + enemy.height / 2.0,
                        color=(0.2, 1.0, 0.8, 1.0),
                    )
                    if enemy.hp <= 0:
                        beam_dead.add(enemy)
                        earned = getattr(enemy, "score_value", 100)
                        self.score += earned
                        add_credits(earned)
                        self._create_explosion(
                            enemy.x + enemy.width / 2.0,
                            enemy.y + enemy.height / 2.0,
                            count=22,
                            color=(0.2, 0.95, 0.85, 1.0),
                        )
                        self._spawn_floating_text(
                            f"+{earned}",
                            enemy.x + enemy.width / 2.0,
                            enemy.y + enemy.height / 2.0,
                            color=(0.2, 1.0, 0.8, 1.0),
                        )
                        get_audio_manager().play("explosion", 0.65)
            for enemy in beam_dead:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.game_area.remove_widget(enemy)

            if self.boss is not None and check_collision(self.laser_beam, self.boss):
                self.boss.take_damage(self.laser_beam.damage)
                self._create_hit_particles(
                    self.boss.x + self.boss.width / 2.0,
                    self.boss.y + 12.0,
                    color=(0.2, 1.0, 0.8, 1.0),
                )
                self._update_boss_hud()
                if self.boss.hp <= 0:
                    self._handle_boss_defeat()

            vaporized = set()
            for b in self.bullets:
                if not b.is_player and check_collision(self.laser_beam, b):
                    vaporized.add(b)
                    self._create_hit_particles(b.x, b.y, color=(0.3, 1.0, 0.9, 1.0))
            for b in vaporized:
                if b in self.bullets:
                    self.bullets.remove(b)
                    self.game_area.remove_widget(b)
        else:
            self.laser_beam.opacity = 0.0

        # 3.2 Оновлення здібностей гравця (пасивні ефекти, кулдауни)
        self.abilities.update(dt, self.player)

        # 3.3 Періодичний спавн перешкод біому (астероїди, міни, уламки)
        self.obstacle_spawn_timer += dt
        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            self.obstacle_spawn_timer = 0.0
            obs = spawn_obstacle(self.current_biome, screen_w, screen_h)
            self.obstacles.append(obs)
            self.game_area.add_widget(obs)

        # 4. Спавн ворогів по таймеру
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            self._spawn_enemy(screen_w, screen_h)

        # 4.1 Перевірка умови появи боса за очками
        if (
            self.boss is None
            and not self.boss_warning_active
            and self.score >= self.next_boss_score
        ):
            self.boss_warning_active = True
            self.boss_warning_timer = 2.4
            self.boss_warning_box.opacity = 1.0
            get_audio_manager().play("warning", 0.9)
            self._spawn_floating_text(
                "⚠️ БОС НАБЛИЖАЄТЬСЯ!",
                screen_w / 2.0,
                screen_h / 2.0,
                color=(1.0, 0.25, 0.25, 1.0),
            )

        # 5. Оновлення ворогів
        player_center = (
            self.player.x + self.player.width / 2.0,
            self.player.y + self.player.height / 2.0,
        )
        surviving_enemies = []
        for enemy in self.enemies:
            enemy_shots = enemy.update(dt, player_pos=player_center)
            if enemy_shots:
                if isinstance(enemy_shots, list):
                    for b in enemy_shots:
                        self.bullets.append(b)
                        self.game_area.add_widget(b)
                else:
                    self.bullets.append(enemy_shots)
                    self.game_area.add_widget(enemy_shots)

            if enemy.is_out_of_bounds():
                self.game_area.remove_widget(enemy)
                continue

            # Колізія: Ворог врізається в гравця
            if check_collision(enemy, self.player):
                self.game_area.remove_widget(enemy)
                absorbed = self.player.take_damage(25)
                if absorbed:
                    get_audio_manager().play("shield", 0.85)
                    self._create_hit_particles(
                        self.player.x + self.player.width / 2,
                        self.player.y + self.player.height / 2,
                        color=(0.2, 0.85, 1.0, 1.0),
                    )
                    self._spawn_floating_text(
                        "ЩИТ! 🛡️",
                        self.player.x + self.player.width / 2.0,
                        self.player.y + self.player.height + 8.0,
                        color=(0.2, 0.85, 1.0, 1.0),
                    )
                else:
                    get_audio_manager().play("hit", 0.85)
                    self._create_hit_particles(
                        self.player.x + self.player.width / 2,
                        self.player.y + self.player.height / 2,
                    )
                    self._spawn_floating_text(
                        "-25 HP",
                        self.player.x + self.player.width / 2.0,
                        self.player.y + self.player.height + 8.0,
                        color=(1.0, 0.25, 0.25, 1.0),
                    )

                # Якщо таран на лавовому рівні — підпалюємо гравця
                if self.current_biome == "lava":
                    self.player.apply_burn(3.0)
                    get_audio_manager().play("burn", 0.85)
                elif self.current_biome == "water":
                    self.player.apply_slow(2.5)
                    get_audio_manager().play("splash", 0.85)

                self._update_hud()
                if self.player.hp <= 0:
                    self._trigger_game_over()
                    return
                continue

            surviving_enemies.append(enemy)
        self.enemies = surviving_enemies

        # 5.15 Оновлення перешкод
        surviving_obstacles = []
        for obs in self.obstacles:
            obs.update(dt, player_x=self.player.x + self.player.width / 2.0, player_y=self.player.y)
            if obs.is_out_of_bounds() or obs.is_destroyed:
                self.game_area.remove_widget(obs)
                continue

            # Колізія перешкоди з гравцем
            if check_collision(obs, self.player):
                if not self.abilities.is_invincible():
                    dmg = obs.contact_damage
                    red = self.abilities.get_armor_reduction()
                    final_dmg = max(1, int(dmg * (1.0 - red)))
                    absorbed = self.player.take_damage(final_dmg)
                    if absorbed:
                        get_audio_manager().play("shield", 0.8)
                        self._spawn_floating_text("ЩИТ! 🛡️", self.player.x + self.player.width / 2, self.player.y + self.player.height + 5, color=(0.3, 0.85, 1.0, 1.0))
                    else:
                        get_audio_manager().play("hit", 0.8)
                        self._spawn_floating_text(f"-{final_dmg} HP", self.player.x + self.player.width / 2, self.player.y + self.player.height + 5, color=(1.0, 0.3, 0.2, 1.0))

                    if obs.hazard_type == "burn":
                        self.player.apply_burn(3.0)
                        get_audio_manager().play("burn", 0.8)
                    elif obs.hazard_type == "freeze":
                        self.player.apply_freeze(2.5)
                        get_audio_manager().play("freeze", 0.8)
                    elif obs.hazard_type == "emp":
                        self.player.apply_emp(2.0)
                        get_audio_manager().play("shock", 0.8)
                    elif obs.hazard_type == "slow":
                        self.player.apply_slow(2.5)
                        get_audio_manager().play("splash", 0.8)

                    self._update_hud()
                    if self.player.hp <= 0:
                        self._trigger_game_over()
                        return

                obs.take_damage(3)
                if obs.is_destroyed:
                    self._create_explosion(obs.x + obs.width / 2, obs.y + obs.height / 2, count=16)
                    self.game_area.remove_widget(obs)
                    continue

            surviving_obstacles.append(obs)
        self.obstacles = surviving_obstacles

        # 5.1 Оновлення флагмана-боса
        if self.boss is not None:
            boss_shots = self.boss.update(
                dt, player_pos=player_center, screen_w=screen_w, screen_h=screen_h
            )
            for b in boss_shots:
                self.bullets.append(b)
                self.game_area.add_widget(b)

            if check_collision(self.boss, self.player):
                absorbed = self.player.take_damage(35)
                if absorbed:
                    get_audio_manager().play("shield", 0.85)
                    self._create_hit_particles(
                        self.player.x + self.player.width / 2,
                        self.player.y + self.player.height / 2,
                        color=(0.2, 0.85, 1.0, 1.0),
                    )
                    self._spawn_floating_text(
                        "ЩИТ! 🛡️",
                        self.player.x + self.player.width / 2.0,
                        self.player.y + self.player.height + 8.0,
                        color=(0.2, 0.85, 1.0, 1.0),
                    )
                else:
                    get_audio_manager().play("hit", 0.85)
                    self._create_hit_particles(
                        self.player.x + self.player.width / 2,
                        self.player.y + self.player.height / 2,
                        color=(1.0, 0.2, 0.2, 1.0),
                    )
                    self._spawn_floating_text(
                        "-35 HP",
                        self.player.x + self.player.width / 2.0,
                        self.player.y + self.player.height + 8.0,
                        color=(1.0, 0.2, 0.2, 1.0),
                    )
                self._update_hud()
                if self.player.hp <= 0:
                    self._trigger_game_over()
                    return

        # 6. Оновлення куль
        alive_bullets = []
        for bullet in self.bullets:
            bullet.update(dt)
            if bullet.is_out_of_bounds(screen_h):
                self.game_area.remove_widget(bullet)
            else:
                alive_bullets.append(bullet)
        self.bullets = alive_bullets

        # 7. Обробка колізій куль
        self._handle_bullet_collisions()

        # 8. Оновлення часточок
        self._update_particles(dt)

        # 8.1 Оновлення спливаючих написів
        alive_ft = []
        for ft in self.floating_texts:
            ft.update(dt)
            if ft.is_dead:
                self.game_area.remove_widget(ft)
            else:
                alive_ft.append(ft)
        self.floating_texts = alive_ft

        # 9. Перевірка смерті гравця (в т.ч. від DoT-підпалу)
        if self.player.hp <= 0:
            self._trigger_game_over()

    def _spawn_enemy(self, screen_w: float, screen_h: float):
        """Створює нового ворога з урахуванням поточного біому та розширених класів."""
        if self.boss is not None or self.boss_warning_active:
            if random.random() > 0.35:
                return

        margin = 18.0
        max_x = max(margin, screen_w - 68.0 - margin)
        spawn_x = random.uniform(margin, max_x)
        spawn_y = screen_h + 16.0

        enemy = spawn_enemy_for_biome(spawn_x, spawn_y, self.current_biome, self.score)
        self.enemies.append(enemy)
        self.game_area.add_widget(enemy)

    def _spawn_boss(self, screen_w: float, screen_h: float):
        self.boss_level += 1
        boss_x = max(12.0, screen_w / 2.0 - 57.0)
        boss_y = screen_h + 30.0

        # Елітний бос на кожному 3-му рівні або починаючи з 4-го рівня
        if self.boss_level >= 4 or (self.boss_level > 1 and self.boss_level % 3 == 0):
            self.boss = EliteBoss(boss_x, boss_y, boss_level=self.boss_level, biome=self.current_biome)
            boss_prefix = "☠️ ЕЛІТНИЙ ФЛАГМАН"
        else:
            self.boss = Boss(boss_x, boss_y, boss_level=self.boss_level, biome=self.current_biome)
            boss_prefix = "☠️ БОС"

        self.game_area.add_widget(self.boss)
        self._show_boss_hud()
        cfg = get_biome_config(self.current_biome)
        self._spawn_floating_text(
            f"{boss_prefix}: {cfg.name} {cfg.icon}!",
            screen_w / 2.0,
            screen_h - 160.0,
            color=cfg.accent_color,
        )

    def _handle_boss_defeat(self):
        """Обробляє знищення боса гравцем (дропи матеріалів та здібностей)."""
        if self.boss is None:
            return
        reward = self.boss.score_value
        self.score += reward
        add_credits(reward)
        cx = self.boss.x + self.boss.width / 2.0
        cy = self.boss.y + self.boss.height / 2.0

        self._create_explosion(cx, cy, count=55, color=(1.0, 0.25, 0.4, 1.0))
        self._create_explosion(cx - 25, cy - 10, count=35, color=(1.0, 0.85, 0.1, 1.0))
        self._create_explosion(cx + 25, cy + 10, count=35, color=(0.7, 0.2, 1.0, 1.0))

        self._spawn_floating_text(
            f"☠️ БОС ЗНИЩЕНИЙ! +{reward}",
            cx,
            cy + 20.0,
            color=(1.0, 0.85, 0.2, 1.0),
        )
        get_audio_manager().play("boss_explosion", 1.0)

        # === Дроп матеріалів ===
        is_elite = self.boss_level >= 5
        dropped_mats = roll_drops(self.current_biome, is_boss=True, is_elite=is_elite)
        if dropped_mats:
            from game.storage import add_material
            from game.materials import get_material
            mat_names = []
            for mat_id in dropped_mats:
                add_material(mat_id, 1)
                try:
                    mat = get_material(mat_id)
                    mat_names.append(f"{mat.icon} {mat.name}")
                except Exception:
                    mat_names.append(mat_id)
            drop_text = "📦 ДРОП: " + ", ".join(mat_names[:3])
            self._spawn_floating_text(drop_text, cx, cy + 60.0, color=(0.85, 0.55, 1.0, 1.0))
            self.drop_notification_text = drop_text
            self.drop_notification_timer = 4.0

        # === Дроп здібностей (малий шанс) ===
        passive_drop = roll_passive_drop(self.current_biome)
        if passive_drop and self.abilities.add_passive(passive_drop):
            from game.abilities import get_passive_config
            try:
                ab = get_passive_config(passive_drop)
                self._spawn_floating_text(
                    f"⭐ ПАСИВКА: {ab.icon} {ab.name}",
                    cx, cy + 90.0, color=(1.0, 0.9, 0.3, 1.0)
                )
            except Exception:
                pass

        active_drop = roll_active_drop(self.current_biome)
        if active_drop and self.abilities.add_active(active_drop):
            from game.abilities import get_active_config
            try:
                ab = get_active_config(active_drop)
                self._spawn_floating_text(
                    f"🔮 ЗДІБНІСТЬ: {ab.icon} {ab.name}",
                    cx, cy + 115.0, color=(0.5, 0.95, 1.0, 1.0)
                )
            except Exception:
                pass

        self.game_area.remove_widget(self.boss)
        self.boss = None
        self._hide_boss_hud()
        self.next_boss_score = self.score + 2500 + self.boss_level * 1200

    def _handle_bullet_collisions(self):
        """Перевіряє зіткнення куль із ворогами та гравцем (з накладанням ефектів біомів)."""
        bullets_to_remove = set()
        enemies_to_remove = set()

        for bullet in self.bullets:
            if bullet in bullets_to_remove:
                continue

            # 1. Снаряд гравця -> Бос
            if bullet.is_player and self.boss is not None:
                if check_collision(bullet, self.boss):
                    bullets_to_remove.add(bullet)
                    self.boss.take_damage(bullet.damage)
                    self._create_hit_particles(
                        bullet.x, bullet.y, color=(1.0, 0.4, 0.8, 1.0)
                    )
                    self._update_boss_hud()
                    if self.boss.hp <= 0:
                        self._handle_boss_defeat()
                    continue

            # 1.1 Снаряд гравця -> Перешкоди
            if bullet.is_player and self.obstacles:
                hit_obs = False
                for obs in self.obstacles:
                    if obs.is_destroyed:
                        continue
                    if check_collision(bullet, obs):
                        bullets_to_remove.add(bullet)
                        obs.take_damage(bullet.damage)
                        self._create_hit_particles(bullet.x, bullet.y, color=(0.8, 0.8, 0.9, 1.0))
                        if obs.is_destroyed:
                            self._create_explosion(obs.x + obs.width / 2.0, obs.y + obs.height / 2.0, count=16)
                            self.score += 50
                            add_credits(50)
                            self._spawn_floating_text("+50", obs.x + obs.width / 2.0, obs.y + obs.height / 2.0, color=(0.7, 0.9, 1.0, 1.0))
                            get_audio_manager().play("hit", 0.7)
                        hit_obs = True
                        break
                if hit_obs:
                    continue

            if bullet.is_player:
                # 2. Снаряд гравця -> Звичайний ворог
                for enemy in self.enemies:
                    if enemy in enemies_to_remove:
                        continue

                    if check_collision(bullet, enemy):
                        bullets_to_remove.add(bullet)
                        dmg = int(bullet.damage * self.abilities.get_damage_multiplier())
                        enemy.take_damage(dmg)

                        # Якщо це зарядна плазмова сфера — викликаємо ударну хвилю (AoE)
                        if getattr(bullet, "is_plasma_orb", False):
                            cx = bullet.x + bullet.width / 2.0
                            cy = bullet.y + bullet.height / 2.0
                            self._create_explosion(
                                cx, cy, count=36, color=(1.0, 0.65, 0.15, 1.0)
                            )
                            get_audio_manager().play("explosion", 0.85)

                            splash_r = 90.0
                            splash_dmg = 80
                            for other in self.enemies:
                                if other is enemy or other in enemies_to_remove:
                                    continue
                                dist = math.hypot(
                                    (other.x + other.width / 2.0) - cx,
                                    (other.y + other.height / 2.0) - cy,
                                )
                                if dist <= splash_r:
                                    other.take_damage(splash_dmg)
                                    self._create_hit_particles(
                                        other.x + other.width / 2.0,
                                        other.y + other.height / 2.0,
                                        color=(1.0, 0.7, 0.2, 1.0),
                                    )
                                    if other.hp <= 0:
                                        enemies_to_remove.add(other)
                                        pts = getattr(other, "score_value", 100)
                                        self.score += pts
                                        add_credits(pts)
                                        self._spawn_floating_text(
                                            f"💥+{pts}",
                                            other.x + other.width / 2.0,
                                            other.y + other.height / 2.0,
                                            color=(1.0, 0.65, 0.2, 1.0),
                                        )

                        if enemy.hp <= 0:
                            enemies_to_remove.add(enemy)
                            earned = getattr(enemy, "score_value", 100)
                            self.score += earned
                            add_credits(earned)

                            # Якщо це splitter — породжує 2 маленьких дрони
                            if hasattr(enemy, "get_split_children"):
                                for child in enemy.get_split_children():
                                    self.enemies.append(child)
                                    self.game_area.add_widget(child)

                            # Шанс випадання зоряного пилу
                            if random.random() < 0.22:
                                from game.storage import add_material
                                add_material("stellar_dust", 1)

                            etype = getattr(enemy, "enemy_type", "fighter")
                            p_count = 32 if etype in ("cruiser", "bomber", "titan") else 20
                            p_color = (
                                (1.0, 0.45, 0.1, 1.0)
                                if etype == "fighter"
                                else (
                                    (1.0, 0.85, 0.2, 1.0)
                                    if etype in ("scout", "drone")
                                    else (
                                        (1.0, 0.2, 0.4, 1.0)
                                        if etype in ("sniper", "kamikaze")
                                        else (
                                            (1.0, 0.55, 0.1, 1.0)
                                            if etype == "bomber"
                                            else (0.85, 0.2, 0.7, 1.0)
                                        )
                                    )
                                )
                            )
                            self._create_explosion(
                                enemy.x + enemy.width / 2.0,
                                enemy.y + enemy.height / 2.0,
                                count=p_count,
                                color=p_color,
                            )
                            self._spawn_floating_text(
                                f"+{earned}",
                                enemy.x + enemy.width / 2.0,
                                enemy.y + enemy.height / 2.0,
                                color=(0.25, 1.0, 0.45, 1.0),
                            )
                            get_audio_manager().play("explosion", 0.7)
                        else:
                            self._create_hit_particles(
                                bullet.x, bullet.y, color=(1.0, 0.8, 0.2, 1.0)
                            )
                        break
            else:
                # 3. Куля ворога -> Гравець
                if check_collision(bullet, self.player):
                    bullets_to_remove.add(bullet)

                    # Перевірка невразливості
                    if self.abilities.is_invincible():
                        self._create_hit_particles(bullet.x, bullet.y, color=(0.4, 0.8, 1.0, 1.0))
                        continue

                    # Перевірка Щита Пустоти (блокує смертельний удар)
                    raw_dmg = bullet.damage
                    if self.player.hp - raw_dmg <= 0 and self.abilities.check_void_shield_proc():
                        get_audio_manager().play("shield", 1.0)
                        self._spawn_floating_text(
                            "🌌 ЩИТ ПУСТОТИ!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 12.0,
                            color=(0.7, 0.2, 1.0, 1.0)
                        )
                        continue

                    # Зменшення шкоди від пасивної наноброні
                    red = self.abilities.get_armor_reduction()
                    final_dmg = max(1, int(raw_dmg * (1.0 - red)))
                    absorbed = self.player.take_damage(final_dmg)
                    hazard = getattr(bullet, "hazard_type", "none")

                    if absorbed:
                        get_audio_manager().play("shield", 0.85)
                        self._create_hit_particles(
                            bullet.x, bullet.y, color=(0.2, 0.85, 1.0, 1.0)
                        )
                        self._spawn_floating_text(
                            "ЩИТ! 🛡️",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 8.0,
                            color=(0.2, 0.85, 1.0, 1.0),
                        )
                    else:
                        get_audio_manager().play("hit", 0.85)
                        self._create_hit_particles(
                            bullet.x, bullet.y, color=(1.0, 0.2, 0.2, 1.0)
                        )
                        self._spawn_floating_text(
                            f"-{final_dmg} HP",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 8.0,
                            color=(1.0, 0.25, 0.25, 1.0),
                        )

                    # Аномальні ефекти біомів при влучанні
                    if hazard == "burn":
                        self.player.apply_burn(3.0)
                        get_audio_manager().play("burn", 0.85)
                        self._spawn_floating_text(
                            "🔥 ПІДПАЛ!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(1.0, 0.45, 0.1, 1.0),
                        )
                    elif hazard == "slow":
                        self.player.apply_slow(2.5)
                        get_audio_manager().play("splash", 0.85)
                        self._spawn_floating_text(
                            "🌊 СПОВІЛЬНЕННЯ!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.15, 0.9, 0.95, 1.0),
                        )
                    elif hazard == "emp":
                        self.player.apply_emp(1.8)
                        get_audio_manager().play("shock", 0.85)
                        self._spawn_floating_text(
                            "⚡ ШОК!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.85, 0.25, 1.0, 1.0),
                        )
                    elif hazard == "freeze":
                        self.player.apply_freeze(2.0)
                        get_audio_manager().play("freeze", 0.85)
                        self._spawn_floating_text(
                            "❄️ ЗАМОРОЗКА!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.5, 0.9, 1.0, 1.0),
                        )
                    elif hazard == "toxin":
                        self.player.apply_burn(2.5)
                        self._spawn_floating_text(
                            "☠️ ТОКСИН!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.3, 1.0, 0.1, 1.0),
                        )
                    elif hazard == "gravity":
                        self.player.apply_slow(2.0)
                        self._spawn_floating_text(
                            "🌀 ГРАВІТАЦІЯ!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.7, 0.4, 1.0, 1.0),
                        )
                    elif hazard == "dark":
                        self.player.apply_emp(1.5)
                        self._spawn_floating_text(
                            "🕳️ ТЬМА!",
                            self.player.x + self.player.width / 2.0,
                            self.player.y + self.player.height + 26.0,
                            color=(0.6, 0.2, 0.9, 1.0),
                        )

                    self._update_hud()
                    if self.player.hp <= 0:
                        break

        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
                self.game_area.remove_widget(bullet)

        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
                self.game_area.remove_widget(enemy)

        self._update_hud()

        if (
            self.is_playing
            and not self.is_paused
            and not self.is_upgrading
            and self.player.hp > 0
        ):
            if self.score >= self.next_upgrade_score:
                self.upgrade_level += 1
                next_cost = (
                    self.upgrade_base_cost
                    + self.upgrade_level * self.upgrade_cost_step
                )
                self.next_upgrade_score += next_cost
                self._show_upgrade_modal()

    def _show_upgrade_modal(self):
        if not self.is_playing:
            return
        self.is_upgrading = True
        get_audio_manager().play("upgrade", 0.9)

        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

        upgrades = get_random_upgrades(self.player, count=3)
        next_cost = (
            self.upgrade_base_cost
            + self.upgrade_level * self.upgrade_cost_step
        )

        self.upgrade_overlay.show_cards(
            upgrades=upgrades,
            score=self.score,
            on_select=self._on_upgrade_selected,
            upgrade_level=self.upgrade_level,
            next_cost=next_cost,
        )
        if self.upgrade_overlay not in self.root_layout.children:
            self.root_layout.add_widget(self.upgrade_overlay)
        self.upgrade_overlay.opacity = 1.0
        self.upgrade_overlay.disabled = False

    def _on_upgrade_selected(self, upgrade):
        upgrade.apply(self.player)
        self._update_hud()

        self._create_explosion(
            self.player.x + self.player.width / 2.0,
            self.player.y + self.player.height / 2.0,
            count=32,
            color=upgrade.color,
        )

        self._spawn_floating_text(
            f"⭐ {upgrade.title}!",
            self.player.x + self.player.width / 2.0,
            self.player.y + self.player.height + 25.0,
            color=upgrade.color,
        )

        if self.upgrade_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.upgrade_overlay)
        self.upgrade_overlay.opacity = 0.0
        self.upgrade_overlay.disabled = True
        self.is_upgrading = False

        if self.score >= self.next_upgrade_score:
            self.upgrade_level += 1
            next_cost = (
                self.upgrade_base_cost
                + self.upgrade_level * self.upgrade_cost_step
            )
            self.next_upgrade_score += next_cost
            Clock.schedule_once(lambda dt: self._show_upgrade_modal(), 0.15)
            return

        if self.is_playing and not self.is_paused:
            if self.game_clock_event:
                Clock.unschedule(self.game_clock_event)
            self.game_clock_event = Clock.schedule_interval(self.update, FRAME_INTERVAL)

    def _create_explosion(self, x: float, y: float, count: int = 20, color: tuple = (1.0, 0.5, 0.1, 1.0)):
        new_particles = create_explosion(x, y, count=count, base_color=color)
        self.particles.extend(new_particles)

    def _create_hit_particles(self, x: float, y: float, color: tuple = (1.0, 0.8, 0.3, 1.0)):
        new_particles = create_explosion(x, y, count=8, base_color=color)
        self.particles.extend(new_particles)

    def _update_particles(self, dt: float):
        alive = []
        for p in self.particles:
            p.update(dt)
            if not p.is_dead:
                alive.append(p)
        self.particles = alive

        self.effects_widget.canvas.clear()
        if self.particles:
            with self.effects_widget.canvas:
                for p in self.particles:
                    alpha = p.color[3] * (1.0 - p.life / p.max_life)
                    Color(p.color[0], p.color[1], p.color[2], alpha)
                    Ellipse(
                        pos=(p.x - p.size / 2.0, p.y - p.size / 2.0),
                        size=(p.size, p.size),
                    )

    def _update_hud(self):
        """Оновлює показники HP, активного щита, балансу кредитів, статусу та біому."""
        hp = max(0, self.player.hp)
        shield_str = f" [🛡️{self.player.shield}]" if self.player.shield > 0 else ""
        status_str = ""
        if self.player.is_burning:
            status_str = f" [🔥{self.player.burn_timer:.1f}s]"
        elif self.player.is_slowed:
            status_str = " [🌊]"
        elif self.player.is_frozen:
            status_str = " [❄️]"
        elif self.player.is_emp:
            status_str = " [⚡]"

        self.hp_label.text = f"HP: {hp}/{self.player.max_hp}{shield_str}{status_str}"

        ratio = max(0.0, min(1.0, self.player.hp / max(1, self.player.max_hp)))
        if ratio > 0.5:
            self.hp_label.text_color = (0.2, 1.0, 0.4, 1.0)
            if hasattr(self, "hp_fill_color"):
                self.hp_fill_color.rgba = (0.2, 0.95, 0.4, 1.0)
        elif ratio > 0.25:
            self.hp_label.text_color = (1.0, 0.85, 0.2, 1.0)
            if hasattr(self, "hp_fill_color"):
                self.hp_fill_color.rgba = (1.0, 0.85, 0.2, 1.0)
        else:
            self.hp_label.text_color = (1.0, 0.25, 0.25, 1.0)
            if hasattr(self, "hp_fill_color"):
                self.hp_fill_color.rgba = (1.0, 0.25, 0.25, 1.0)

        if hasattr(self, "hp_bar_widget") and hasattr(self, "hp_fill_rect"):
            self.hp_fill_rect.size = (self.hp_bar_widget.width * ratio, self.hp_bar_widget.height)

        self.score_label.text = f"SCORE: {self.score}"
        self.credits_label.text = f"🪙 {get_credits()}"

        cfg = get_biome_config(self.current_biome)
        if hasattr(self, "level_badge_label"):
            self.level_badge_label.text = f"{cfg.icon} РІВЕНЬ {self.current_level}"

    def _update_hp_bar_canvas(self, *args):
        if hasattr(self, "hp_track_rect") and hasattr(self, "hp_bar_widget"):
            self.hp_track_rect.pos = self.hp_bar_widget.pos
            self.hp_track_rect.size = self.hp_bar_widget.size
            ratio = max(0.0, min(1.0, self.player.hp / max(1, self.player.max_hp)))
            self.hp_fill_rect.pos = self.hp_bar_widget.pos
            self.hp_fill_rect.size = (self.hp_bar_widget.width * ratio, self.hp_bar_widget.height)

    def _show_boss_hud(self):
        titles = [
            "ФЛАГМАН ТИТАН",
            "ДРЕДНОУТ ВОРОГА",
            "НЕЙТРОННИЙ РУЙНІВНИК",
            "ГАЛАКТИЧНИЙ ПОЖИРАЧ",
            "АБСОЛЮТНИЙ ЛЕВІАФАН",
        ]
        title_idx = min(len(titles) - 1, max(0, self.boss_level - 1))
        boss_title = titles[title_idx]
        cfg = get_biome_config(self.current_biome)
        self.boss_title_label.text = f"☠️ {boss_title} ({cfg.name})"
        self.boss_bar_box.opacity = 1.0
        self._update_boss_hud()

    def _update_boss_hud(self):
        if self.boss is not None and hasattr(self, "boss_hp_fill"):
            ratio = max(0.0, min(1.0, self.boss.hp / max(1, self.boss.max_hp)))
            self.boss_hp_fill.size = (
                self.boss_hp_widget.width * ratio,
                self.boss_hp_widget.height,
            )

    def _hide_boss_hud(self):
        if hasattr(self, "boss_bar_box"):
            self.boss_bar_box.opacity = 0.0

    def _update_boss_bar_canvas(self, *args):
        if hasattr(self, "boss_bg_rect") and hasattr(self, "boss_bar_box"):
            self.boss_bg_rect.pos = self.boss_bar_box.pos
            self.boss_bg_rect.size = self.boss_bar_box.size
            self.boss_border_line.rounded_rectangle = [
                self.boss_bar_box.x,
                self.boss_bar_box.y,
                self.boss_bar_box.width,
                self.boss_bar_box.height,
                6,
            ]

    def _update_boss_hp_canvas(self, *args):
        if hasattr(self, "boss_hp_track") and hasattr(self, "boss_hp_fill"):
            self.boss_hp_track.pos = self.boss_hp_widget.pos
            self.boss_hp_track.size = self.boss_hp_widget.size
            self.boss_hp_fill.pos = self.boss_hp_widget.pos
            ratio = 1.0
            if self.boss is not None:
                ratio = max(0.0, min(1.0, self.boss.hp / max(1, self.boss.max_hp)))
            self.boss_hp_fill.size = (
                self.boss_hp_widget.width * ratio,
                self.boss_hp_widget.height,
            )

    def _update_warning_canvas(self, *args):
        if hasattr(self, "warning_bg_rect") and hasattr(self, "boss_warning_box"):
            self.warning_bg_rect.pos = self.boss_warning_box.pos
            self.warning_bg_rect.size = self.boss_warning_box.size
            self.warning_border_line.rounded_rectangle = [
                self.boss_warning_box.x,
                self.boss_warning_box.y,
                self.boss_warning_box.width,
                self.boss_warning_box.height,
                10,
            ]

    def _spawn_floating_text(
        self,
        text: str,
        x: float,
        y: float,
        color: tuple = (1.0, 1.0, 0.2, 1.0),
    ):
        ft = FloatingText(text=text, x=x, y=y, color=color)
        self.floating_texts.append(ft)
        self.game_area.add_widget(ft)

    def trigger_active_ability(self, index: int):
        """Активує здібність за індексом у списку зібраних активних здібностей."""
        if not self.is_playing or self.is_paused or self.is_upgrading:
            return
        if index < 0 or index >= len(self.abilities.active_ids):
            return

        ability_id = self.abilities.active_ids[index]
        if not self.abilities.can_use_active(ability_id):
            cd = self.abilities.get_active_cooldown_remaining(ability_id)
            self._spawn_floating_text(
                f"⏳ Кулдаун: {cd:.1f}с",
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height + 15.0,
                color=(0.8, 0.8, 0.8, 0.9),
            )
            return

        self.abilities.use_active(ability_id)
        cx = self.player.x + self.player.width / 2.0
        cy = self.player.y + self.player.height / 2.0

        if ability_id == "emergency_repair":
            heal = int(self.player.max_hp * 0.5)
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            get_audio_manager().play("upgrade", 0.9)
            self._spawn_floating_text(f"🔧 РЕМОНТ +{heal} HP!", cx, cy + 20.0, color=(0.2, 1.0, 0.4, 1.0))

        elif ability_id == "warp_jump":
            screen_w = max(self.width, 100.0)
            self.player.x = random.uniform(20.0, screen_w - self.player.width - 20.0)
            self.abilities.invincible_timer = 1.5
            get_audio_manager().play("warp", 0.85)
            self._spawn_floating_text("🚀 ВАРП-СТРИБОК!", cx, cy + 20.0, color=(0.4, 0.85, 1.0, 1.0))

        elif ability_id == "biome_shift":
            self._trigger_level_transition()
            self._spawn_floating_text("🌀 ЗМІНА БІОМУ!", cx, cy + 20.0, color=(0.6, 1.0, 0.7, 1.0))

        elif ability_id == "time_warp":
            get_audio_manager().play("shock", 0.85)
            self._spawn_floating_text("⏱️ УПОВІЛЬНЕННЯ ЧАСУ!", cx, cy + 20.0, color=(0.85, 0.4, 1.0, 1.0))

        elif ability_id == "nova_burst":
            get_audio_manager().play("explosion", 1.0)
            for e in list(self.enemies):
                e.take_damage(80)
            if self.boss:
                self.boss.take_damage(120)
            self.bullets = [b for b in self.bullets if b.is_player]
            self._create_explosion(cx, cy, count=40, color=(1.0, 0.6, 0.1, 1.0))
            self._spawn_floating_text("💥 СПАЛАХ НОВИ!", cx, cy + 20.0, color=(1.0, 0.5, 0.1, 1.0))

        elif ability_id == "shield_overload":
            self.player.shield += 3
            self.abilities.invincible_timer = 5.0
            get_audio_manager().play("shield", 1.0)
            self._spawn_floating_text("⚡ ПЕРЕВАНТАЖЕННЯ ЩИТА (+3)!", cx, cy + 20.0, color=(0.3, 0.9, 1.0, 1.0))

        elif ability_id == "missile_barrage":
            get_audio_manager().play("laser", 0.9)
            for vx in [-160, -110, -60, -20, 20, 60, 110, 160]:
                mb = Bullet(
                    cx - 4.0, cy + 10.0, is_player=True,
                    damage=60, vx=vx, vy=550.0,
                    color=(1.0, 0.4, 0.2, 1.0), width=9.0, height=18.0
                )
                self.bullets.append(mb)
                self.game_area.add_widget(mb)
            self._spawn_floating_text("🚀 РАКЕТНИЙ ШТОРМ!", cx, cy + 20.0, color=(1.0, 0.35, 0.2, 1.0))

        elif ability_id == "resurrection":
            self.player.hp = self.player.max_hp
            self.abilities.invincible_timer = 3.0
            get_audio_manager().play("upgrade", 1.0)
            self._spawn_floating_text("☀️ ВОСКРЕСІННЯ!", cx, cy + 20.0, color=(1.0, 0.9, 0.2, 1.0))

        self._update_hud()

    def _trigger_game_over(self):
        """Завершує гру та переходить на GameOverScreen (з підтримкою відродження)."""
        # 1. Пасивна здібність: Матриця Фенікса (одноразове відродження)
        if self.abilities.has_passive("phoenix_matrix") and not self.abilities.phoenix_used:
            self.abilities.phoenix_used = True
            self.player.hp = max(30, int(self.player.max_hp * 0.35))
            self.abilities.invincible_timer = 3.0
            get_audio_manager().play("upgrade", 1.0)
            self._create_explosion(
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height / 2.0,
                count=35,
                color=(1.0, 0.5, 0.1, 1.0),
            )
            self._spawn_floating_text(
                "🔥 МАТРИЦЯ ФЕНІКСА: ВІДРОДЖЕННЯ!",
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height + 25.0,
                color=(1.0, 0.7, 0.1, 1.0),
            )
            self._update_hud()
            return

        # 2. Активна здібність: Воскресіння
        if self.abilities.has_active("resurrection") and self.abilities.can_use_active("resurrection"):
            self.abilities.use_active("resurrection")
            self.player.hp = self.player.max_hp
            self.abilities.invincible_timer = 4.0
            get_audio_manager().play("upgrade", 1.0)
            self._create_explosion(
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height / 2.0,
                count=45,
                color=(1.0, 0.9, 0.2, 1.0),
            )
            self._spawn_floating_text(
                "☀️ ВОСКРЕСІННЯ!",
                self.player.x + self.player.width / 2.0,
                self.player.y + self.player.height + 25.0,
                color=(1.0, 0.95, 0.3, 1.0),
            )
            self._update_hud()
            return

        self.is_playing = False
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

        get_audio_manager().stop_music()
        get_audio_manager().play("game_over", 0.95)
        update_high_score(self.score)

        self._create_explosion(
            self.player.x + self.player.width / 2.0,
            self.player.y + self.player.height / 2.0,
            count=45,
            color=(0.2, 0.8, 1.0, 1.0),
        )

        def switch_to_game_over(dt):
            if self.manager:
                game_over_screen = self.manager.get_screen("game_over_screen")
                game_over_screen.set_score(self.score)
                self.manager.current = "game_over_screen"

        Clock.schedule_once(switch_to_game_over, 0.5)

    # --- Сенсорне та мишаче керування (Android & Desktop) ---
    def on_touch_down(self, touch):
        if self.is_upgrading:
            return self.upgrade_overlay.on_touch_down(touch)

        if self.is_paused:
            if hasattr(self, "resume_btn") and self.resume_btn.collide_point(*touch.pos):
                self.resume_game()
                return True
            if hasattr(self, "pause_sound_btn") and self.pause_sound_btn.collide_point(*touch.pos):
                self._toggle_sound_pause()
                return True
            if hasattr(self, "pause_music_btn") and self.pause_music_btn.collide_point(*touch.pos):
                self._toggle_music_pause()
                return True
            if hasattr(self, "menu_btn") and self.menu_btn.collide_point(*touch.pos):
                self._quit_to_menu()
                return True
            return super().on_touch_down(touch)

        is_pause_corner = touch.x >= (self.width - 80) and touch.y >= (self.height - 65)
        if self.pause_btn.collide_point(*touch.pos) or is_pause_corner:
            self.toggle_pause()
            return True

        if self.hud_box.collide_point(*touch.pos):
            return self.hud_box.on_touch_down(touch)

        if hasattr(self, "controls_box") and self.controls_box.collide_point(*touch.pos):
            return self.controls_box.on_touch_down(touch)

        if self.is_playing:
            self.player.move_to_x(touch.x, self.width)
            touch.grab(self)
            return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.is_upgrading:
            return True
        if touch.grab_current is self and self.is_playing and not self.is_paused:
            self.player.move_to_x(touch.x, self.width)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    # --- Клавіатурне керування (Desktop) ---
    def on_pre_enter(self, *args):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def on_pre_leave(self, *args):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if self.is_upgrading:
            if key in (49, 50, 51):
                self.upgrade_overlay.select_by_index(key - 49)
            return False

        if not self.is_playing or self.is_paused:
            if key == 112:
                self.toggle_pause()
            return False

        if key in (276, 97):  # Left / 'a'
            self.keys_pressed.add("left")
            self.player.set_move_direction(-1)
        elif key in (275, 100):  # Right / 'd'
            self.keys_pressed.add("right")
            self.player.set_move_direction(1)
        elif key == 32:  # Space
            self.is_shooting = True
        elif key == 112:  # 'p'
            self.toggle_pause()
        elif key in (49, 113):  # '1' or 'q'
            self.trigger_active_ability(0)
        elif key in (50, 101):  # '2' or 'e'
            self.trigger_active_ability(1)
        elif key in (51, 114):  # '3' or 'r'
            self.trigger_active_ability(2)
        return False

    def _on_key_up(self, window, key, scancode):
        if key in (276, 97):
            self.keys_pressed.discard("left")
        elif key in (275, 100):
            self.keys_pressed.discard("right")
        elif key == 32:
            self.is_shooting = False

        if "left" in self.keys_pressed:
            self.player.set_move_direction(-1)
        elif "right" in self.keys_pressed:
            self.player.set_move_direction(1)
        else:
            self.player.set_move_direction(0)
        return False
