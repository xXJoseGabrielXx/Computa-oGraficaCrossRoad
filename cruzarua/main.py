"""
CruzaRua - Jogo inspirado em Crossy Road
Desenvolvido com Python 3, PyOpenGL, FreeGLUT e NumPy

Ponto de entrada principal do jogo.
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from core.game import Game

# Instância global do jogo (necessária para callbacks do GLUT)
game = None


def display_callback():
    global game
    if game:
        game.render()


def reshape_callback(width, height):
    global game
    if game:
        game.reshape(width, height)


def keyboard_callback(key, x, y):
    global game
    if game:
        game.handle_key(key, x, y)


def special_key_callback(key, x, y):
    global game
    if game:
        game.handle_special_key(key, x, y)


def timer_callback(value):
    global game
    if game:
        game.update()
        glutPostRedisplay()
        glutTimerFunc(16, timer_callback, 0)


def main():
    global game

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(900, 700)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"CruzaRua - Crossy Road Clone")

    game = Game(900, 700)
    game.init_gl()

    glutDisplayFunc(display_callback)
    glutReshapeFunc(reshape_callback)
    glutKeyboardFunc(keyboard_callback)
    glutSpecialFunc(special_key_callback)
    glutTimerFunc(16, timer_callback, 0)

    print("=== CruzaRua iniciado ===")
    print("Controles:")
    print("  W   - Avançar (frente)")
    print("  S   - Recuar")
    print("  A   - Mover para esquerda")
    print("  D   - Mover para direita")
    print("  R   - Reiniciar (após Game Over ou Menu)")
    print("  ESC - Sair")

    glutMainLoop()


if __name__ == "__main__":
    main()