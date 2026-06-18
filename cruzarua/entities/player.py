
import math
from utils.constants import (
    CELL_SIZE, HALF_GRID,
    PLAYER_MOVE_DURATION, PLAYER_HOP_HEIGHT
)
from utils.math_utils import lerp, smooth_step, hop_height


class Player:

    def __init__(self):
        self.grid_x = 0
        self.grid_z = 0

        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        self._from_x = 0.0
        self._from_z = 0.0

        self.is_moving    = False
        self.move_timer   = 0.0
        self.facing       = 1.0

        self.platform_dx  = 0.0

        self.alive = True

        self._move_queue = []

    def reset(self):
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

        if abs(new_x) > HALF_GRID:
            return

        if len(self._move_queue) < 1:
            self._move_queue.append((new_x, new_z, dx, dz))


    def update(self, dt):
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
        self.platform_dx = dx
        logical_x = float(self.grid_x) * CELL_SIZE + self.platform_dx
        if abs(logical_x) > (HALF_GRID + 1) * CELL_SIZE:
            self.alive = False

    def get_aabb(self):
        return (self.x, self.z, 0.45, 0.45)

    @property
    def row(self):
        """Linha atual do jogador (grid_z negativo = avançou)."""
        return -self.grid_z
