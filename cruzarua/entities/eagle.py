"""
entities/eagle.py - Águia que captura o jogador se ficar parado.

Estados:
  idle      - não visível, aguardando timer
  appearing - aparece ao fundo e se aproxima
  striking  - mergulha para capturar
  captured  - segurou o jogador (game over)
"""

import math
from utils.math_utils import lerp, smooth_step


class Eagle:
    """
    Águia gigante que aparece quando o jogador fica muito tempo parado.
    Animação em 3 fases: idle → appearing → striking → captured.
    """

    def __init__(self):
        # Estado
        self.state     = 'idle'
        self.idle_timer = 0.0
        self.phase_timer = 0.0

        # Posição visual
        self.x = 0.0
        self.y = 8.0
        self.z = 0.0

        # Posição alvo (segue o jogador)
        self.target_x = 0.0
        self.target_z = 0.0

        # Animação de asas
        self.wing_angle = 0.0

        # Escala (cresce ao se aproximar)
        self.scale = 0.5

        # Flag de morte
        self.captured = False

    def reset(self):
        """Reinicia a águia."""
        self.state       = 'idle'
        self.idle_timer  = 0.0
        self.phase_timer = 0.0
        self.captured    = False
        self.scale       = 0.5

    def update(self, dt, player_x, player_z, idle_time_threshold):
        """
        Atualiza a águia.
        idle_time_threshold: segundos antes de aparecer.
        """
        self.wing_angle += dt * 5.0  # animação contínua das asas
        self.target_x = player_x
        self.target_z = player_z

        if self.state == 'idle':
            self.idle_timer += dt
            if self.idle_timer >= idle_time_threshold:
                self._start_appearing(player_x, player_z)

        elif self.state == 'appearing':
            self._update_appearing(dt, player_x, player_z)

        elif self.state == 'striking':
            self._update_striking(dt, player_x, player_z)

    def reset_idle_timer(self):
        """Chamado quando o jogador se move — reseta o timer da águia."""
        if self.state == 'idle':
            self.idle_timer = 0.0
        elif self.state == 'appearing':
            # Recua a águia
            self.state      = 'idle'
            self.idle_timer = 0.0

    def _start_appearing(self, px, pz):
        """Inicia a fase de aproximação."""
        self.state       = 'appearing'
        self.phase_timer = 0.0
        # Começa bem atrás e acima
        self.x = px
        self.y = 12.0
        self.z = pz + 15.0

    def _update_appearing(self, dt, px, pz):
        from utils.constants import EAGLE_APPROACH_TIME
        self.phase_timer += dt
        t = min(1.0, self.phase_timer / EAGLE_APPROACH_TIME)
        st = smooth_step(t)

        # Aproxima-se gradualmente
        self.x = lerp(self.x, px, dt * 0.8)
        self.z = lerp(self.z, pz + 4.0, st * dt * 3.0)
        self.y = lerp(12.0, 5.5, st)
        self.scale = lerp(0.5, 1.2, st)

        if t >= 1.0:
            self.state       = 'striking'
            self.phase_timer = 0.0

    def _update_striking(self, dt, px, pz):
        from utils.constants import EAGLE_STRIKE_TIME
        self.phase_timer += dt
        t = min(1.0, self.phase_timer / EAGLE_STRIKE_TIME)
        st = smooth_step(t)

        # Mergulha direto no jogador
        self.x = lerp(self.x, px, dt * 4.0)
        self.z = lerp(self.z, pz, dt * 4.0)
        self.y = lerp(5.5, 0.8, st)
        self.scale = lerp(1.2, 1.5, st)

        if t >= 1.0:
            self.captured = True

    @property
    def visible(self):
        """True quando a águia deve ser renderizada."""
        return self.state in ('appearing', 'striking')

    @property
    def warning_level(self):
        """
        0 = não visível, 1 = máximo perigo.
        Usado para efeito visual de aviso.
        """
        if self.state == 'idle':
            return 0.0
        elif self.state == 'appearing':
            from utils.constants import EAGLE_APPROACH_TIME
            return min(1.0, self.phase_timer / EAGLE_APPROACH_TIME) * 0.6
        elif self.state == 'striking':
            return 0.6 + 0.4 * min(1.0, self.phase_timer)
        return 0.0
