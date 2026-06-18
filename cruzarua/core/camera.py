

from OpenGL.GL import *
from OpenGL.GLU import *

from utils.constants import CAM_OFFSET_Y, CAM_OFFSET_Z, CAM_SMOOTH
from utils.math_utils import lerp


class Camera:

    def __init__(self):
        # Posição atual (suavizada) do alvo
        self.target_x = 0.0
        self.target_z = 0.0
        # Posição real atual (interpolada)
        self.current_x = 0.0
        self.current_z = 0.0

    def update(self, player_x, player_z, dt):

        self.target_x = player_x
        self.target_z = player_z

        # Interpolação suave (exponential decay)
        t = min(1.0, CAM_SMOOTH * dt)
        self.current_x = lerp(self.current_x, self.target_x, t)
        self.current_z = lerp(self.current_z, self.target_z, t)

    def apply(self):

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        eye_x = self.current_x
        eye_y = CAM_OFFSET_Y
        eye_z = self.current_z + CAM_OFFSET_Z

        look_x = self.current_x
        look_y = 0.5
        look_z = self.current_z

        gluLookAt(eye_x, eye_y, eye_z,
                  look_x, look_y, look_z,
                  0.0, 1.0, 0.0)

    def snap_to(self, x, z):
        self.current_x = x
        self.current_z = z
        self.target_x  = x
        self.target_z  = z
