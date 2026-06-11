"""
core/renderer.py - Sistema de renderização OpenGL.

Centraliza todas as chamadas de desenho: cubos, prismas,
iluminação, névoa e overlays 2D (HUD).
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

from utils.constants import *


class Renderer:
    """
    Responsável por toda a renderização do jogo.
    Oferece primitivas de alto nível (draw_box, draw_tree, etc.)
    e gerencia estado de iluminação / névoa.
    """

    def __init__(self, width, height):
        self.width  = width
        self.height = height

    # ──────────────────────────────────────────────────────────────────────────
    # Inicialização GL
    # ──────────────────────────────────────────────────────────────────────────

    def init(self):
        """Configura estado GL inicial."""
        glClearColor(*COLOR_SKY, 1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glShadeModel(GL_SMOOTH)

        # Iluminação
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION,  [4.0, 10.0, 5.0, 0.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,   [1.0, 0.95, 0.85, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,   [0.35, 0.35, 0.40, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR,  [0.3, 0.3, 0.3, 1.0])
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Névoa leve
        glEnable(GL_FOG)
        glFogfv(GL_FOG_COLOR, [*COLOR_FOG, 1.0])
        glFogi(GL_FOG_MODE, GL_LINEAR)
        glFogf(GL_FOG_START, 12.0)
        glFogf(GL_FOG_END,   28.0)

    def resize(self, width, height):
        """Atualiza viewport e projeção ao redimensionar."""
        if height == 0:
            height = 1
        self.width  = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    # ──────────────────────────────────────────────────────────────────────────
    # Primitivas geométricas
    # ──────────────────────────────────────────────────────────────────────────

    def draw_box(self, x, y, z, w, h, d, color):
        """
        Desenha um cubo/prisma em (x, y, z) com dimensões (w, h, d).
        x, y, z = posição do centro.
        """
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(w, h, d)
        self._unit_box()
        glPopMatrix()

    def draw_box_faces(self, x, y, z, w, h, d, colors):
        """
        Desenha prisma com cor diferente por face.
        colors = dict com chaves 'top','bottom','front','back','left','right'.
        """
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
        """Cubo unitário centrado na origem, com normais corretas."""
        glBegin(GL_QUADS)
        # Topo
        glNormal3f(0, 1, 0)
        glVertex3f( 0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5,-0.5)
        # Base
        glNormal3f(0,-1, 0)
        glVertex3f(-0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5,-0.5)
        # Frente
        glNormal3f(0, 0, 1)
        glVertex3f(-0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5, 0.5)
        glVertex3f( 0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5, 0.5)
        # Trás
        glNormal3f(0, 0,-1)
        glVertex3f( 0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5,-0.5)
        glVertex3f(-0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5,-0.5)
        # Esquerda
        glNormal3f(-1, 0, 0)
        glVertex3f(-0.5,-0.5,-0.5); glVertex3f(-0.5,-0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5); glVertex3f(-0.5, 0.5,-0.5)
        # Direita
        glNormal3f(1, 0, 0)
        glVertex3f( 0.5,-0.5, 0.5); glVertex3f( 0.5,-0.5,-0.5)
        glVertex3f( 0.5, 0.5,-0.5); glVertex3f( 0.5, 0.5, 0.5)
        glEnd()

    # ──────────────────────────────────────────────────────────────────────────
    # Objetos de cena
    # ──────────────────────────────────────────────────────────────────────────

    def draw_tree(self, x, z):
        """Árvore blocky simples: tronco + copa."""
        # Tronco
        self.draw_box(x, 0.4, z, 0.25, 0.8, 0.25, COLOR_TREE_TRUNK)
        # Copa (dois blocos para dar volume)
        self.draw_box(x, 1.15, z, 0.75, 0.7, 0.75, COLOR_TREE_TOP)
        self.draw_box(x, 1.65, z, 0.50, 0.5, 0.50, COLOR_TREE_TOP2)

    def draw_shadow(self, x, z, size=0.45):
        """Sombra circular plana sob o personagem."""
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0, 0, 0, 0.30)
        glBegin(GL_POLYGON)
        for i in range(16):
            ang = 2 * math.pi * i / 16
            glVertex3f(x + math.cos(ang) * size, 0.01, z + math.sin(ang) * size)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

    def draw_player(self, x, y, z, facing=1.0):
        """
        Personagem estilo pinto voxel.
        facing: +1 para frente, -1 para trás.
        """
        self.draw_shadow(x, z)

        # Corpo
        self.draw_box(x, y + 0.35, z, 0.55, 0.50, 0.55, COLOR_PLAYER_BODY)
        # Cabeça
        self.draw_box(x, y + 0.82, z, 0.40, 0.38, 0.40, COLOR_PLAYER_BODY)
        # Bico
        self.draw_box(x, y + 0.78, z + facing * 0.26,
                      0.18, 0.12, 0.15, COLOR_PLAYER_BEAK)
        # Olhos
        eye_off = 0.13
        self.draw_box(x - eye_off, y + 0.88, z + facing * 0.21,
                      0.08, 0.08, 0.06, COLOR_PLAYER_EYE)
        self.draw_box(x + eye_off, y + 0.88, z + facing * 0.21,
                      0.08, 0.08, 0.06, COLOR_PLAYER_EYE)
        # Asas
        self.draw_box(x - 0.35, y + 0.35, z, 0.15, 0.35, 0.45, COLOR_PLAYER_WING)
        self.draw_box(x + 0.35, y + 0.35, z, 0.15, 0.35, 0.45, COLOR_PLAYER_WING)

    def draw_car(self, x, z, direction, color_index, speed_factor=1.0):
        """
        Carro blocky.
        direction: +1 ou -1 (sentido X).
        """
        c = COLOR_CAR_BODY[color_index % len(COLOR_CAR_BODY)]
        # Chassi
        self.draw_box(x, 0.25, z, 0.75, 0.28, 1.0, c)
        # Cabine
        self.draw_box(x + direction * (-0.05), 0.55, z, 0.55, 0.30, 0.80, c)
        # Para-brisas
        self.draw_box(x + direction * 0.20, 0.56, z,
                      0.08, 0.22, 0.62, COLOR_WINDOW)
        # Rodas (4)
        wc = COLOR_WHEEL
        for wx in [-0.30, 0.30]:
            for wz in [-0.38, 0.38]:
                self.draw_box(x + wx, 0.13, z + wz, 0.15, 0.22, 0.22, wc)

    def draw_truck(self, x, z, direction, color_index):
        """Caminhão: cabine + carroceria."""
        c = COLOR_TRUCK_BODY[color_index % len(COLOR_TRUCK_BODY)]
        # Carroceria
        self.draw_box(x + direction * (-0.55), 0.35, z, 1.30, 0.55, 0.95, c)
        # Cabine
        self.draw_box(x + direction * 0.60, 0.30, z, 0.55, 0.50, 0.85, c)
        self.draw_box(x + direction * 0.68, 0.57, z, 0.42, 0.28, 0.70, c)
        # Para-brisas
        self.draw_box(x + direction * 0.80, 0.58, z,
                      0.08, 0.22, 0.60, COLOR_WINDOW)
        # Rodas (6)
        wc = COLOR_WHEEL
        for wx in [-0.80, -0.20, 0.60]:
            for wz in [-0.42, 0.42]:
                self.draw_box(x + wx, 0.14, z + wz, 0.15, 0.25, 0.25, wc)

    def draw_train(self, x, z, direction, wagon_index=0):
        """Vagão de trem."""
        c = COLOR_TRAIN
        # Corpo principal
        self.draw_box(x, 0.52, z, 1.80, 0.72, 0.95, c)
        # Frente (se primeiro vagão)
        if wagon_index == 0:
            self.draw_box(x + direction * 0.98, 0.55, z,
                          0.20, 0.65, 0.80, (0.65, 0.08, 0.08))
        # Janelas
        for wz in [-0.30, 0.0, 0.30]:
            self.draw_box(x, 0.68, z + wz, 1.60, 0.22, 0.18, COLOR_TRAIN_WINDOW)
        # Rodas / truques
        for wx in [-0.60, 0.60]:
            self.draw_box(x + wx, 0.16, z, 0.25, 0.25, 1.00, (0.25, 0.25, 0.28))

    def draw_log(self, x, z, length):
        """Tronco flutuante de comprimento `length` células."""
        w = length * CELL_SIZE - 0.1
        # Corpo
        self.draw_box(x, 0.12, z, w, 0.22, 0.82, COLOR_LOG)
        # Topos (ends)
        self.draw_box(x - w * 0.5 + 0.07, 0.12, z, 0.12, 0.24, 0.84, COLOR_LOG_END)
        self.draw_box(x + w * 0.5 - 0.07, 0.12, z, 0.12, 0.24, 0.84, COLOR_LOG_END)

    def draw_lilypad(self, x, z):
        """Vitória-régia: disco verde + flor."""
        self.draw_box(x, 0.06, z, LILYPAD_SIZE, 0.08, LILYPAD_SIZE, COLOR_LILYPAD)
        # Flor central
        self.draw_box(x, 0.14, z, 0.18, 0.12, 0.18, COLOR_FLOWER)

    def draw_eagle(self, x, y, z, wing_angle, scale=1.0):
        """
        Águia estilo blocky.
        wing_angle em radianos para animação de asas.
        """
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)

        wing_flap = math.sin(wing_angle) * 0.4

        # Corpo
        self.draw_box(0, 0, 0, 1.20, 0.55, 0.60, COLOR_EAGLE_BODY)
        # Cabeça branca
        self.draw_box(0.55, 0.25, 0, 0.45, 0.42, 0.42, COLOR_EAGLE_HEAD)
        # Bico
        self.draw_box(0.82, 0.12, 0, 0.22, 0.14, 0.18, COLOR_EAGLE_BEAK)
        # Olho
        self.draw_box(0.73, 0.30, 0.18, 0.08, 0.08, 0.06, (0.1, 0.1, 0.1))
        # Asa esquerda
        glPushMatrix()
        glTranslatef(0, 0, 0.35)
        glRotatef(-wing_flap * 30, 1, 0, 0)
        self.draw_box(0, 0.10 + wing_flap * 0.3, 0.60,
                      1.10, 0.14, 1.10, COLOR_EAGLE_BODY)
        glPopMatrix()
        # Asa direita
        glPushMatrix()
        glTranslatef(0, 0, -0.35)
        glRotatef(wing_flap * 30, 1, 0, 0)
        self.draw_box(0, 0.10 + wing_flap * 0.3, -0.60,
                      1.10, 0.14, 1.10, COLOR_EAGLE_BODY)
        glPopMatrix()
        # Cauda
        self.draw_box(-0.68, -0.05, 0, 0.35, 0.12, 0.50, COLOR_EAGLE_BODY)

        glPopMatrix()

    # ──────────────────────────────────────────────────────────────────────────
    # Terrenos / Lanes
    # ──────────────────────────────────────────────────────────────────────────

    def draw_grass_lane(self, row, is_dark=False):
        """Renderiza uma linha de grama."""
        c = COLOR_GRASS_DARK if is_dark else COLOR_GRASS_LIGHT
        z = float(row)
        for col in range(-HALF_GRID, HALF_GRID + 1):
            self.draw_box(float(col), -0.05, z, 1.0, 0.10, 1.0, c)

    def draw_road_lane(self, row):
        """Renderiza uma linha de estrada com faixas."""
        z = float(row)
        # Asfalto
        for col in range(-HALF_GRID, HALF_GRID + 1):
            self.draw_box(float(col), -0.05, z, 1.0, 0.10, 1.0, COLOR_ROAD)
        # Faixa tracejada central
        glDisable(GL_LIGHTING)
        glColor3f(*COLOR_ROAD_LINE)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        for col in range(-HALF_GRID, HALF_GRID + 1, 2):
            glVertex3f(float(col) - 0.3, 0.02, z)
            glVertex3f(float(col) + 0.3, 0.02, z)
        glEnd()
        glEnable(GL_LIGHTING)

    def draw_river_lane(self, row, anim_offset=0.0):
        """Renderiza uma linha de rio com efeito de onda."""
        z = float(row)
        for col in range(-HALF_GRID, HALF_GRID + 1):
            # Alterna cores de água para efeito visual
            t = (col + anim_offset) % 2.0
            c = COLOR_WATER if t < 1.0 else COLOR_WATER_DARK
            self.draw_box(float(col), -0.05, z, 1.0, 0.10, 1.0, c)

    def draw_rail_lane(self, row):
        """Renderiza uma linha de trilhos de trem."""
        z = float(row)
        # Lastro
        for col in range(-HALF_GRID, HALF_GRID + 1):
            self.draw_box(float(col), -0.05, z, 1.0, 0.10, 1.0, COLOR_RAIL_BED)
        # Dormentes
        glDisable(GL_LIGHTING)
        glColor3f(*COLOR_RAIL_TRACK)
        half = HALF_GRID + 0.5
        for offset in [-0.35, 0.35]:
            glBegin(GL_QUADS)
            glVertex3f(-half, 0.02, z + offset - 0.05)
            glVertex3f( half, 0.02, z + offset - 0.05)
            glVertex3f( half, 0.02, z + offset + 0.05)
            glVertex3f(-half, 0.02, z + offset + 0.05)
            glEnd()
        # Trilhos
        for col in range(-HALF_GRID, HALF_GRID + 1, 1):
            self.draw_box(float(col), 0.05, z, 0.8, 0.06, 0.12, COLOR_RAIL_TRACK)
        glEnable(GL_LIGHTING)

    # ──────────────────────────────────────────────────────────────────────────
    # HUD (2D overlay)
    # ──────────────────────────────────────────────────────────────────────────

    def begin_2d(self):
        """Entra no modo 2D para desenhar o HUD."""
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
        """Sai do modo 2D."""
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_FOG)

    def draw_text(self, x, y, text, color=(1, 1, 1), font=GLUT_BITMAP_HELVETICA_18):
        """Desenha texto 2D na posição (x, y) da tela."""
        glColor3f(*color)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def draw_rect_2d(self, x, y, w, h, color, alpha=1.0):
        """Retângulo sólido 2D (para painéis de HUD)."""
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

    def draw_warning_flash(self, row, flash_state, cam_z_offset=0):
        """
        Pisca a lane do trilho em amarelo/vermelho como aviso de trem.
        flash_state: valor 0..1 que pulsa.
        """
        if flash_state <= 0:
            return
        z = float(row)
        alpha = flash_state * 0.5
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        c = COLOR_WARNING if flash_state < 0.7 else COLOR_DANGER
        glColor4f(*c, alpha)
        half = HALF_GRID + 0.5
        glBegin(GL_QUADS)
        glVertex3f(-half, 0.05, z - 0.5)
        glVertex3f( half, 0.05, z - 0.5)
        glVertex3f( half, 0.05, z + 0.5)
        glVertex3f(-half, 0.05, z + 0.5)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
