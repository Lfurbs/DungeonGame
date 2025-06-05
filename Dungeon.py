import pygame
import sys
import math

pygame.init()

TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

TAMANHO_CELULA_BASE = 24
zoom = 1.5

pygame.display.set_caption("Labirinto")

COR_PAREDE = (50, 50, 50)
COR_CAMINHO = (200, 200, 200)
COR_JOGADOR = (255, 0, 0)
COR_BOLINHA = (0, 0, 0)

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

tamanho_jogador_base = TAMANHO_CELULA_BASE // 2

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
    centro_x = x * zoom - offset_x
    centro_y = y * zoom - offset_y
    metade = tamanho_jogador / 3
    pontos = []
    for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        ox = dx * metade
        oy = dy * metade
        rot_x = ox * math.cos(angulo) - oy * math.sin(angulo)
        rot_y = ox * math.sin(angulo) + oy * math.cos(angulo)
        pontos.append((centro_x + rot_x, centro_y + rot_y))
    pygame.draw.polygon(TELA, COR_JOGADOR, pontos)
    frente_x = centro_x + math.cos(angulo) * metade * 1.5
    frente_y = centro_y + math.sin(angulo) * metade * 1.5
    pygame.draw.circle(TELA, COR_BOLINHA, (int(frente_x), int(frente_y)), max(1, int(1 * zoom)))

def pode_mover_celula(cx, cy):
    return 0 <= cx < LARGURA_MAPA and 0 <= cy < ALTURA_MAPA and labirinto[cy][cx] != '#'

def pode_mover_pixel(px, py, raio):
    # Testa múltiplos pontos ao redor do centro para evitar passar por cantos
    # Usa passo menor para um círculo "mais cheio"
    passos = 8
    for i in range(passos):
        angle = 2 * math.pi * i / passos
        check_x = px + math.cos(angle) * raio
        check_y = py + math.sin(angle) * raio
        cx = int(check_x // TAMANHO_CELULA_BASE)
        cy = int(check_y // TAMANHO_CELULA_BASE)
        if not pode_mover_celula(cx, cy):
            return False
    return True

def celula_para_pixel(cx, cy):
    return cx * TAMANHO_CELULA_BASE, cy * TAMANHO_CELULA_BASE

jogador_x, jogador_y = celula_para_pixel(1, 1)
jogador_x += TAMANHO_CELULA_BASE / 2
jogador_y += TAMANHO_CELULA_BASE / 2

angulo = 0
VEL_PX_POR_SEG = 100

while True:
    delta = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    teclas = pygame.key.get_pressed()

    dx = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
    dy = (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP])

    if dx != 0 or dy != 0:
        dist = math.hypot(dx, dy)
        dx /= dist
        dy /= dist

        passo_x = dx * VEL_PX_POR_SEG * delta
        passo_y = dy * VEL_PX_POR_SEG * delta

        if pode_mover_pixel(jogador_x + passo_x, jogador_y, tamanho_jogador_base * 0.45):
            jogador_x += passo_x

        if pode_mover_pixel(jogador_x, jogador_y + passo_y, tamanho_jogador_base * 0.45):
            jogador_y += passo_y

        angulo = math.atan2(dy, dx)

    tamanho_celula_zoom = TAMANHO_CELULA_BASE * zoom
    tamanho_jogador_zoom = tamanho_jogador_base * zoom

    offset_x = jogador_x * zoom - LARGURA_TELA / 2
    offset_y = jogador_y * zoom - ALTURA_TELA / 2

    max_offset_x = LARGURA_MAPA * tamanho_celula_zoom - LARGURA_TELA
    max_offset_y = ALTURA_MAPA * tamanho_celula_zoom - ALTURA_TELA

    offset_x = max(0, min(offset_x, max_offset_x))
    offset_y = max(0, min(offset_y, max_offset_y))

    TELA.fill((0, 0, 0))
    desenhar_labirinto(offset_x, offset_y, tamanho_celula_zoom)
    desenhar_jogador(jogador_x, jogador_y, angulo, offset_x, offset_y, tamanho_jogador_zoom)

    pygame.display.flip()
