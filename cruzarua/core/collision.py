from utils.constants import LANE_ROAD, LANE_RIVER, LANE_RAIL, HALF_GRID


class CollisionManager:

    def __init__(self):
        pass

    def check_death(self, player, map_generator):
        if not player.alive:
            return False, None

        paabb = player.get_aabb()
        player_row = player.row
        lane = map_generator.get_lane(player_row)

        if lane is None:
            return False, None

        if lane.lane_type == LANE_ROAD:
            if lane.check_collision(paabb):
                return True, "vehicle"

        elif lane.lane_type == LANE_RAIL:
            if lane.check_collision(paabb):
                return True, "train"

        elif lane.lane_type == LANE_RIVER:
            if not lane.is_player_safe(paabb):
                return True, "water"

        return False, None

    def handle_river_transport(self, player, map_generator, dt, speed_factor):

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
