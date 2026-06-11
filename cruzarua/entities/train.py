"""
entities/train.py - Trem de alta velocidade com sistema de aviso.
"""

import random
from utils.constants import (
    HALF_GRID, TRAIN_SPEED, TRAIN_WARNING_TIME,
    TRAIN_INTERVAL_MIN, TRAIN_INTERVAL_MAX
)
from utils.math_utils import aabb_overlap


class Train:
    """
    Trem que atravessa a lane em alta velocidade.

    Estados:
      'idle'    - aguardando o próximo intervalo
      'warning' - aviso visual antes da chegada
      'running' - trem em movimento
    """

    WAGON_LENGTH = 1.9    # comprimento de cada vagão
    WAGON_COUNT  = 5      # vagões por trem
    TRAIN_WIDTH  = 1.8    # largura total do trem
    TRAIN_DEPTH  = 0.90

    def __init__(self, z_lane, difficulty=1.0):
        self.z         = float(z_lane)
        self.difficulty = difficulty

        # Estado
        self.state       = 'idle'
        self.timer       = 0.0
        self.interval    = random.uniform(TRAIN_INTERVAL_MIN, TRAIN_INTERVAL_MAX)
        self.direction   = random.choice([-1, 1])

        # Posição do trem (centro do conjunto)
        half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 2.0
        self.x = -half * self.direction

        # Flash de aviso (0..1)
        self.warning_flash = 0.0

    def update(self, dt):
        """Atualiza o estado do trem."""
        self.timer += dt

        if self.state == 'idle':
            if self.timer >= self.interval:
                self.timer    = 0.0
                self.state    = 'warning'
                self.interval = random.uniform(
                    TRAIN_INTERVAL_MIN / self.difficulty,
                    TRAIN_INTERVAL_MAX / self.difficulty
                )

        elif self.state == 'warning':
            # Pisca o aviso
            self.warning_flash = (self.timer / TRAIN_WARNING_TIME)
            if self.timer >= TRAIN_WARNING_TIME:
                self.timer         = 0.0
                self.state         = 'running'
                self.warning_flash = 0.0
                # Inicia fora do mapa
                half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 2.0
                self.x = -half * self.direction

        elif self.state == 'running':
            speed = TRAIN_SPEED * self.difficulty
            self.x += self.direction * speed * dt

            # Quando sai do mapa, volta para idle
            half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 3.0
            if self.direction > 0 and self.x > half:
                self.state = 'idle'
                self.timer = 0.0
            elif self.direction < 0 and self.x < -half:
                self.state = 'idle'
                self.timer = 0.0

    def is_dangerous(self):
        """True quando o trem está em movimento (pode matar)."""
        return self.state == 'running'

    def get_aabbs(self):
        """
        Retorna lista de AABBs para todos os vagões em movimento.
        Cada item: (cx, cz, w, d).
        """
        if self.state != 'running':
            return []

        aabbs = []
        for i in range(self.WAGON_COUNT):
            offset = (i - self.WAGON_COUNT // 2) * self.WAGON_LENGTH
            wx = self.x + offset
            aabbs.append((wx, self.z, self.TRAIN_WIDTH, self.TRAIN_DEPTH * 0.85))
        return aabbs

    def collides_with_player(self, player_aabb):
        px, pz, pw, pd = player_aabb
        for vx, vz, vw, vd in self.get_aabbs():
            if aabb_overlap(px, pz, pw, pd, vx, vz, vw, vd):
                return True
        return False

    def get_wagon_positions(self):
        """Posições X de cada vagão para renderização."""
        positions = []
        for i in range(self.WAGON_COUNT):
            offset = (i - self.WAGON_COUNT // 2) * self.WAGON_LENGTH
            positions.append(self.x + offset)
        return positions
