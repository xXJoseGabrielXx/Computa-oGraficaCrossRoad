"""
core/renderer.py - Sistema de renderização OpenGL.
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

from utils.constants import *


class Renderer:

    def __init__(self, width, height):
        self.width  = width
        self.height = height

    # ─── Inicialização ────────────────────────────────────────────────────────

    def init(self):
        glClearColor(*COLOR_SKY, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Iluminação — usada APENAS em objetos 3D (veículos, árvores, player)
        # O terreno é desenhado com glDisable(GL_LIGHTING) para evitar estouro.
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [4.0, 10.0, 5.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.70, 0.68, 0.60, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.0,  0.0,  0.0,  1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0,  0.0,  0.0,  1.0])
        # Ambient global: ilumina faces em sombra sem estouro
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.42, 0.42, 0.46, 1.0])
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

        # Névoa
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [*COLOR_FOG, 1.0])
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 14.0)
        glFogf(GL_FOG_END,   30.0)

    def resize(self, width, height):
        if height == 0:
            height = 1
        self.width  = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(42.0, width / height, 0.1, 120.0)
        glMatrixMode(GL_MODELVIEW)

    # ─── Primitivas ───────────────────────────────────────────────────────────

    def draw_box(self, x, y, z, w, h, d, color):
        """Cubo/prisma centrado em (x,y,z) com dimensões (w,h,d). Usa iluminação."""
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(w, h, d)
        self._unit_box()
        glPopMatrix()

    def draw_box_faces(self, x, y, z, w, h, d, colors):
        hw, hh, hd = w * 0.5, h * 0.5, d * 0.5
        glPushMatrix()
        glTranslatef(x, y, z)
        faces = {
            'top':    ([( hw, hh, hd),(-hw, hh, hd),(-hw, hh,-hd),( hw, hh,-hd)], ( 0, 1, 0)),
            'bottom': ([(-hw,-hh, hd),( hw,-hh, hd),( hw,-hh,-hd),(-hw,-hh,-hd)], ( 0,-1, 0)),
            'front':  ([(-hw,-hh, hd),( hw,-hh, hd),( hw, hh, hd),(-hw, hh, hd)], ( 0, 0, 1)),
            'back':   ([( hw,-hh,-hd),(-hw,-hh,-hd),(-hw, hh,-hd),( hw, hh,-hd)], ( 0, 0,-1)),
            'left':   ([(-hw,-hh,-hd),(-hw,-hh, hd),(-hw, hh, hd),(-hw, hh,-hd)], (-1, 0, 0)),
            'right':  ([( hw,-hh, hd),( hw,-hh,-hd),( hw, hh,-hd),( hw, hh, hd)], ( 1, 0, 0)),
        }
        glBegin(GL_QUADS)
        for key, (verts, normal) in faces.items():
            c = colors.get(key, colors.get('top', (1, 1, 1)))
            glColor3f(*c)
            glNormal3f(*normal)
            for v in verts:
                glVertex3f(*v)
        glEnd()
        glPopMatrix()

    def _unit_box(self):
        """Cubo unitário centrado na origem com normais corretas."""
        glBegin(GL_QUADS)
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)

        glNormal3f(0, 0,-1)
        glVertex3f( 0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5,-0.5)

        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5,-0.5)

        glNormal3f(1, 0, 0)
        glVertex3f( 0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5, 0.5)

        glNormal3f(0, 1, 0)
        glVertex3f(-0.5, 0.5, 0.5); glVertex3f( 0.5, 0.5, 0.5)
        glVertex3f( 0.5, 0.5,-0.5); glVertex3f(-0.5, 0.5,-0.5)

        glNormal3f(0,-1, 0)
        glVertex3f(-0.5,-0.5,-0.5); glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5,-0.5, 0.5); glVertex3f(-0.5,-0.5, 0.5)
        glEnd()

    # ─── Objetos de cena ─────────────────────────────────────────────────────

    def draw_tree(self, x, z):
        self.draw_box(x, 0.40, z, 0.26, 0.80, 0.26, COLOR_TREE_TRUNK)
        self.draw_box(x, 1.15, z, 0.78, 0.72, 0.78, COLOR_TREE_TOP)
        self.draw_box(x, 1.68, z, 0.52, 0.52, 0.52, COLOR_TREE_TOP2)

    def draw_shadow(self, x, z, size=0.42):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.0, 0.0, 0.0, 0.28)
        glBegin(GL_POLYGON)
        for i in range(20):
            ang = 2.0 * math.pi * i / 20
            glVertex3f(x + math.cos(ang) * size, 0.005,
                       z + math.sin(ang) * size * 0.6)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw_player(self, x, y, z, facing=1.0):
        self.draw_shadow(x, z)
        fz = -facing  # facing=+1 avança em -Z

        self.draw_box(x,          y + 0.35, z,           0.55, 0.50, 0.55, COLOR_PLAYER_BODY)
        self.draw_box(x,          y + 0.82, z,           0.40, 0.38, 0.40, COLOR_PLAYER_BODY)
        self.draw_box(x,          y + 0.78, z+fz*0.26,   0.18, 0.12, 0.15, COLOR_PLAYER_BEAK)
        self.draw_box(x - 0.13,   y + 0.88, z+fz*0.21,  0.08, 0.08, 0.06, COLOR_PLAYER_EYE)
        self.draw_box(x + 0.13,   y + 0.88, z+fz*0.21,  0.08, 0.08, 0.06, COLOR_PLAYER_EYE)
        self.draw_box(x - 0.35,   y + 0.38, z,           0.15, 0.35, 0.46, COLOR_PLAYER_WING)
        self.draw_box(x + 0.35,   y + 0.38, z,           0.15, 0.35, 0.46, COLOR_PLAYER_WING)

    def draw_car(self, x, z, direction, color_index):
        c = COLOR_CAR_BODY[color_index % len(COLOR_CAR_BODY)]
        d = direction
        self.draw_box(x,            0.18, z,  0.78, 0.24, 0.92, c)
        self.draw_box(x+d*(-0.04),  0.46, z,  0.54, 0.28, 0.76, c)
        self.draw_box(x+d*0.22,     0.48, z,  0.07, 0.20, 0.58, COLOR_WINDOW)
        win_rear = (COLOR_WINDOW[0]*0.7, COLOR_WINDOW[1]*0.7, COLOR_WINDOW[2]*0.8)
        self.draw_box(x+d*(-0.22),  0.48, z,  0.07, 0.18, 0.56, win_rear)
        wc = COLOR_WHEEL
        for wx_off in [-0.32, 0.32]:
            for wz_off in [-0.35, 0.35]:
                self.draw_box(x+wx_off, 0.14, z+wz_off, 0.16, 0.24, 0.24, wc)

    def draw_truck(self, x, z, direction, color_index):
        c = COLOR_TRUCK_BODY[color_index % len(COLOR_TRUCK_BODY)]
        d = direction
        self.draw_box(x+d*(-0.52), 0.36, z, 1.28, 0.58, 0.92, c)
        roof_c = (c[0]*0.75, c[1]*0.75, c[2]*0.75)
        self.draw_box(x+d*(-0.52), 0.68, z, 1.28, 0.06, 0.94, roof_c)
        self.draw_box(x+d*0.58,    0.30, z, 0.56, 0.52, 0.84, c)
        self.draw_box(x+d*0.60,    0.60, z, 0.44, 0.28, 0.68, c)
        self.draw_box(x+d*0.82,    0.60, z, 0.07, 0.22, 0.58, COLOR_WINDOW)
        wc = COLOR_WHEEL
        for wx_off in [-0.78, -0.18, 0.58]:
            for wz_off in [-0.40, 0.40]:
                self.draw_box(x+wx_off, 0.15, z+wz_off, 0.16, 0.27, 0.27, wc)

    def draw_train(self, x, z, direction, wagon_index=0):
        c = COLOR_TRAIN
        d = direction
        self.draw_box(x, 0.50, z, 1.78, 0.70, 0.92, c)
        roof_c = (c[0]*0.80, c[1]*0.08, c[2]*0.08)
        self.draw_box(x, 0.88, z, 1.78, 0.06, 0.94, roof_c)
        if wagon_index == 0:
            self.draw_box(x+d*0.96, 0.54, z, 0.18, 0.62, 0.78, (0.60, 0.06, 0.06))
            self.draw_box(x+d*1.05, 0.62, z, 0.06, 0.14, 0.24, (1.0, 0.95, 0.70))
        for wz_off in [-0.28, 0.0, 0.28]:
            self.draw_box(x, 0.62, z+wz_off, 1.58, 0.20, 0.16, COLOR_TRAIN_WINDOW)
        for wx_off in [-0.55, 0.55]:
            self.draw_box(x+wx_off, 0.16, z, 0.28, 0.26, 0.98, (0.22, 0.22, 0.25))
            for wz_off in [-0.32, 0.32]:
                self.draw_box(x+wx_off, 0.10, z+wz_off, 0.26, 0.18, 0.20, (0.15, 0.15, 0.16))

    def draw_log(self, x, z, length):
        w = length * CELL_SIZE - 0.10
        self.draw_box(x, 0.12, z, w, 0.22, 0.82, COLOR_LOG)
        self.draw_box(x - w*0.5 + 0.06, 0.12, z, 0.11, 0.24, 0.84, COLOR_LOG_END)
        self.draw_box(x + w*0.5 - 0.06, 0.12, z, 0.11, 0.24, 0.84, COLOR_LOG_END)

    def draw_lilypad(self, x, z):
        self.draw_box(x, 0.06, z, LILYPAD_SIZE, 0.07, LILYPAD_SIZE, COLOR_LILYPAD)
        self.draw_box(x, 0.13, z, 0.20, 0.11, 0.20, COLOR_FLOWER)

    def draw_eagle(self, x, y, z, wing_angle, scale=1.0):
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        flap = math.sin(wing_angle) * 0.45
        self.draw_box(0, 0, 0, 1.20, 0.54, 0.58, COLOR_EAGLE_BODY)
        self.draw_box(0.54, 0.26, 0, 0.44, 0.40, 0.40, COLOR_EAGLE_HEAD)
        self.draw_box(0.80, 0.14, 0, 0.18, 0.12, 0.16, COLOR_EAGLE_BEAK)
        self.draw_box(0.90, 0.06, 0, 0.10, 0.10, 0.12, COLOR_EAGLE_BEAK)
        self.draw_box(0.72, 0.32, 0.17, 0.07, 0.07, 0.05, (0.05, 0.05, 0.05))
        self.draw_box(-0.70, -0.06, 0, 0.36, 0.11, 0.48, COLOR_EAGLE_BODY)
        glPushMatrix()
        glTranslatef(0, 0, 0.30)
        glRotatef(-flap * 35, 1, 0, 0)
        self.draw_box(0, 0.12 + flap*0.25, 0.62, 1.10, 0.13, 1.05, COLOR_EAGLE_BODY)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, -0.30)
        glRotatef(flap * 35, 1, 0, 0)
        self.draw_box(0, 0.12 + flap*0.25, -0.62, 1.10, 0.13, 1.05, COLOR_EAGLE_BODY)
        glPopMatrix()
        glPopMatrix()

    # ─── Terrenos — SEM iluminação (flat color, evita estouro) ───────────────

    def _flat_quad(self, z, x_min, x_max, z_min, z_max, color):
        """
        Quad plano do chão sem iluminação.
        y = -0.02 para ficar abaixo dos objetos e evitar z-fighting.
        Ordem anti-horária vista de cima => normal +Y => passa no GL_BACK cull.
        """
        glColor3f(*color)
        glBegin(GL_QUADS)
        glVertex3f(x_min, -0.02, z_max)
        glVertex3f(x_max, -0.02, z_max)
        glVertex3f(x_max, -0.02, z_min)
        glVertex3f(x_min, -0.02, z_min)
        glEnd()

    def draw_grass_lane(self, z_world, is_dark=False):
        c    = COLOR_GRASS_DARK if is_dark else COLOR_GRASS_LIGHT
        z    = float(z_world)
        half = HALF_GRID + 0.5
        glDisable(GL_LIGHTING)
        self._flat_quad(z, -half, half, z - 0.5, z + 0.5, c)
        glEnable(GL_LIGHTING)

    def draw_road_lane(self, z_world):
        z    = float(z_world)
        half = HALF_GRID + 0.5
        glDisable(GL_LIGHTING)
        self._flat_quad(z, -half, half, z - 0.5, z + 0.5, COLOR_ROAD)
        # Faixas tracejadas
        glColor3f(*COLOR_ROAD_LINE)
        glLineWidth(2.5)
        glBegin(GL_LINES)
        for col in range(-HALF_GRID, HALF_GRID + 1, 2):
            glVertex3f(float(col) - 0.28, 0.0, z)
            glVertex3f(float(col) + 0.28, 0.0, z)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_river_lane(self, z_world, anim_offset=0.0):
        z = float(z_world)
        glDisable(GL_LIGHTING)
        for col in range(-HALF_GRID, HALF_GRID + 1):
            t  = (col + anim_offset) % 2.0
            c  = COLOR_WATER if t < 1.0 else COLOR_WATER_DARK
            cx = float(col)
            self._flat_quad(z, cx - 0.5, cx + 0.5, z - 0.5, z + 0.5, c)
        glEnable(GL_LIGHTING)

    def draw_rail_lane(self, z_world):
        z    = float(z_world)
        half = HALF_GRID + 0.5
        glDisable(GL_LIGHTING)
        # Lastro
        self._flat_quad(z, -half, half, z - 0.5, z + 0.5, COLOR_RAIL_BED)
        # Dormentes
        glColor3f(0.36, 0.26, 0.16)
        for col in range(-HALF_GRID, HALF_GRID + 1):
            cx = float(col)
            glBegin(GL_QUADS)
            glVertex3f(cx - 0.40, -0.01, z + 0.44)
            glVertex3f(cx + 0.40, -0.01, z + 0.44)
            glVertex3f(cx + 0.40, -0.01, z - 0.44)
            glVertex3f(cx - 0.40, -0.01, z - 0.44)
            glEnd()
        # Trilhos
        glColor3f(*COLOR_RAIL_TRACK)
        for z_off in [-0.28, 0.28]:
            glBegin(GL_QUADS)
            glVertex3f(-half, 0.005, z + z_off + 0.05)
            glVertex3f( half, 0.005, z + z_off + 0.05)
            glVertex3f( half, 0.005, z + z_off - 0.05)
            glVertex3f(-half, 0.005, z + z_off - 0.05)
            glEnd()
        glEnable(GL_LIGHTING)

    # ─── HUD (2D overlay) ─────────────────────────────────────────────────────

    def begin_2d(self):
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def end_2d(self):
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_FOG)

    def draw_text(self, x, y, text, color=(1,1,1), font=GLUT_BITMAP_HELVETICA_18):
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def draw_rect_2d(self, x, y, w, h, color, alpha=1.0):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*color, alpha)
        glBegin(GL_QUADS)
        glVertex2f(x,     y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x,     y + h)
        glEnd()
        glDisable(GL_BLEND)

    def draw_warning_flash(self, z_world, flash_state):
        if flash_state <= 0.0:
            return
        z    = float(z_world)
        half = HALF_GRID + 0.5
        c    = COLOR_WARNING if flash_state < 0.65 else COLOR_DANGER
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(*c, flash_state * 0.55)
        glBegin(GL_QUADS)
        glVertex3f(-half, 0.01, z + 0.50)
        glVertex3f( half, 0.01, z + 0.50)
        glVertex3f( half, 0.01, z - 0.50)
        glVertex3f(-half, 0.01, z - 0.50)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
