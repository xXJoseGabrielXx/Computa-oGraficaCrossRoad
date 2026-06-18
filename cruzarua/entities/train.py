
import random
from utils.constants import (
    HALF_GRID, TRAIN_SPEED, TRAIN_WARNING_TIME,
    TRAIN_INTERVAL_MIN, TRAIN_INTERVAL_MAX
)
from utils.math_utils import aabb_overlap


class Train:

    WAGON_LENGTH = 1.9 
    WAGON_COUNT  = 5
    TRAIN_WIDTH  = 1.8
    TRAIN_DEPTH  = 0.90

    def __init__(self, z_lane, difficulty=1.0):
        self.z         = float(z_lane)
        self.difficulty = difficulty

        self.state       = 'idle'
        self.timer       = 0.0
        self.interval    = random.uniform(TRAIN_INTERVAL_MIN, TRAIN_INTERVAL_MAX)
        self.direction   = random.choice([-1, 1])

        half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 2.0
        self.x = -half * self.direction

        self.warning_flash = 0.0

    def update(self, dt):
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
            self.warning_flash = (self.timer / TRAIN_WARNING_TIME)
            if self.timer >= TRAIN_WARNING_TIME:
                self.timer         = 0.0
                self.state         = 'running'
                self.warning_flash = 0.0
                half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 2.0
                self.x = -half * self.direction

        elif self.state == 'running':
            speed = TRAIN_SPEED * self.difficulty
            self.x += self.direction * speed * dt

            half = HALF_GRID + self.WAGON_LENGTH * self.WAGON_COUNT + 3.0
            if self.direction > 0 and self.x > half:
                self.state = 'idle'
                self.timer = 0.0
            elif self.direction < 0 and self.x < -half:
                self.state = 'idle'
                self.timer = 0.0

    def is_dangerous(self):
        return self.state == 'running'

    def get_aabbs(self):
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
        positions = []
        for i in range(self.WAGON_COUNT):
            offset = (i - self.WAGON_COUNT // 2) * self.WAGON_LENGTH
            positions.append(self.x + offset)
        return positions
