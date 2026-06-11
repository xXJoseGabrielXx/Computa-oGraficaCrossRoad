"""
core/camera.py - Câmera isométrica com suavização.

Segue o jogador suavemente, mantendo perspectiva elevada e levemente inclinada.
"""

from OpenGL.GL import *
from OpenGL.GLU import *

from utils.constants import CAM_OFFSET_Y, CAM_OFFSET_Z, CAM_SMOOTH
from utils.math_utils import lerp


class Camera:
    """
    Câmera em terceira pessoa elevada que segue o jogador.
    A câmera está sempre atrás e acima do jogador,
    olhando levemente para baixo (perspectiva isométrica suave).
    """

    def __init__(self):
        # Posição atual (suavizada) do alvo
        self.target_x = 0.0
        self.target_z = 0.0
        # Posição real atual (interpolada)
        self.current_x = 0.0
        self.current_z = 0.0

    def update(self, player_x, player_z, dt):
        """
        Atualiza a posição do alvo e suaviza o movimento.
        Chamado a cada frame com delta time.
        """
        self.target_x = player_x
        self.target_z = player_z

        # Interpolação suave (exponential decay)
        t = min(1.0, CAM_SMOOTH * dt)
        self.current_x = lerp(self.current_x, self.target_x, t)
        self.current_z = lerp(self.current_z, self.target_z, t)

    def apply(self):
        """
        Aplica a transformação de câmera ao pipeline OpenGL.
        Deve ser chamado antes de desenhar a cena 3D.
        """
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Posição do olho: atrás e acima do jogador
        eye_x = self.current_x
        eye_y = CAM_OFFSET_Y
        eye_z = self.current_z + CAM_OFFSET_Z

        # Olhando para a posição do jogador com leve inclinação
        look_x = self.current_x
        look_y = 0.5
        look_z = self.current_z

        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0.0, 1.0, 0.0)

    def snap_to(self, x, z):
        """Teleporta a câmera sem suavização (usado no início/reinício)."""
        self.current_x = x
        self.current_z = z
        self.target_x  = x
        self.target_z  = z
