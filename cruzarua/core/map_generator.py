from utils.constants import LANES_AHEAD, LANES_BEHIND
from entities.lane import create_lane


class MapGenerator:

    def __init__(self):
        self.lanes = {}
        self.difficulty = 1.0

    def reset(self):
        """Limpa o mapa e gera as lanes iniciais."""
        self.lanes.clear()
        self.difficulty = 1.0
        for z in range(-LANES_BEHIND, LANES_AHEAD + 1):
            self._generate_lane(z)

    def update(self, player_row, difficulty):
        self.difficulty = difficulty
        max_needed = player_row + LANES_AHEAD
        for z in range(player_row - LANES_BEHIND, max_needed + 1):
            if z not in self.lanes:
                self._generate_lane(z)

        min_needed = player_row - LANES_BEHIND - 1
        to_remove = [z for z in self.lanes if z < min_needed]
        for z in to_remove:
            del self.lanes[z]

    def _generate_lane(self, z_index):

        lane = create_lane(z_index, self.difficulty)
        self.lanes[z_index] = lane

    def get_lane(self, z_index):
        return self.lanes.get(z_index)

    def get_visible_lanes(self, player_row):
        result = []
        for z in range(player_row - LANES_BEHIND,
                       player_row + LANES_AHEAD + 1):
            lane = self.lanes.get(z)
            if lane:
                result.append(lane)
        return result

    def update_lanes(self, dt, speed_factor):
        for lane in self.lanes.values():
            lane.update(dt, speed_factor)
