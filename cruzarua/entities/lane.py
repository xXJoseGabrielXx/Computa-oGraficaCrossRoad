
import random
from utils.constants import (
    LANE_GRASS, LANE_ROAD, LANE_RIVER, LANE_RAIL,
    HALF_GRID, CELL_SIZE
)
from entities.vehicle import create_vehicles_for_lane
from entities.train import Train
from entities.log import create_platforms_for_lane


class Lane:

    def __init__(self, z_index, lane_type):
        self.z_index   = z_index
        self.z_world   = float(-z_index) 
        self.lane_type = lane_type
        self.anim_offset = 0.0 

    def update(self, dt, speed_factor=1.0):
        pass

    def is_safe_position(self, x):
        return True

    def get_obstacles(self):
        return []


class GrassLane(Lane):

    def __init__(self, z_index, is_dark=False):
        super().__init__(z_index, LANE_GRASS)
        self.is_dark   = is_dark
        self.trees     = [] 
        self._generate_trees()

    def _generate_trees(self):
        if self.z_index == 0:
            return
        for col in range(-HALF_GRID, HALF_GRID + 1):
            if col == 0 and self.z_index <= 2:
                continue  
            if random.random() < 0.18:
                self.trees.append(float(col))

    def is_safe_position(self, x):
        col = round(x / CELL_SIZE)
        return col not in [round(t) for t in self.trees]

    def get_obstacles(self):
        return self.trees


class RoadLane(Lane):

    def __init__(self, z_index, difficulty=1.0):
        super().__init__(z_index, LANE_ROAD)
        self.vehicles = create_vehicles_for_lane(self.z_world, difficulty)

    def update(self, dt, speed_factor=1.0):
        for v in self.vehicles:
            v.update(dt, speed_factor)

    def check_collision(self, player_aabb):
        for v in self.vehicles:
            if v.collides_with_player(player_aabb):
                return True
        return False


class RiverLane(Lane):

    def __init__(self, z_index, difficulty=1.0):
        super().__init__(z_index, LANE_RIVER)
        self.platforms  = create_platforms_for_lane(self.z_world, difficulty)
        self.anim_timer = 0.0

    def update(self, dt, speed_factor=1.0):
        self.anim_timer += dt * 0.5
        for p in self.platforms:
            p.update(dt, speed_factor)

    def get_platform_under_player(self, player_aabb):
        for p in self.platforms:
            if hasattr(p, 'player_on_log') and p.player_on_log(player_aabb):
                return p
            if hasattr(p, 'player_on_lilypad') and p.player_on_lilypad(player_aabb):
                return p
        return None

    def is_player_safe(self, player_aabb):
        return self.get_platform_under_player(player_aabb) is not None


class RailLane(Lane):

    def __init__(self, z_index, difficulty=1.0):
        super().__init__(z_index, LANE_RAIL)
        self.train = Train(self.z_world, difficulty)

    def update(self, dt, speed_factor=1.0):
        self.train.update(dt) 

    def check_collision(self, player_aabb):
        return self.train.collides_with_player(player_aabb)

    @property
    def warning_flash(self):
        return self.train.warning_flash



def create_lane(z_index, difficulty=1.0, force_type=None):
    if force_type:
        lane_type = force_type
    elif z_index <= 1:
        lane_type = LANE_GRASS
    else:
        roll = random.random()
        if roll < 0.35:
            lane_type = LANE_GRASS
        elif roll < 0.70:
            lane_type = LANE_ROAD
        else:
            lane_type = LANE_RAIL

    is_dark = (z_index % 2 == 0)

    if lane_type == LANE_GRASS:
        return GrassLane(z_index, is_dark)
    elif lane_type == LANE_ROAD:
        return RoadLane(z_index, difficulty)
    elif lane_type == LANE_RIVER:
        return RiverLane(z_index, difficulty)
    elif lane_type == LANE_RAIL:
        return RailLane(z_index, difficulty)
    else:
        return GrassLane(z_index, is_dark)
