"""
core/game.py - Orquestrador principal do jogo.

Gerencia os estados (menu, playing, game_over), o loop de update,
a renderização e o input do jogador.
"""

import time
import math

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from core.renderer     import Renderer
from core.camera       import Camera
from core.map_generator import MapGenerator
from core.collision    import CollisionManager
from core.score        import ScoreManager
from entities.player   import Player
from entities.eagle    import Eagle
from utils.constants   import *


# Estados do jogo
STATE_MENU     = 'menu'
STATE_PLAYING  = 'playing'
STATE_GAMEOVER = 'gameover'


class Game:
    """
    Classe central que coordena todos os subsistemas.
    """

    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.state  = STATE_MENU

        # Subsistemas
        self.renderer  = Renderer(width, height)
        self.camera    = Camera()
        self.map_gen   = MapGenerator()
        self.collision = CollisionManager()
        self.score_mgr = ScoreManager()

        # Entidades
        self.player = Player()
        self.eagle  = Eagle()

        # Controle de tempo
        self._last_time = time.time()
        self.dt         = 0.0

        # Efeitos de game over
        self._gameover_timer = 0.0
        self._death_cause    = None

        # Timer de inatividade do jogador (para a águia)
        self._idle_timer = 0.0
        self._last_row   = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Inicialização
    # ──────────────────────────────────────────────────────────────────────────

    def init_gl(self):
        """Inicializa OpenGL e carrega o estado inicial."""
        self.renderer.init()
        self.renderer.resize(self.width, self.height)

    def _start_game(self):
        """Inicia ou reinicia uma partida."""
        self.state = STATE_PLAYING
        self.player.reset()
        self.eagle.reset()
        self.score_mgr.reset()
        self.map_gen.reset()
        self.camera.snap_to(0.0, 0.0)
        self._gameover_timer = 0.0
        self._death_cause    = None
        self._idle_timer     = 0.0
        self._last_row       = 0

    # ──────────────────────────────────────────────────────────────────────────
    # Loop principal
    # ──────────────────────────────────────────────────────────────────────────

    def update(self):
        """Chamado a cada frame pelo timer do GLUT."""
        now = time.time()
        self.dt = min(now - self._last_time, 0.05)  # cap em 50ms
        self._last_time = now

        self.score_mgr.update_fps()

        if self.state == STATE_PLAYING:
            self._update_playing()
        elif self.state == STATE_GAMEOVER:
            self._gameover_timer += self.dt

    def _update_playing(self):
        dt = self.dt
        difficulty = self.score_mgr.get_difficulty()
        speed_factor = difficulty

        # Atualiza lanes
        self.map_gen.update(self.player.row, difficulty)
        self.map_gen.update_lanes(dt, speed_factor)

        # Transporte por tronco (antes de mover o jogador)
        self.collision.handle_river_transport(
            self.player, self.map_gen, dt, speed_factor)

        # Atualiza jogador
        self.player.update(dt)

        # Pontuação
        self.score_mgr.update_row(self.player.row)

        # Timer de inatividade
        if self.player.row > self._last_row:
            self._last_row   = self.player.row
            self._idle_timer = 0.0
            self.eagle.reset_idle_timer()
        else:
            self._idle_timer += dt

        # Águia
        eagle_threshold = self.score_mgr.get_eagle_idle_time()
        self.eagle.update(dt, self.player.x, self.player.z, eagle_threshold)

        if self.eagle.captured:
            self._trigger_death("eagle")
            return

        # Colisões
        is_dead, cause = self.collision.check_death(self.player, self.map_gen)
        if is_dead:
            self._trigger_death(cause)
            return

        # Câmera
        self.camera.update(self.player.x, self.player.z, dt)

    def _trigger_death(self, cause):
        """Aciona a tela de game over."""
        self.player.alive = False
        self._death_cause  = cause
        self.state         = STATE_GAMEOVER
        self._gameover_timer = 0.0

    # ──────────────────────────────────────────────────────────────────────────
    # Renderização
    # ──────────────────────────────────────────────────────────────────────────

    def render(self):
        """Callback de render do GLUT."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.state == STATE_MENU:
            self._render_menu()
        elif self.state == STATE_PLAYING:
            self._render_game()
            self._render_hud()
        elif self.state == STATE_GAMEOVER:
            self._render_game()
            self._render_gameover()

        glutSwapBuffers()

    def _render_game(self):
        """Renderiza a cena 3D completa."""
        self.camera.apply()

        player_row = self.player.row
        r = self.renderer

        # Desenha lanes visíveis
        for lane in self.map_gen.get_visible_lanes(player_row):
            ltype = lane.lane_type
            z     = lane.z_world

            if ltype == LANE_GRASS:
                r.draw_grass_lane(z, lane.is_dark)
                # Árvores
                for tx in lane.trees:
                    r.draw_tree(tx, z)

            elif ltype == LANE_ROAD:
                r.draw_road_lane(z)
                # Veículos
                for v in lane.vehicles:
                    if hasattr(v, 'WIDTH') and v.WIDTH > 1.5:
                        r.draw_truck(v.x, v.z, v.direction, v.color_index)
                    else:
                        r.draw_car(v.x, v.z, v.direction, v.color_index)

            elif ltype == LANE_RIVER:
                r.draw_river_lane(z, lane.anim_timer)
                # Plataformas
                for p in lane.platforms:
                    if hasattr(p, 'length'):
                        r.draw_log(p.x, p.z, p.length)
                    else:
                        r.draw_lilypad(p.x, p.z)

            elif ltype == LANE_RAIL:
                r.draw_rail_lane(z)
                # Aviso de trem
                r.draw_warning_flash(z, lane.warning_flash)
                # Trem
                if lane.train.state == 'running':
                    for i, wx in enumerate(lane.train.get_wagon_positions()):
                        r.draw_train(wx, lane.train.z,
                                     lane.train.direction, i)

        # Jogador
        r.draw_player(self.player.x, self.player.y, self.player.z,
                      self.player.facing)

        # Águia
        if self.eagle.visible:
            r.draw_eagle(
                self.eagle.x, self.eagle.y, self.eagle.z,
                self.eagle.wing_angle, self.eagle.scale
            )

    def _render_hud(self):
        """Renderiza o HUD (pontuação, FPS, etc.)."""
        r = self.renderer
        r.begin_2d()

        # Painel superior esquerdo
        r.draw_rect_2d(8, self.height - 90, 200, 82, (0, 0, 0), 0.45)
        r.draw_text(16, self.height - 22,
                    f"PONTOS: {self.score_mgr.score}", (1, 1, 0))
        r.draw_text(16, self.height - 46,
                    f"RECORDE: {self.score_mgr.high_score}", (1, 0.8, 0.2))
        r.draw_text(16, self.height - 70,
                    f"FPS: {self.score_mgr.fps:.0f}", (0.7, 1, 0.7))

        # Aviso de águia
        if self.eagle.warning_level > 0.1:
            alpha = self.eagle.warning_level
            r.draw_rect_2d(0, self.height - 30,
                           self.width, 30, (0.8, 0.1, 0.1), alpha * 0.6)
            r.draw_text(self.width // 2 - 80, self.height - 10,
                        "⚠ AGUIA SE APROXIMA!", (1, 1, 0.2),
                        GLUT_BITMAP_HELVETICA_18)

        r.end_2d()

    def _render_menu(self):
        """Tela inicial."""
        # Fundo simples
        glClearColor(0.2, 0.35, 0.55, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        r = self.renderer
        r.begin_2d()

        cx = self.width // 2
        cy = self.height // 2

        # Painel central
        r.draw_rect_2d(cx - 220, cy - 160, 440, 320, (0, 0, 0), 0.65)

        r.draw_text(cx - 100, cy + 120,
                    "CRUZARUA", (1, 0.9, 0.1), GLUT_BITMAP_TIMES_ROMAN_24)
        r.draw_text(cx - 140, cy + 70,
                    "Inspirado em Crossy Road", (0.9, 0.9, 0.9))

        r.draw_text(cx - 130, cy + 20,  "W  - Avancar para frente", (0.7, 1, 0.7))
        r.draw_text(cx - 130, cy - 5,   "S  - Recuar",              (0.7, 1, 0.7))
        r.draw_text(cx - 130, cy - 30,  "A  - Mover para esquerda", (0.7, 1, 0.7))
        r.draw_text(cx - 130, cy - 55,  "D  - Mover para direita",  (0.7, 1, 0.7))
        r.draw_text(cx - 130, cy - 80,  "ESC - Sair",               (1, 0.5, 0.5))

        # Pisca "Pressione D"
        flash = abs(math.sin(time.time() * 2.5))
        r.draw_text(cx - 110, cy - 130,
                    "Pressione W para comecar!",
                    (flash, flash, 0.2), GLUT_BITMAP_HELVETICA_18)

        r.end_2d()

    def _render_gameover(self):
        """Overlay de game over."""
        r = self.renderer
        r.begin_2d()

        cx = self.width // 2
        cy = self.height // 2

        # Overlay escuro
        r.draw_rect_2d(0, 0, self.width, self.height, (0, 0, 0), 0.55)

        # Painel
        r.draw_rect_2d(cx - 200, cy - 140, 400, 280, (0.1, 0, 0), 0.80)

        r.draw_text(cx - 90, cy + 110,
                    "GAME OVER", (1, 0.2, 0.1), GLUT_BITMAP_TIMES_ROMAN_24)

        # Causa da morte
        causes = {
            "vehicle": "Atropelado!",
            "train":   "Esmagado pelo trem!",
            "water":   "Afogado no rio!",
            "eagle":   "Capturado pela aguia!",
        }
        cause_text = causes.get(self._death_cause, "Boa tentativa!")
        r.draw_text(cx - 90, cy + 70, cause_text, (1, 0.8, 0.3))

        r.draw_text(cx - 70, cy + 30,
                    f"Pontos: {self.score_mgr.score}", (1, 1, 0.2))
        r.draw_text(cx - 80, cy + 0,
                    f"Recorde: {self.score_mgr.high_score}", (1, 0.7, 0.1))

        # Pisca "Pressione R"
        flash = abs(math.sin(self._gameover_timer * 3.0))
        r.draw_text(cx - 110, cy - 60,
                    "Pressione R para reiniciar",
                    (flash, flash, 0.2), GLUT_BITMAP_HELVETICA_18)

        r.draw_text(cx - 70, cy - 100,
                    "ESC para sair", (0.7, 0.4, 0.4))

        r.end_2d()

    # ──────────────────────────────────────────────────────────────────────────
    # Input
    # ──────────────────────────────────────────────────────────────────────────

    def handle_key(self, key, x, y):
        """Teclas normais (bytes)."""
        # ESC
        if key == b'\x1b':
            import sys
            sys.exit(0)

        # Reiniciar
        if key in (b'r', b'R'):
            if self.state in (STATE_GAMEOVER, STATE_MENU):
                self._start_game()

        if self.state == STATE_MENU:
            if key in (b'w', b'W'):
                self._start_game()
            return

        if self.state != STATE_PLAYING:
            return

        # Movimentos
        if key in (b'w', b'W'):
            # Avançar (z diminui = vai para frente)
            if not self.collision.check_tree_block(
                    self.player, self.map_gen,
                    self.player.grid_x, self.player.grid_z - 1):
                self.player.request_move(0, -1)
                self.eagle.reset_idle_timer()
                self._idle_timer = 0.0

        elif key in (b's', b'S'):
            # Recuar
            self.player.request_move(0, 1)
            self.eagle.reset_idle_timer()
            self._idle_timer = 0.0

        elif key in (b'a', b'A'):
            # Mover para esquerda (X diminui)
            if not self.collision.check_tree_block(
                    self.player, self.map_gen,
                    self.player.grid_x - 1, self.player.grid_z):
                self.player.request_move(-1, 0)
                self.eagle.reset_idle_timer()
                self._idle_timer = 0.0

        elif key in (b'd', b'D'):
            # Mover para direita (X aumenta)
            if not self.collision.check_tree_block(
                    self.player, self.map_gen,
                    self.player.grid_x + 1, self.player.grid_z):
                self.player.request_move(1, 0)
                self.eagle.reset_idle_timer()
                self._idle_timer = 0.0

    def handle_special_key(self, key, x, y):
        """Teclas especiais (setas, F-keys)."""
        pass  # pode mapear setas aqui se quiser

    def reshape(self, width, height):
        """Callback de redimensionamento."""
        self.width  = width
        self.height = height
        self.renderer.resize(width, height)