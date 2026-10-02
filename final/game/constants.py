"""Константи та налаштування гри-шутера."""

# Вікно для десктопного тестування (пропорції Android смартфону)
WINDOW_WIDTH = 420
WINDOW_HEIGHT = 750

# Частота оновлення (FPS)
FPS = 60
FRAME_INTERVAL = 1.0 / FPS

# Параметри гравця
PLAYER_WIDTH = 56
PLAYER_HEIGHT = 56
PLAYER_MAX_HP = 100
PLAYER_SPEED = 360.0
PLAYER_FIRE_COOLDOWN = 0.22  # Обмеження швидкості стрільби (в секундах)

# Параметри куль
BULLET_PLAYER_SPEED = 650.0   # Рух вгору (+Y)
BULLET_ENEMY_SPEED = -320.0   # Рух вниз (-Y)
BULLET_PLAYER_DAMAGE = 35
BULLET_ENEMY_DAMAGE = 15
BULLET_WIDTH = 6
BULLET_HEIGHT = 16

# Параметри ворогів
ENEMY_WIDTH = 48
ENEMY_HEIGHT = 48
ENEMY_DEFAULT_HP = 35
ENEMY_SPEED_MIN = 110.0
ENEMY_SPEED_MAX = 190.0
ENEMY_SPAWN_INTERVAL = 1.3
ENEMY_FIRE_INTERVAL_MIN = 1.6
ENEMY_FIRE_INTERVAL_MAX = 3.0

# Параметри 2-шарового рухомого фону
BG_LAYER1_STARS_COUNT = 55
BG_LAYER1_SPEED = 40.0   # Повільний шар (далекі зірки)
BG_LAYER2_STARS_COUNT = 30
BG_LAYER2_SPEED = 115.0  # Швидкий шар (близькі яскраві зорі)

# Кольори (RGBA від 0.0 до 1.0)
COLOR_BG_SPACE = (0.04, 0.05, 0.10, 1.0)
COLOR_STAR_FAR = (0.65, 0.75, 0.95, 0.7)
COLOR_STAR_NEAR = (1.0, 1.0, 0.9, 0.95)

COLOR_PLAYER_PRIMARY = (0.15, 0.75, 1.0, 1.0)
COLOR_PLAYER_SECONDARY = (0.9, 0.95, 1.0, 1.0)
COLOR_PLAYER_ACCENT = (1.0, 0.4, 0.1, 1.0)

COLOR_ENEMY_PRIMARY = (0.95, 0.25, 0.35, 1.0)
COLOR_ENEMY_SECONDARY = (1.0, 0.6, 0.2, 1.0)

COLOR_BULLET_PLAYER = (0.2, 0.95, 1.0, 1.0)
COLOR_BULLET_ENEMY = (1.0, 0.3, 0.3, 1.0)
