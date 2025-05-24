import pygame
import sys
import math

pygame.init()

# Configurações do mapa (grade)

# Tela cheia
TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

# Tamanho base da célula (sem zoom)
TAMANHO_CELULA_BASE = 24
# Zoom inicial
zoom = 1.5

pygame.display.set_caption("Labirinto")

# Cores
COR_PAREDE = (50, 50, 50)
COR_CAMINHO = (200, 200, 200)
COR_JOGADOR = (255, 0, 0)
COR_BOLINHA = (0, 0, 0)

# Labirinto
labirinto = [
    "#########################################",
    "#      ##################################",
    "##     ##################################",
    "##     ##################################",
    "#####      ##############################",
    "#####          ##########################",
    "############## ##########################",
    "############## ####          ############",
    "############## ####          ############",
    "############## ######## #################",
    "##############                 ##########",
    "##########   # ##########################",
    "##########   # #######        ###########",
    "##########             ##################",
    "##########   # ##########################",
    "##########   # ##########################",
    "##############       # ####   ###########",
    "#################### # ####     #########",
    "#######   ####    ## # ####      ########",
    "#######   ####    ## #           ########",
    "#######              # ####      ########",
    "#######   ####    ## # ####      ########",
    "#######   ####    ## # ####    ##########",
    "##############    ##   ##################",
    "#########################################"
]


labirinto = [list(linha) for linha in labirinto]
ALTURA_MAPA = len(labirinto)
LARGURA_MAPA = len(labirinto[0])

# Posição do jogador no mundo (em pixels sem zoom)
jogador_x = 1 * TAMANHO_CELULA_BASE
jogador_y = 1 * TAMANHO_CELULA_BASE
velocidade = 2  # pixels por frame (sem zoom)
tamanho_jogador_base = TAMANHO_CELULA_BASE // 2

# Offset da câmera (em pixels, com zoom)
offset_x = 0
offset_y = 0

clock = pygame.time.Clock()

def desenhar_labirinto(offset_x, offset_y, tamanho_celula):
    for y in range(ALTURA_MAPA):
        for x in range(LARGURA_MAPA):
            celula = labirinto[y][x]
            cor = COR_PAREDE if celula == '#' else COR_CAMINHO
            rect = pygame.Rect(
                x * tamanho_celula - offset_x,
                y * tamanho_celula - offset_y,
                tamanho_celula,
                tamanho_celula
            )
            pygame.draw.rect(TELA, cor, rect)

def desenhar_jogador(x, y, angulo, offset_x, offset_y, tamanho_jogador):
    # Centro do jogador na tela (posição com zoom e offset)
    centro_x = x * zoom + TAMANHO_CELULA_BASE * zoom / 2 - offset_x
    centro_y = y * zoom + TAMANHO_CELULA_BASE * zoom / 2 - offset_y
    metade = tamanho_jogador / 3

    pontos = []
    for dx, dy in [(-1,-1), (1,-1), (1,1), (-1,1)]:
        ox = dx * metade
        oy = dy * metade
        rot_x = ox * math.cos(angulo) - oy * math.sin(angulo)
        rot_y = ox * math.sin(angulo) + oy * math.cos(angulo)
        pontos.append((centro_x + rot_x, centro_y + rot_y))

    pygame.draw.polygon(TELA, COR_JOGADOR, pontos)

    # Bolinha frontal
    frente_x = centro_x + math.cos(angulo) * metade * 1.5
    frente_y = centro_y + math.sin(angulo) * metade * 1.5
    pygame.draw.circle(TELA, COR_BOLINHA, (int(frente_x), int(frente_y)), max(1, int(1 * zoom)))

def pode_mover(x, y):
    margem = (TAMANHO_CELULA_BASE - tamanho_jogador_base) // 2
    pontos = [
        (x + margem, y + margem),
        (x + margem + tamanho_jogador_base - 1, y + margem),
        (x + margem, y + margem + tamanho_jogador_base - 1),
        (x + margem + tamanho_jogador_base - 1, y + margem + tamanho_jogador_base - 1),
    ]
    for px, py in pontos:
        col = int(px) // TAMANHO_CELULA_BASE
        lin = int(py) // TAMANHO_CELULA_BASE
        if 0 <= lin < ALTURA_MAPA and 0 <= col < LARGURA_MAPA:
            if labirinto[lin][col] == '#':
                return False
        else:
            return False
    return True

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEWHEEL:
                zoom += event.y * 0.1
                zoom = max(0.5, min(3.0, zoom))

        # Pega posição do mouse na tela
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calcula posição do mouse no mundo, considerando offset e zoom
        mouse_mundo_x = mouse_x + offset_x
        mouse_mundo_y = mouse_y + offset_y

        # Centro do jogador no mundo (com zoom)
        centro_jogador_x = jogador_x * zoom + TAMANHO_CELULA_BASE * zoom / 2
        centro_jogador_y = jogador_y * zoom + TAMANHO_CELULA_BASE * zoom / 2

        # Vetor direção do jogador para o mouse no mundo
        dx = mouse_mundo_x - centro_jogador_x
        dy = mouse_mundo_y - centro_jogador_y

        distancia = math.hypot(dx, dy)
        if distancia != 0:
            dx /= distancia
            dy /= distancia

        # Move jogador ao clicar botão esquerdo
        distancia_minima = 10  # ajuste esse valor como quiser
        if pygame.mouse.get_pressed()[0] and distancia > distancia_minima:
            novo_x = jogador_x + dx * velocidade
            novo_y = jogador_y + dy * velocidade
            if pode_mover(novo_x, jogador_y):
                jogador_x = novo_x
            if pode_mover(jogador_x, novo_y):
                jogador_y = novo_y

        # Calcula tamanho da célula e jogador com zoom
        tamanho_celula_zoom = TAMANHO_CELULA_BASE * zoom
        tamanho_jogador_zoom = tamanho_jogador_base * zoom

        # Atualiza offset da câmera para centralizar jogador
        offset_x = jogador_x * zoom + tamanho_celula_zoom / 2 - LARGURA_TELA / 2
        offset_y = jogador_y * zoom + tamanho_celula_zoom / 2 - ALTURA_TELA / 2

        # Limita offset para não mostrar fora do mapa
        max_offset_x = LARGURA_MAPA * tamanho_celula_zoom - LARGURA_TELA
        max_offset_y = ALTURA_MAPA * tamanho_celula_zoom - ALTURA_TELA
        offset_x = max(0, min(offset_x, max_offset_x))
        offset_y = max(0, min(offset_y, max_offset_y))

        # Calcula ângulo para desenhar jogador olhando para o mouse
        angulo = math.atan2(dy, dx)

        # Desenho
        TELA.fill((0,0,0))
        desenhar_labirinto(offset_x, offset_y, tamanho_celula_zoom)
        desenhar_jogador(jogador_x, jogador_y, angulo, offset_x, offset_y, tamanho_jogador_zoom)

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    pygame.quit()
    print("Ocorreu um erro:", e)
    sys.exit()
