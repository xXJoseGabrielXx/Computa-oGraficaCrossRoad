"""
entities/player.py - Personagem controlado pelo jogador.

Movimento grid-based com animação suave de salto.
"""

import math
from utils.constants import (
    CELL_SIZE, HALF_GRID,
    PLAYER_MOVE_DURATION, PLAYER_HOP_HEIGHT
)
from utils.math_utils import lerp, smooth_step, hop_height


class Player:
    """
    O personagem principal.

    Posição lógica: (grid_x, grid_z) inteiros no grid.
    Posição visual: (x, y, z) floats interpolados para animação suave.
    """

    def __init__(self):
        # Posição lógica no grid
        self.grid_x = 0
        self.grid_z = 0

        # Posição visual (interpolada)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        # Posição anterior (para interpolação)
        self._from_x = 0.0
        self._from_z = 0.0

        # Animação de movimento
        self.is_moving    = False
        self.move_timer   = 0.0   # 0..PLAYER_MOVE_DURATION
        self.facing       = 1.0   # +1 frente, -1 trás

        # Movimento de plataforma (tronco): offset aplicado ao visual
        self.platform_dx  = 0.0

        # Vivo/morto
        self.alive = True

        # Fila de movimentos pendentes
        self._move_queue = []

    def reset(self):
        """Reinicia o jogador na posição inicial."""
        self.grid_x = 0
        self.grid_z = 0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self._from_x = 0.0
        self._from_z = 0.0
        self.is_moving   = False
        self.move_timer  = 0.0
        self.alive       = True
        self.platform_dx = 0.0
        self._move_queue.clear()

    # ──────────────────────────────────────────────────────────────────────────
    # Input
    # ──────────────────────────────────────────────────────────────────────────

    def request_move(self, dx, dz):
        """
        Solicita um movimento no grid.
        dx: deslocamento em X (±1).
        dz: deslocamento em Z (±1 — negativo = avançar).
        """
        if not self.alive:
            return

        new_x = self.grid_x + dx
        new_z = self.grid_z + dz

        # Limites laterais do mapa
        if abs(new_x) > HALF_GRID:
            return

        # Enfileira o movimento (descarta se já tem 1 na fila)
        if len(self._move_queue) < 1:
            self._move_queue.append((new_x, new_z, dx, dz))

    # ──────────────────────────────────────────────────────────────────────────
    # Update
    # ──────────────────────────────────────────────────────────────────────────

    def update(self, dt):
        """Atualiza a animação de movimento. Chamado a cada frame."""
        if not self.is_moving and self._move_queue:
            new_x, new_z, dx, dz = self._move_queue.pop(0)
            self._from_x  = float(self.grid_x) * CELL_SIZE
            self._from_z  = self.z
            self.grid_x   = new_x
            self.grid_z   = new_z
            self.is_moving = True
            self.move_timer = 0.0
            if dz < 0:
                self.facing = 1.0
            elif dz > 0:
                self.facing = -1.0

        if self.is_moving:
            self.move_timer += dt
            t = self.move_timer / PLAYER_MOVE_DURATION
            if t >= 1.0:
                t = 1.0
                self.is_moving = False

            st = smooth_step(t)
            target_x = float(self.grid_x) * CELL_SIZE
            target_z = float(self.grid_z) * CELL_SIZE

            self.x = lerp(self._from_x, target_x, st) + self.platform_dx
            self.z = lerp(self._from_z, target_z, st)
            self.y = hop_height(t, PLAYER_HOP_HEIGHT)
        else:
            self.x = float(self.grid_x) * CELL_SIZE + self.platform_dx
            self.z = float(self.grid_z) * CELL_SIZE
            self.y = 0.0

    def apply_platform_move(self, dx):
        """
        Chamado pela lane de rio quando o jogador está sobre um tronco.
        dx é o deslocamento do tronco neste frame.
        """
        self.platform_dx = dx
        logical_x = float(self.grid_x) * CELL_SIZE + self.platform_dx
        if abs(logical_x) > (HALF_GRID + 1) * CELL_SIZE:
            self.alive = False

    def get_aabb(self):
        """
        Retorna o AABB do jogador: (cx, cz, w, d).
        cx, cz = centro; w, d = largura e profundidade.
        """
        return (self.x, self.z, 0.45, 0.45)

    @property
    def row(self):
        """Linha atual do jogador (grid_z negativo = avançou)."""
        return -self.grid_z