"""
utils/math_utils.py - Funções matemáticas auxiliares.
"""

import math


def lerp(a, b, t):
    """Interpolação linear entre a e b pelo fator t."""
    return a + (b - a) * t


def clamp(val, min_val, max_val):
    """Limita val entre min_val e max_val."""
    return max(min_val, min(max_val, val))


def smooth_step(t):
    """Curva de suavização suave (ease in-out)."""
    t = clamp(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def aabb_overlap(ax, az, aw, ad, bx, bz, bw, bd):
    """
    Verifica sobreposição entre dois AABBs 2D (eixos X e Z).
    ax, az = centro do objeto A
    aw, ad = largura e profundidade do objeto A
    bx, bz = centro do objeto B
    bw, bd = largura e profundidade do objeto B
    Retorna True se houver sobreposição.
    """
    half_aw = aw * 0.5
    half_ad = ad * 0.5
    half_bw = bw * 0.5
    half_bd = bd * 0.5

    return (abs(ax - bx) < (half_aw + half_bw) and
            abs(az - bz) < (half_ad + half_bd))


def hop_height(t, max_height):
    """
    Calcula a altura de um pulo parabólico.
    t entre 0 e 1 representa o progresso do movimento.
    Retorna a altura no instante t.
    """
    return max_height * math.sin(math.pi * t)
