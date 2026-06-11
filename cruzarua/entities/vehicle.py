"""
entities/vehicle.py - Veículos (carros e caminhões) nas estradas.
"""

import random
from utils.constants import (
    CELL_SIZE, HALF_GRID, VEHICLE_SPAWN_MARGIN,
    CAR_BASE_SPEED, TRUCK_BASE_SPEED
)
from utils.math_utils import aabb_overlap


class Vehicle:
    """
    Veículo genérico que se move horizontalmente em uma lane.

    direction: +1 (esquerda→direita) ou -1 (direita→esquerda).
    """

    # Dimensões padrão (override nas subclasses)
    WIDTH  = 0.70   # ao longo do eixo X (direção do movimento)
    DEPTH  = 0.90   # ao longo do eixo Z

    def __init__(self, z_lane, direction, speed, color_index):
        self.z           = float(z_lane)
        self.direction   = direction   # ±1
        self.speed       = speed
        self.color_index = color_index

        # Posição X inicial (fora do mapa)
        half = HALF_GRID + VEHICLE_SPAWN_MARGIN
        self.x = -half * direction  # aparece do lado oposto ao movimento

    def update(self, dt, speed_factor=1.0):
        """Move o veículo horizontalmente."""
        self.x += self.direction * self.speed * speed_factor * dt

        # Reposiciona quando sai do mapa pelo outro lado
        half = HALF_GRID + VEHICLE_SPAWN_MARGIN
        if self.direction > 0 and self.x > half:
            self.x = -half
        elif self.direction < 0 and self.x < -half:
            self.x = half

    def get_aabb(self):
        """AABB: (cx, cz, w, d)."""
        return (self.x, self.z, self.WIDTH * 0.9, self.DEPTH * 0.85)

    def collides_with_player(self, player_aabb):
        px, pz, pw, pd = player_aabb
        vx, vz, vw, vd = self.get_aabb()
        return aabb_overlap(px, pz, pw, pd, vx, vz, vw, vd)


class Car(Vehicle):
    """Carro pequeno, mais rápido."""
    WIDTH = 0.70
    DEPTH = 0.90

    def __init__(self, z_lane, direction, speed, color_index):
        super().__init__(z_lane, direction, speed, color_index)


class Truck(Vehicle):
    """Caminhão largo, mais lento."""
    WIDTH = 2.20
    DEPTH = 0.90

    def __init__(self, z_lane, direction, speed, color_index):
        super().__init__(z_lane, direction, speed, color_index)


def create_vehicles_for_lane(z_lane, difficulty=1.0):
    """
    Cria um conjunto de veículos para uma lane de estrada.
    Retorna lista de Vehicle.
    """
    vehicles = []
    direction = random.choice([-1, 1])

    # Número de veículos baseado na dificuldade
    count = random.randint(1, min(3, 1 + int(difficulty)))

    # Decide tipo: carros ou caminhões (nunca mistura)
    use_truck = random.random() < 0.3

    half = HALF_GRID + VEHICLE_SPAWN_MARGIN
    positions = []

    for i in range(count):
        color_idx = random.randint(0, 10)

        if use_truck:
            speed = TRUCK_BASE_SPEED * difficulty * random.uniform(0.8, 1.2)
            v = Truck(z_lane, direction, speed, color_idx)
        else:
            speed = CAR_BASE_SPEED * difficulty * random.uniform(0.8, 1.2)
            v = Car(z_lane, direction, speed, color_idx)

        # Espaça os veículos uniformemente
        spacing = (2 * half) / max(count, 1)
        v.x = -half * direction + direction * spacing * i
        vehicles.append(v)

    return vehicles
