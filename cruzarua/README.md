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

## Arquitetura

### Separação de responsabilidades

- **`Game`** — máquina de estados (menu / playing / gameover). Não conhece OpenGL diretamente.
- **`Renderer`** — único módulo com chamadas `glXxx`. Oferece métodos de alto nível como `draw_car()`, `draw_tree()`, `draw_hud()`.
- **`Camera`** — calcula `gluLookAt` com interpolação suave para evitar movimentos bruscos.
- **`MapGenerator`** — mantém um dicionário `z_index → Lane`. Gera lanes à frente e descarta as antigas.
- **`CollisionManager`** — AABB puro, sem acoplamento a OpenGL.
- **`ScoreManager`** — calcula dificuldade progressiva como função da pontuação.

### Loop de jogo

```
GLUT timer (16ms) → game.update() → game.render() → glutSwapBuffers()
```

`update()` usa `delta time` real para que velocidades sejam independentes de FPS.

### Geração procedural

Cada frame, `MapGenerator.update()` verifica quantas lanes existem à frente e atrás do jogador.
Se faltam lanes (janela de `LANES_AHEAD` à frente), gera novas com tipo aleatório ponderado.
Se há lanes além de `LANES_BEHIND` para trás, remove-as do dicionário.

### Sistema de colisão AABB

```
player AABB (cx, cz, w, d) ↔ veículo AABB → sobreposição nos eixos X e Z
```

Para o rio, a lógica é inversa: se **não** há sobreposição com nenhuma plataforma → morte.

### Dificuldade progressiva

```
speed_factor = 1.0 + score × DIFF_SPEED_SCALE
eagle_idle   = max(2.0, EAGLE_IDLE_TIME - score × DIFF_EAGLE_SCALE)
```

---

## Solução de Problemas

**`No module named 'OpenGL'`**
```bash
pip install PyOpenGL PyOpenGL_accelerate
```

**`freeglut: ERROR: Function called without first calling 'glutInit'`**
- Certifique-se de rodar `python main.py`, não importar o módulo diretamente.

**Janela preta / sem imagem no macOS**
```bash
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH
python main.py
```

**Performance ruim**
- Verifique se `PyOpenGL_accelerate` está instalado.
- Reduza `VISIBLE_LANES` em `utils/constants.py`.
