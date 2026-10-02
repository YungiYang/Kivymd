"""Ігровий екран із повним ігровим циклом, колізіями, HUD та паузою."""

import random
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Ellipse
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton

from game.constants import (
    FRAME_INTERVAL,
    PLAYER_MAX_HP,
    ENEMY_SPAWN_INTERVAL,
    COLOR_BG_SPACE,
)
from game.background import ParallaxBackground
from game.entities import (
    PlayerShip,
    Enemy,
    Bullet,
    Particle,
    check_collision,
    create_explosion,
)


class GameScreen(MDScreen):
    """Головний ігровий екран із 60 FPS циклом."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "game_screen"

        # Стан гри
        self.is_playing = False
        self.is_paused = False
        self.score = 0
        self.spawn_timer = 0.0
        self.game_clock_event = None

        # Керування
        self.auto_fire = True
        self.is_shooting = False
        self.keys_pressed = set()

        # Списки ігрових сутностей
        self.enemies: list[Enemy] = []
        self.bullets: list[Bullet] = []
        self.particles: list[Particle] = []

        self._build_ui()

    def _build_ui(self):
        """Створює структуру інтерфейсу гри."""
        self.root_layout = FloatLayout(size_hint=(1, 1))

        # 1. Двошаровий рухомий фон
        self.bg = ParallaxBackground(size_hint=(1, 1))
        self.root_layout.add_widget(self.bg)

        # 2. Шар ігрового простору (де малюються кораблі та частинки)
        self.game_area = Widget(size_hint=(1, 1))
        self.root_layout.add_widget(self.game_area)

        # 3. Шар часточок вибухів (власний Canvas)
        self.effects_widget = Widget(size_hint=(1, 1))
        self.root_layout.add_widget(self.effects_widget)

        # 4. Корабель гравця
        self.player = PlayerShip()
        self.game_area.add_widget(self.player)

        # 5. Верхня панель (HUD)
        self._build_hud()

        # 6. Нижні екранні кнопки керування для Android
        self._build_controls()

        # 7. Оверлей паузи
        self._build_pause_overlay()

        self.add_widget(self.root_layout)

    def _build_hud(self):
        """Створює верхню панель з HP, рахунком та кнопкою паузи."""
        self.hud_box = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=56,
            pos_hint={"top": 1.0, "x": 0.0},
            padding=[14, 8, 14, 8],
            spacing=10,
        )

        # Фон панелі HUD
        with self.hud_box.canvas.before:
            Color(0.05, 0.08, 0.16, 0.75)
            self.hud_bg = Rectangle(pos=self.hud_box.pos, size=self.hud_box.size)
        self.hud_box.bind(
            pos=lambda *args: setattr(self.hud_bg, "pos", self.hud_box.pos),
            size=lambda *args: setattr(self.hud_bg, "size", self.hud_box.size),
        )

        # Індикатор HP
        self.hp_label = MDLabel(
            text=f"HP: {PLAYER_MAX_HP}",
            theme_text_color="Custom",
            text_color=(0.2, 1.0, 0.4, 1.0),
            font_style="Title",
            role="medium",
            bold=True,
            size_hint=(0.35, 1),
        )
        self.hud_box.add_widget(self.hp_label)

        # Рахунок
        self.score_label = MDLabel(
            text="SCORE: 0",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.85, 1.0, 1.0),
            font_style="Title",
            role="medium",
            bold=True,
            size_hint=(0.45, 1),
        )
        self.hud_box.add_widget(self.score_label)

        # Кнопка паузи (чітка та зручна для натискання пальцем або мишкою)
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
            size=(58, 42),
            pos_hint={"center_y": 0.5},
            theme_bg_color="Custom",
            md_bg_color=(0.20, 0.35, 0.55, 0.95),
        )
        self.pause_btn.bind(on_release=self.toggle_pause)
        self.hud_box.add_widget(self.pause_btn)

        self.root_layout.add_widget(self.hud_box)

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

        # Кнопка «Вліво»
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

        # Кнопка «Вогонь»
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

        # Кнопка «Вправо»
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
        """Створює напівпрозорий екран паузи."""
        self.pause_overlay = FloatLayout(
            size_hint=(1, 1),
            pos_hint={"x": 0.0, "y": 0.0},
        )
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        # Темний фон затемнення
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
            size_hint=(0.82, None),
            height=280,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[24, 24, 24, 24],
            spacing=18,
        )
        with menu_card.canvas.before:
            Color(0.1, 0.15, 0.28, 0.95)
            self.card_bg = Rectangle(pos=menu_card.pos, size=menu_card.size)
        menu_card.bind(
            pos=lambda *args: setattr(self.card_bg, "pos", menu_card.pos),
            size=lambda *args: setattr(self.card_bg, "size", menu_card.size),
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
            height=40,
        )
        menu_card.add_widget(pause_title)

        # Кнопка «Продовжити»
        self.resume_btn = MDButton(
            MDButtonText(text="ПРОДОВЖИТИ", font_style="Title", role="medium"),
            style="filled",
            size_hint=(1, None),
            height=50,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.7, 0.45, 1.0),
        )
        self.resume_btn.bind(on_release=self.resume_game)
        menu_card.add_widget(self.resume_btn)

        # Кнопка «Головне меню»
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
            height=46,
        )
        self.menu_btn.bind(on_release=self._quit_to_menu)
        menu_card.add_widget(self.menu_btn)

        self.pause_overlay.add_widget(menu_card)

    def _set_shooting(self, active: bool):
        self.is_shooting = active

    def start_new_game(self):
        """Ініціалізує нову ігрову партію та запускає ігровий цикл."""
        # Очищення попереднього стану
        self._clear_all_entities()

        self.score = 0
        self.spawn_timer = 0.0
        self.is_paused = False
        self.is_playing = True
        self.is_shooting = False

        # Позиціювання гравця знизу по центру над кнопками керування
        screen_w = self.width if self.width > 50 else 420
        self.player.x = screen_w / 2.0 - self.player.width / 2.0
        self.player.y = 80.0
        self.player.hp = PLAYER_MAX_HP
        self.player.time_since_last_shot = self.player.fire_cooldown
        self.player.set_move_direction(0)
        self.player.engine_particles.clear()
        self.player.redraw()

        # Оновлення інтерфейсу HUD
        self._update_hud()

        # Приховування оверлею паузи
        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        # Запуск ігрового циклу з фіксованим FPS
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
        self.game_clock_event = Clock.schedule_interval(self.update, FRAME_INTERVAL)

    def _clear_all_entities(self):
        """Очищує всі активні кулі, ворогів та ефекти з поля бою."""
        for enemy in self.enemies:
            self.game_area.remove_widget(enemy)
        self.enemies.clear()

        for bullet in self.bullets:
            self.game_area.remove_widget(bullet)
        self.bullets.clear()

        self.particles.clear()
        self.effects_widget.canvas.clear()

    def toggle_pause(self, *args):
        """Перемикач паузи."""
        if self.is_paused:
            self.resume_game()
        else:
            self.pause_game()

    def pause_game(self, *args):
        """Зупиняє ігровий цикл та показує оверлей паузи."""
        if not self.is_playing or self.is_paused:
            return
        self.is_paused = True

        # Зупинка таймера ігрового циклу (Clock)
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

        # Відображення вікна паузи
        if self.pause_overlay not in self.root_layout.children:
            self.root_layout.add_widget(self.pause_overlay)
        self.pause_overlay.opacity = 1.0
        self.pause_overlay.disabled = False

    def resume_game(self, *args):
        """Відновлює гру та перезапускає ігровий цикл."""
        if not self.is_playing or not self.is_paused:
            return
        self.is_paused = False

        # Приховування та видалення вікна паузи
        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True

        # Перезапуск ігрового циклу
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
        self.game_clock_event = Clock.schedule_interval(self.update, FRAME_INTERVAL)

    def _quit_to_menu(self, *args):
        """Зупиняє гру та повертає користувача в меню."""
        self.is_playing = False
        self.is_paused = False
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None
        if self.pause_overlay in self.root_layout.children:
            self.root_layout.remove_widget(self.pause_overlay)
        self.pause_overlay.opacity = 0.0
        self.pause_overlay.disabled = True
        self._clear_all_entities()
        if self.manager:
            self.manager.current = "menu_screen"

    def update(self, dt: float):
        """Головний ігровий цикл (Game Loop)."""
        if not self.is_playing or self.is_paused:
            return

        screen_w = max(self.width, 100.0)
        screen_h = max(self.height, 100.0)

        # 1. Оновлення рухомого двошарового фону
        self.bg.update(dt)

        # 2. Оновлення гравця та анімації часточок двигуна
        self.player.update(dt, screen_w)

        # 3. Стрільба гравця (автоматична або за кнопкою з обмеженням швидкості)
        if (self.auto_fire or self.is_shooting) and self.player.can_shoot():
            bullet = self.player.shoot()
            self.bullets.append(bullet)
            self.game_area.add_widget(bullet)

        # 4. Спавн нових ворогів по таймеру
        self.spawn_timer += dt
        if self.spawn_timer >= ENEMY_SPAWN_INTERVAL:
            self.spawn_timer = 0.0
            self._spawn_enemy(screen_w, screen_h)

        # 5. Оновлення ворогів (рух та стрільба)
        surviving_enemies = []
        for enemy in self.enemies:
            enemy_bullet = enemy.update(dt)
            if enemy_bullet:
                self.bullets.append(enemy_bullet)
                self.game_area.add_widget(enemy_bullet)

            # Перевірка виходу ворога за нижню межу екрана
            if enemy.is_out_of_bounds():
                self.game_area.remove_widget(enemy)
                continue

            # Колізія: Ворог врізається в гравця
            if check_collision(enemy, self.player):
                self.game_area.remove_widget(enemy)
                self.player.take_damage(25)
                self._create_hit_particles(self.player.x + self.player.width / 2, self.player.y + self.player.height / 2)
                self._update_hud()
                if self.player.hp <= 0:
                    self._trigger_game_over()
                    return
                continue

            surviving_enemies.append(enemy)
        self.enemies = surviving_enemies

        # 6. Оновлення куль (рух, вихід за екран)
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

        # 8. Оновлення часточок вибухів
        self._update_particles(dt)

        # 9. Перевірка смерті гравця
        if self.player.hp <= 0:
            self._trigger_game_over()

    def _spawn_enemy(self, screen_w: float, screen_h: float):
        """Створює нового ворога на випадковій горизонтальній позиції вгорі."""
        margin = 15.0
        max_x = max(margin, screen_w - 48.0 - margin)
        spawn_x = random.uniform(margin, max_x)
        spawn_y = screen_h + 10.0

        enemy = Enemy(spawn_x, spawn_y)
        self.enemies.append(enemy)
        self.game_area.add_widget(enemy)

    def _handle_bullet_collisions(self):
        """Перевіряє зіткнення куль із ворогами та гравцем."""
        bullets_to_remove = set()
        enemies_to_remove = set()

        for bullet in self.bullets:
            if bullet in bullets_to_remove:
                continue

            if bullet.is_player:
                # Куля гравця -> Ворог
                for enemy in self.enemies:
                    if enemy in enemies_to_remove:
                        continue

                    if check_collision(bullet, enemy):
                        bullets_to_remove.add(bullet)
                        enemy.take_damage(bullet.damage)

                        if enemy.hp <= 0:
                            enemies_to_remove.add(enemy)
                            self.score += 100
                            self._create_explosion(
                                enemy.x + enemy.width / 2.0,
                                enemy.y + enemy.height / 2.0,
                                count=22,
                                color=(1.0, 0.45, 0.1, 1.0),
                            )
                        else:
                            self._create_hit_particles(
                                bullet.x, bullet.y, color=(1.0, 0.8, 0.2, 1.0)
                            )
                        break
            else:
                # Куля ворога -> Гравець
                if check_collision(bullet, self.player):
                    bullets_to_remove.add(bullet)
                    self.player.take_damage(bullet.damage)
                    self._create_hit_particles(
                        bullet.x, bullet.y, color=(1.0, 0.2, 0.2, 1.0)
                    )
                    self._update_hud()
                    if self.player.hp <= 0:
                        break

        # Видалення знищених куль
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
                self.game_area.remove_widget(bullet)

        # Видалення знищених ворогів
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
                self.game_area.remove_widget(enemy)

        self._update_hud()

    def _create_explosion(self, x: float, y: float, count: int = 20, color: tuple = (1.0, 0.5, 0.1, 1.0)):
        """Створює ефект вибуху."""
        new_particles = create_explosion(x, y, count=count, base_color=color)
        self.particles.extend(new_particles)

    def _create_hit_particles(self, x: float, y: float, color: tuple = (1.0, 0.8, 0.3, 1.0)):
        """Створює невеликий спалах часточок при влучанні."""
        new_particles = create_explosion(x, y, count=8, base_color=color)
        self.particles.extend(new_particles)

    def _update_particles(self, dt: float):
        """Оновлює та перемальовує всі часточки вибухів на екрані."""
        alive = []
        for p in self.particles:
            p.update(dt)
            if not p.is_dead:
                alive.append(p)
        self.particles = alive

        # Малювання часточок
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
        """Оновлює показники HP та рахунку."""
        hp = max(0, self.player.hp)
        self.hp_label.text = f"HP: {hp}"
        if hp > 50:
            self.hp_label.text_color = (0.2, 1.0, 0.4, 1.0)
        elif hp > 25:
            self.hp_label.text_color = (1.0, 0.85, 0.2, 1.0)
        else:
            self.hp_label.text_color = (1.0, 0.25, 0.25, 1.0)

        self.score_label.text = f"SCORE: {self.score}"

    def _trigger_game_over(self):
        """Завершує гру та переходить на GameOverScreen."""
        self.is_playing = False
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

        # Створюємо великий фінальний вибух корабля гравця
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
        # 1. Якщо гра на паузі — обробляємо кнопки оверлею паузи
        if self.is_paused:
            if hasattr(self, "resume_btn") and self.resume_btn.collide_point(*touch.pos):
                self.resume_game()
                return True
            if hasattr(self, "menu_btn") and self.menu_btn.collide_point(*touch.pos):
                self._quit_to_menu()
                return True
            return super().on_touch_down(touch)

        # 2. Кнопка паузи (натискання на саму кнопку або у верхньому правому кутку HUD)
        is_pause_corner = touch.x >= (self.width - 80) and touch.y >= (self.height - 65)
        if self.pause_btn.collide_point(*touch.pos) or is_pause_corner:
            self.toggle_pause()
            return True

        # 3. Торкання у верхній панелі HUD — передача панелі HUD
        if self.hud_box.collide_point(*touch.pos):
            return self.hud_box.on_touch_down(touch)

        # 4. Нижні кнопки керування (Android) — штатне делегування контейнеру кнопок
        if hasattr(self, "controls_box") and self.controls_box.collide_point(*touch.pos):
            return self.controls_box.on_touch_down(touch)

        # 5. Торкання по ігровому полю — плавне переміщення корабля пальцем
        if self.is_playing:
            self.player.move_to_x(touch.x, self.width)
            touch.grab(self)
            return True

        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self.is_playing and not self.is_paused:
            self.player.move_to_x(touch.x, self.width)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    # --- Клавіатурне керування (для тестування на десктопі) ---
    def on_pre_enter(self, *args):
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def on_pre_leave(self, *args):
        Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        if self.game_clock_event:
            Clock.unschedule(self.game_clock_event)
            self.game_clock_event = None

    def _on_key_down(self, window, key, scancode, codepoint, modifier):
        if not self.is_playing or self.is_paused:
            if key == 112:  # 'p' для паузи
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
