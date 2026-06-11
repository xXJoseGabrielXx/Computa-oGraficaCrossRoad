"""
core/collision.py - Gerenciamento centralizado de colisões AABB.

Verifica todas as colisões entre o jogador e:
  - Veículos nas estradas
  - Trens nos trilhos
  - Água (rio sem plataforma)
  - Limites do mapa
  - Árvores/obstáculos fixos (bloqueio de movimento)
"""

from utils.constants import LANE_ROAD, LANE_RIVER, LANE_RAIL, HALF_GRID


class CollisionManager:
    """
    Centraliza a lógica de detecção de colisão.
    Recebe referências ao jogador e ao gerador de mapa.
    """

    def __init__(self):
        pass

    def check_death(self, player, map_generator):
        """
        Verifica se o jogador deve morrer neste frame.
        Retorna (is_dead, cause) onde cause é uma string ou None.
        """
        if not player.alive:
            return False, None

        paabb = player.get_aabb()
        player_row = player.row
        lane = map_generator.get_lane(player_row)

        if lane is None:
            return False, None

        # ── Estrada: colisão com veículo ──────────────────────────────────────
        if lane.lane_type == LANE_ROAD:
            if lane.check_collision(paabb):
                return True, "vehicle"

        # ── Trilho: colisão com trem ──────────────────────────────────────────
        elif lane.lane_type == LANE_RAIL:
            if lane.check_collision(paabb):
                return True, "train"

        # ── Rio: verifica se está sobre plataforma ────────────────────────────
        elif lane.lane_type == LANE_RIVER:
            if not lane.is_player_safe(paabb):
                return True, "water"

        return False, None

    def handle_river_transport(self, player, map_generator, dt, speed_factor):
        """
        Se o jogador está sobre um tronco, aplica o deslocamento do tronco.
        Chamado a cada frame para lanes de rio.
        """
        player_row = player.row
        lane = map_generator.get_lane(player_row)

        if lane is None or lane.lane_type != LANE_RIVER:
            player.platform_dx = 0.0
            return

        paabb = player.get_aabb()
        platform = lane.get_platform_under_player(paabb)

        if platform is not None:
            player.platform_dx = 0.0
            dx = platform.get_velocity_dx(dt, speed_factor)
            player.apply_platform_move(dx)
        else:
            player.platform_dx = 0.0

    def check_tree_block(self, player, map_generator, new_grid_x, new_grid_z):
        """
        Verifica se mover para (new_grid_x, new_grid_z) está bloqueado por árvore.
        Retorna True se o movimento é bloqueado.
        """
        from utils.constants import CELL_SIZE
        target_row = -new_grid_z
        lane = map_generator.get_lane(target_row)

        if lane is None:
            return False

        if hasattr(lane, 'trees'):
            for tree_x in lane.trees:
                if round(tree_x) == new_grid_x:
                    return True

        return False