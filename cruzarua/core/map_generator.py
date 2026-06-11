"""
core/map_generator.py - Geração procedural infinita do mapa.

Cria novas lanes à medida que o jogador avança e remove
as antigas para economizar memória.
"""

from utils.constants import LANES_AHEAD, LANES_BEHIND
from entities.lane import create_lane


class MapGenerator:
    """
    Mantém um dicionário de lanes indexadas por z_index.
    Gera novas lanes à frente e remove as que ficaram para trás.
    """

    def __init__(self):
        self.lanes = {}       # z_index → Lane
        self.difficulty = 1.0

    def reset(self):
        """Limpa o mapa e gera as lanes iniciais."""
        self.lanes.clear()
        self.difficulty = 1.0
        # Gera lanes iniciais (trás até frente)
        for z in range(-LANES_BEHIND, LANES_AHEAD + 1):
            self._generate_lane(z)

    def update(self, player_row, difficulty):
        """
        Verifica se novas lanes devem ser geradas e antigas removidas.
        player_row: linha atual do jogador (≥ 0, cresce ao avançar).
        """
        self.difficulty = difficulty

        # Gera lanes à frente
        max_needed = player_row + LANES_AHEAD
        for z in range(player_row - LANES_BEHIND, max_needed + 1):
            if z not in self.lanes:
                self._generate_lane(z)

        # Remove lanes antigas
        min_needed = player_row - LANES_BEHIND - 1
        to_remove = [z for z in self.lanes if z < min_needed]
        for z in to_remove:
            del self.lanes[z]

    def _generate_lane(self, z_index):
        """Gera uma lane para o índice dado."""
        # Não repete tipos iguais 3x seguidos
        lane = create_lane(z_index, self.difficulty)
        self.lanes[z_index] = lane

    def get_lane(self, z_index):
        """Retorna a lane no índice, ou None."""
        return self.lanes.get(z_index)

    def get_visible_lanes(self, player_row):
        """Retorna as lanes que devem ser renderizadas."""
        result = []
        for z in range(player_row - LANES_BEHIND,
                       player_row + LANES_AHEAD + 1):
            lane = self.lanes.get(z)
            if lane:
                result.append(lane)
        return result

    def update_lanes(self, dt, speed_factor):
        """Chama update em todas as lanes ativas."""
        for lane in self.lanes.values():
            lane.update(dt, speed_factor)
