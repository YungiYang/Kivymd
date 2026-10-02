"""Моделі та конфігурації кораблів гравця (Hangar / Ship Shop)."""

class ShipConfig:
    """Конфігурація характеристик та візуального стилю корабля гравця."""

    def __init__(
        self,
        ship_id: str,
        name: str,
        class_name: str,
        cost: int,
        attack_type: str,  # "blaster", "beam", "charge", "spread", "missile", "dual_beam"
        max_hp: int,
        speed: float,
        fire_cooldown: float,
        bullet_damage: int,
        bullet_speed: float,
        initial_shield: int,
        description: str,
        weapon_desc: str,
        primary_color: tuple,
        secondary_color: tuple,
        accent_color: tuple,
        width: float = 46.0,
        height: float = 46.0,
    ):
        self.ship_id = ship_id
        self.name = name
        self.class_name = class_name
        self.cost = cost
        self.attack_type = attack_type
        self.max_hp = max_hp
        self.speed = speed
        self.fire_cooldown = fire_cooldown
        self.bullet_damage = bullet_damage
        self.bullet_speed = bullet_speed
        self.initial_shield = initial_shield
        self.description = description
        self.weapon_desc = weapon_desc
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.accent_color = accent_color
        self.width = width
        self.height = height


# Каталог кораблів, доступних у грі
SHIPS_CATALOG: dict[str, ShipConfig] = {
    "striker": ShipConfig(
        ship_id="striker",
        name="«ФЕНІКС»",
        class_name="Швидкісний Штурмовик",
        cost=0,
        attack_type="blaster",
        max_hp=100,
        speed=360.0,
        fire_cooldown=0.22,
        bullet_damage=35,
        bullet_speed=650.0,
        initial_shield=0,
        description="Збалансований класичний винищувач Альянсу. Швидкий, надійний та легкий у пілотуванні.",
        weapon_desc="Здвоєні скорострільні плазмові лазери з можливістю модернізації.",
        primary_color=(0.15, 0.45, 0.95, 1.0),
        secondary_color=(0.10, 0.25, 0.60, 1.0),
        accent_color=(0.20, 0.90, 1.0, 1.0),
        width=46.0,
        height=46.0,
    ),
    "beam_titan": ShipConfig(
        ship_id="beam_titan",
        name="«ГЕЛІОС»",
        class_name="Променевий Крейсер",
        cost=1500,
        attack_type="beam",
        max_hp=125,
        speed=325.0,
        fire_cooldown=2.5,  # Повний цикл променя
        bullet_damage=180,  # DPS безперервного променя
        bullet_speed=900.0,
        initial_shield=0,
        description="Важкий науково-бойовий крейсер із потужною квантовою призмою на носовій турелі.",
        weapon_desc="Довгий безперервний лазерний промінь (діє 2.2 сек), що пропалює ворогів наскрізь!",
        primary_color=(0.05, 0.65, 0.60, 1.0),
        secondary_color=(0.04, 0.35, 0.38, 1.0),
        accent_color=(0.20, 1.0, 0.75, 1.0),
        width=50.0,
        height=50.0,
    ),
    "plasma_vanguard": ShipConfig(
        ship_id="plasma_vanguard",
        name="«ВУЛКАН»",
        class_name="Плазмовий Дредноут",
        cost=3000,
        attack_type="charge",
        max_hp=150,
        speed=295.0,
        fire_cooldown=1.5,  # Час заряджання мега-сфери
        bullet_damage=160,  # Велика шкода мега-сфери
        bullet_speed=520.0,
        initial_shield=0,
        description="Масивний броньований дредноут, здатний генерувати нестабільні згустки антиматерії.",
        weapon_desc="Заряджає велику плазмову сферу, яка при влучанні вибухає по радіусу!",
        primary_color=(0.85, 0.45, 0.10, 1.0),
        secondary_color=(0.50, 0.20, 0.05, 1.0),
        accent_color=(1.0, 0.85, 0.20, 1.0),
        width=54.0,
        height=50.0,
    ),
    "storm_valkyrie": ShipConfig(
        ship_id="storm_valkyrie",
        name="«ВАЛЬКІРІЯ»",
        class_name="Штормовий Перехоплювач",
        cost=5000,
        attack_type="spread",
        max_hp=95,
        speed=425.0,
        fire_cooldown=0.25,
        bullet_damage=26,  # 3 x 26 = 78 на залп
        bullet_speed=700.0,
        initial_shield=1,  # Вбудований щит на старті!
        description="Надшвидкий перехоплювач спеціального призначення з фазованим щитом та віяловим залпом.",
        weapon_desc="Віяловий залп 3 плазмовими снарядами + стартовий силовий щит у кожному бою!",
        primary_color=(0.60, 0.15, 0.80, 1.0),
        secondary_color=(0.35, 0.08, 0.50, 1.0),
        accent_color=(0.95, 0.35, 1.0, 1.0),
        width=48.0,
        height=48.0,
    ),
    # ── Нові кораблі ──────────────────────────────────────────────────────────
    "nova_hunter": ShipConfig(
        ship_id="nova_hunter",
        name="«НОВА»",
        class_name="Мисливець за Новими",
        cost=8000,
        attack_type="missile",
        max_hp=110,
        speed=340.0,
        fire_cooldown=0.65,  # Ракети летять повільніше, але б'ють дуже боляче
        bullet_damage=75,    # Висока шкода ракети
        bullet_speed=480.0,
        initial_shield=0,
        description="Спеціалізований мисливець, озброєний самонавідними ракетами класу 'Зенітна Нова'.",
        weapon_desc="Самонавідна ракета, що обирає найближчого ворога і завдає великої шкоди при вибуху!",
        primary_color=(0.7, 0.15, 0.15, 1.0),
        secondary_color=(0.45, 0.08, 0.08, 1.0),
        accent_color=(1.0, 0.45, 0.1, 1.0),
        width=48.0,
        height=46.0,
    ),
    "phantom_shade": ShipConfig(
        ship_id="phantom_shade",
        name="«ТІНЬ»",
        class_name="Корвет-Примара",
        cost=12000,
        attack_type="dual_beam",
        max_hp=80,
        speed=490.0,          # Надшвидкий корвет
        fire_cooldown=0.18,   # Дуже швидка стрільба
        bullet_damage=22,
        bullet_speed=750.0,
        initial_shield=2,     # Вбудований фазовий щит
        description="Надшвидкий корвет-невидимка з подвійними паралельними лазерами та вбудованим фазовим щитом.",
        weapon_desc="Безперервний дуальний лазерний залп - два паралельних промені пробивають щити ворогів!",
        primary_color=(0.15, 0.15, 0.25, 1.0),
        secondary_color=(0.08, 0.08, 0.18, 1.0),
        accent_color=(0.7, 0.4, 1.0, 1.0),
        width=42.0,
        height=44.0,
    ),
    # ── Крафтові (легендарні) кораблі ─────────────────────────────────────────
    "inferno_titan": ShipConfig(
        ship_id="inferno_titan",
        name="«ІНФЕРНО-ТИТАН»",
        class_name="Легендарний Дредноут",
        cost=0,               # Тільки крафт
        attack_type="charge",
        max_hp=220,
        speed=270.0,
        fire_cooldown=1.2,    # Заряджання термоядерного пострілу
        bullet_damage=220,    # Нищівний удар
        bullet_speed=580.0,
        initial_shield=3,
        description="Викований у глибинах Магма-9, цей дредноут може витримати все - крім зупинки.",
        weapon_desc="Термоядерна мега-плазма заряджається 1.2 сек, але вибух знищує все на екрані!",
        primary_color=(0.85, 0.25, 0.05, 1.0),
        secondary_color=(0.55, 0.10, 0.02, 1.0),
        accent_color=(1.0, 0.75, 0.1, 1.0),
        width=60.0,
        height=56.0,
    ),
    "abyssal_leviathan": ShipConfig(
        ship_id="abyssal_leviathan",
        name="«ЛЕВІАФАН»",
        class_name="Елітний Лінкор Безодні",
        cost=0,               # Тільки крафт
        attack_type="beam",
        max_hp=190,
        speed=300.0,
        fire_cooldown=2.0,    # Повний цикл абісального променя
        bullet_damage=250,    # Нищівний DPS антиматерії
        bullet_speed=1000.0,
        initial_shield=2,
        description="Знайдений на дні найглибшого океану, Левіафан - живий корабель, що стріляє потоком антиматерії.",
        weapon_desc="Абісальний промінь тривалістю 3 сек. Пронизує все на своєму шляху!",
        primary_color=(0.05, 0.40, 0.55, 1.0),
        secondary_color=(0.03, 0.22, 0.35, 1.0),
        accent_color=(0.1, 0.95, 0.85, 1.0),
        width=58.0,
        height=54.0,
    ),
    "void_phantom": ShipConfig(
        ship_id="void_phantom",
        name="«ФАНТОМ ПУСТОТИ»",
        class_name="Надлегендарний Тіньовий Destroyer",
        cost=0,               # Тільки крафт (ультимейт корабель)
        attack_type="spread",
        max_hp=160,
        speed=520.0,          # Найшвидший корабель у грі
        fire_cooldown=0.15,   # Найшвидша стрільба у грі
        bullet_damage=45,     # 5 снарядів × 45 = 225 на залп
        bullet_speed=800.0,
        initial_shield=4,     # Максимальний стартовий щит
        description="Корабель, побудований з матерії Пустоти. Він не існує у нашому вимірі... але вороги його відчувають.",
        weapon_desc="П'ятипроменевий квантовий залп. 5 снарядів розходяться по всій ширині екрана!",
        primary_color=(0.25, 0.05, 0.45, 1.0),
        secondary_color=(0.15, 0.02, 0.28, 1.0),
        accent_color=(0.85, 0.25, 1.0, 1.0),
        width=52.0,
        height=50.0,
    ),
}

# Порядок відображення кораблів у магазині/ангарі
ORDERED_SHIP_IDS = [
    "striker",
    "beam_titan",
    "plasma_vanguard",
    "storm_valkyrie",
    "nova_hunter",
    "phantom_shade",
    "inferno_titan",
    "abyssal_leviathan",
    "void_phantom",
]

# Кораблі, які не продаються — їх можна отримати лише крафтом
CRAFT_ONLY_SHIPS = ["inferno_titan", "abyssal_leviathan", "void_phantom"]


def get_ship_config(ship_id: str) -> ShipConfig:
    """Повертає конфігурацію корабля за його ID, або striker за замовчуванням."""
    return SHIPS_CATALOG.get(ship_id, SHIPS_CATALOG["striker"])
