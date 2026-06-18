# CruzaRua 🐣

Jogo 3D inspirado em Crossy Road, desenvolvido com Python 3, PyOpenGL, FreeGLUT e NumPy.

---

## Estrutura de Pastas

```
cruzarua/
├── main.py                  # Ponto de entrada, callbacks GLUT
├── requirements.txt
│
├── core/                    # Lógica central do jogo
│   ├── game.py              # Orquestrador: estados, loop, input
│   ├── renderer.py          # Todas as chamadas OpenGL (cubos, HUD, etc.)
│   ├── camera.py            # Câmera isométrica com suavização
│   ├── map_generator.py     # Geração procedural infinita de lanes
│   ├── collision.py         # Detecção AABB centralizada
│   └── score.py             # Pontuação, recorde, dificuldade
│
├── entities/                # Entidades do jogo
│   ├── player.py            # Personagem (grid-based + animação)
│   ├── lane.py              # Grass / Road / River / Rail + fábrica
│   ├── vehicle.py           # Car, Truck + geração para lane
│   ├── train.py             # Trem (idle → warning → running)
│   ├── log.py               # Log (tronco), LilyPad (vitória-régia)
│   └── eagle.py             # Águia (idle → appearing → striking)
│
└── utils/
    ├── constants.py         # Todas as constantes e cores
    └── math_utils.py        # lerp, clamp, smooth_step, AABB, hop_height
```

---

## Instalação

### 1. Instale o Python 3 e o FreeGLUT

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip freeglut3-dev
```

**macOS (Homebrew):**
```bash
brew install freeglut
```

**Windows:**
- Instale o Python 3 em python.org
- Baixe `freeglut.dll` e coloque na pasta do projeto ou em `System32`

### 2. Instale as dependências Python

```bash
pip install -r requirements.txt
```

Ou manualmente:
```bash
pip install PyOpenGL PyOpenGL_accelerate numpy
```

### 3. Execute o jogo

```bash
python main.py
```

---

##  Controles

| Tecla | Ação |
|-------|------|
| `W`   | Avançar (frente) |
| `A`   | Mover para esquerda |
| `D`   | Mover para direita |
| `S`   | Recuar |
| `R`   | Reiniciar (menu ou game over) |
| `ESC` | Sair |

---
