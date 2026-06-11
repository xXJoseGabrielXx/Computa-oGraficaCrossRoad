"""
core/score.py - Gerenciamento de pontuação e recordes.
"""

import time


class ScoreManager:
    """
    Mantém a pontuação atual, o recorde da sessão e estatísticas.
    A pontuação aumenta conforme o jogador avança para novas linhas.
    """

    def __init__(self):
        self.score       = 0       # pontuação atual
        self.high_score  = 0       # recorde da sessão
        self.max_row     = 0       # linha mais avançada atingida
        self.start_time  = time.time()
        self.frame_count = 0
        self.fps         = 0.0
        self._fps_timer  = time.time()
        self._fps_frames = 0

    def reset(self):
        """Reinicia para uma nova partida (mantém high_score)."""
        self.score      = 0
        self.max_row    = 0
        self.start_time = time.time()
        self.frame_count = 0

    def update_row(self, row):
        """
        Atualiza a pontuação se o jogador chegou a uma nova linha recorde.
        `row` é a linha atual do jogador (aumenta ao avançar).
        """
        if row > self.max_row:
            self.score   += row - self.max_row
            self.max_row  = row
            if self.score > self.high_score:
                self.high_score = self.score

    def update_fps(self):
        """Calcula FPS médio nos últimos frames."""
        self._fps_frames += 1
        now = time.time()
        elapsed = now - self._fps_timer
        if elapsed >= 1.0:
            self.fps = self._fps_frames / elapsed
            self._fps_frames = 0
            self._fps_timer  = now

    def get_difficulty(self):
        """
        Retorna fator de dificuldade baseado na pontuação.
        Vai de 1.0 (início) a ~3.0 (pontuação alta).
        """
        from utils.constants import DIFF_SPEED_SCALE
        return 1.0 + self.score * DIFF_SPEED_SCALE

    def get_eagle_idle_time(self):
        """Tempo de espera antes da águia aparecer (diminui com a pontuação)."""
        from utils.constants import EAGLE_IDLE_TIME, DIFF_EAGLE_SCALE
        t = EAGLE_IDLE_TIME - self.score * DIFF_EAGLE_SCALE
        return max(2.0, t)
