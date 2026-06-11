"""
entities/log.py - Troncos e vitórias-régias do rio.
"""

import random
from utils.constants import (
    CELL_SIZE, HALF_GRID,
    LOG_SPEED_MIN, LOG_SPEED_MAX,
    LOG_MIN_LEN, LOG_MAX_LEN,
    LILYPAD_SIZE
)
from utils.math_utils import aabb_overlap


class Log:
    """
    Tronco flutuante no rio.
    O jogador pode se mover sobre o tronco e é transportado com ele.
    """

    HEIGHT = 0.20   # altura superfície do tronco

    def __init__(self, z_lane, x_start, length, direction, speed):
        self.z         = float(z_lane)
        self.x         = float(x_start)
        self.length    = length          # em células
        self.direction = direction       # ±1
        self.speed     = speed

        # Tamanho real
        self.width = length * CELL_SIZE - 0.1  # eixo X (direção)
        self.depth = 0.82                       # eixo Z

    def update(self, dt, speed_factor=1.0):
        """Move o tronco horizontalmente."""
        self.x += self.direction * self.speed * speed_factor * dt

        # Wrap ao sair do mapa
        half = HALF_GRID + self.length * CELL_SIZE + 1.0
        if self.direction > 0 and self.x - self.width * 0.5 > half:
            self.x = -half - self.width * 0.5
        elif self.direction < 0 and self.x + self.width * 0.5 < -half:
            self.x = half + self.width * 0.5

    def get_aabb(self):
        """AABB: (cx, cz, w, d)."""
        return (self.x, self.z, self.width, self.depth)

    def player_on_log(self, player_aabb):
        """Verifica se o jogador está sobre este tronco."""
        px, pz, pw, pd = player_aabb
        return aabb_overlap(px, pz, pw * 0.9, pd * 0.9,
                            self.x, self.z, self.width, self.depth)

    def get_velocity_dx(self, dt, speed_factor=1.0):
        """Deslocamento deste frame para transportar o jogador."""
        return self.direction * self.speed * speed_factor * dt


class LilyPad:
    """
    Vitória-régia: plataforma estática no rio.
    O jogador pode ficar sobre ela mas ela não se move.
    """

    HEIGHT = 0.10

    def __init__(self, z_lane, x_pos):
        self.z = float(z_lane)
        self.x = float(x_pos)
        self.size = LILYPAD_SIZE

    def update(self, dt, speed_factor=1.0):
        pass  # estática

    def player_on_lilypad(self, player_aabb):
        px, pz, pw, pd = player_aabb
        return aabb_overlap(px, pz, pw * 0.9, pd * 0.9,
                            self.x, self.z, self.size, self.size)

    def get_velocity_dx(self, dt, speed_factor=1.0):
        return 0.0


def create_platforms_for_lane(z_lane, difficulty=1.0):
    """
    Cria troncos e vitórias-régias para uma lane de rio.
    Garante que sempre haja pelo menos uma plataforma segura.
    """
    platforms = []
    direction = random.choice([-1, 1])

    # Número de troncos baseado em dificuldade
    n_logs = random.randint(2, min(4, 2 + int(difficulty * 0.5)))

    half = HALF_GRID
    spacing = (2 * half) / max(n_logs, 1)

    for i in range(n_logs):
        length = random.randint(LOG_MIN_LEN, LOG_MAX_LEN)
        speed  = random.uniform(LOG_SPEED_MIN,
                                LOG_SPEED_MAX * min(difficulty, 2.0))
        x_start = -half + spacing * i + random.uniform(-0.5, 0.5)
        platforms.append(Log(z_lane, x_start, length, direction, speed))

    # Adiciona vitória-régia ocasionalmente
    if random.random() < 0.3:
        x_pos = random.uniform(-half + 1, half - 1)
        platforms.append(LilyPad(z_lane, x_pos))

    return platforms