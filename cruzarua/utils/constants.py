"""
utils/constants.py - Constantes e configurações globais do jogo.
"""

import numpy as np

# ─── Janela ───────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 900
WINDOW_HEIGHT = 700
TARGET_FPS    = 60

# ─── Grid / Mapa ──────────────────────────────────────────────────────────────
CELL_SIZE       = 1.0        # tamanho de cada célula do grid
GRID_WIDTH      = 11         # número de colunas (-5 a +5)
HALF_GRID       = GRID_WIDTH // 2   # limite lateral
VISIBLE_LANES   = 20         # linhas visíveis
LANES_AHEAD     = 14         # linhas geradas à frente do jogador
LANES_BEHIND    = 6          # linhas mantidas atrás

# ─── Jogador ──────────────────────────────────────────────────────────────────
PLAYER_MOVE_DURATION = 0.12  # segundos por movimento
PLAYER_HOP_HEIGHT    = 0.4   # altura do pulo

# ─── Câmera ───────────────────────────────────────────────────────────────────
CAM_OFFSET_Y   = 8.0    # distância vertical
CAM_OFFSET_Z   = 7.0    # distância atrás
CAM_SMOOTH     = 6.0    # fator de suavização da câmera

# ─── Veículos ─────────────────────────────────────────────────────────────────
CAR_BASE_SPEED   = 4.0
TRUCK_BASE_SPEED = 2.5
VEHICLE_SPAWN_MARGIN = 3.0   # fora do mapa antes de reaparecer

# ─── Trem ─────────────────────────────────────────────────────────────────────
TRAIN_SPEED        = 18.0
TRAIN_WARNING_TIME = 2.0     # segundos de aviso antes do trem
TRAIN_INTERVAL_MIN = 4.0
TRAIN_INTERVAL_MAX = 8.0

# ─── Rio ──────────────────────────────────────────────────────────────────────
LOG_SPEED_MIN  = 1.5
LOG_SPEED_MAX  = 3.0
LOG_MIN_LEN    = 1        # comprimento em células
LOG_MAX_LEN    = 3
LILYPAD_SIZE   = 0.9

# ─── Águia ────────────────────────────────────────────────────────────────────
EAGLE_IDLE_TIME    = 6.0    # segundos antes de aparecer
EAGLE_APPROACH_TIME= 4.0    # segundos da aproximação
EAGLE_STRIKE_TIME  = 1.5    # segundos do ataque final

# ─── Dificuldade ──────────────────────────────────────────────────────────────
DIFF_SPEED_SCALE   = 0.008   # multiplicador de velocidade por ponto
DIFF_EAGLE_SCALE   = 0.03    # redução do tempo da águia por ponto

# ─── Tipos de Lane ────────────────────────────────────────────────────────────
LANE_GRASS  = "grass"
LANE_ROAD   = "road"
LANE_RIVER  = "river"
LANE_RAIL   = "rail"

# ─── Cores (R, G, B) ──────────────────────────────────────────────────────────
COLOR_GRASS_LIGHT  = (0.42, 0.72, 0.28)
COLOR_GRASS_DARK   = (0.36, 0.62, 0.22)
COLOR_ROAD         = (0.28, 0.28, 0.30)
COLOR_ROAD_LINE    = (0.95, 0.85, 0.10)
COLOR_WATER        = (0.15, 0.50, 0.85)
COLOR_WATER_DARK   = (0.10, 0.40, 0.75)
COLOR_RAIL_BED     = (0.55, 0.48, 0.38)
COLOR_RAIL_TRACK   = (0.65, 0.65, 0.70)

COLOR_TREE_TRUNK   = (0.45, 0.30, 0.15)
COLOR_TREE_TOP     = (0.18, 0.55, 0.18)
COLOR_TREE_TOP2    = (0.22, 0.65, 0.22)

COLOR_LOG          = (0.60, 0.42, 0.22)
COLOR_LOG_END      = (0.72, 0.52, 0.30)
COLOR_LILYPAD      = (0.20, 0.60, 0.25)
COLOR_FLOWER       = (1.00, 0.95, 0.95)

COLOR_CAR_BODY     = [(0.85, 0.15, 0.15), (0.15, 0.45, 0.85),
                      (0.85, 0.65, 0.10), (0.55, 0.10, 0.75),
                      (0.10, 0.70, 0.45)]
COLOR_TRUCK_BODY   = [(0.70, 0.30, 0.10), (0.20, 0.50, 0.20),
                      (0.50, 0.50, 0.60)]
COLOR_WINDOW       = (0.70, 0.90, 1.00)
COLOR_WHEEL        = (0.12, 0.12, 0.12)

COLOR_TRAIN        = (0.80, 0.10, 0.10)
COLOR_TRAIN_WINDOW = (0.70, 0.90, 1.00)

COLOR_PLAYER_BODY  = (1.00, 0.85, 0.55)
COLOR_PLAYER_BEAK  = (1.00, 0.60, 0.10)
COLOR_PLAYER_EYE   = (0.10, 0.10, 0.10)
COLOR_PLAYER_WING  = (0.90, 0.75, 0.45)

COLOR_EAGLE_BODY   = (0.55, 0.35, 0.10)
COLOR_EAGLE_HEAD   = (1.00, 1.00, 1.00)
COLOR_EAGLE_BEAK   = (0.95, 0.70, 0.05)

COLOR_WARNING      = (1.00, 0.85, 0.00)
COLOR_DANGER       = (1.00, 0.15, 0.05)

COLOR_FOG          = (0.80, 0.88, 0.95)
COLOR_SKY          = (0.53, 0.81, 0.98)