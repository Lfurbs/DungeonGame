import pygame
import sys
import math
import threading
import time
from collections import deque

pygame.init()

TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

TAMANHO_CELULA_BASE = 24
zoom = 1

pygame.display.set_caption("Labirinto")

COR_PAREDE = (50, 50, 50)
COR_CAMINHO = (200, 200, 200)
COR_JOGADOR = (255, 0, 0)
COR_INIMIGO = (0, 0, 255)
COR_BOLINHA = (0, 0, 0)

labirinto = [list(linha) for linha in [
    "############################################################",
    "############################################################",
    "############################################################",
    "############################################################",
    "##########              #####             ##################",
    "##      ##              #####             ##################",
    "##      ##              #####             ###########      #",
    "##      ###    ####   #########   ####   ############      #",
    "##      ###    ####   #########   ####   ############      #",
    "####  #############   #########   ####         ######      #",
    "####  #######                        #######   #######  ####",
    "####  #######                        #######   #######  ####",
    "#                ###############   #########   #######  ####",
    "#                ###############                        ####",
    "#  #########   ####################                     ####",
    "#  #########   ##############     ###    ###################",
    "#  #########   ##############            ###        ########",
    "#  #                   ######     ###    ###  #     ########",
    "#  #                              ##########  #     ########",
    "#  #                   ######                 ##############",
    "#                      ###########            ##############",
    "####                   ###########            ##############",
    "############    ##################            ##############",
    "#####           ##################            ##############",
    "#####  #####      ################            ##############",
    "#####  #########  ################                      ####",
    "#####  #########                                        ####",
    "###     ########  ######## #######                      ####",
    "###     ########  ######## #################################",
    "###     ########           #################################",
    "################           ##########            ###########",
    "##################                               ###########",
    "##################                               ###########",
    "##################         ##########            ###########",
    "############################################################",
]]

ALTURA_MAPA = len(labirinto)
LARGURA_MAPA = len(labirinto[0])

tamanho_jogador_base = TAMANHO_CELULA_BASE // 2

clock = pygame.time.Clock()

# Variáveis globais para o jogador
jogador_x, jogador_y = (13 * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2, 8 * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2)
angulo = 0
VEL_PX_POR_SEG = 150

# Variáveis globais para o inimigo
def achar_posicao_inimigo():
    for y in range(ALTURA_MAPA - 2, 0, -1):
        for x in range(LARGURA_MAPA - 2, 0, -1):
            if labirinto[y][x] == ' ':
                return x * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2, y * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
    return 1 * TAMANHO_CELULA_BASE, 1 * TAMANHO_CELULA_BASE

inimigo_x, inimigo_y = achar_posicao_inimigo()
angulo_inimigo = 0
VEL_INIMIGO_PX_POR_SEG = 100

# Movimentação do jogador
teclas = {'dx': 0, 'dy': 0}

def atualizar_jogador():
    global jogador_x, jogador_y, angulo
    while True:
        dx = teclas['dx']
        dy = teclas['dy']
        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            dx /= dist
            dy /= dist
            passo_x = dx * VEL_PX_POR_SEG * 0.02
            passo_y = dy * VEL_PX_POR_SEG * 0.02
            if pode_mover_pixel(jogador_x + passo_x, jogador_y, tamanho_jogador_base * 0.45):
                jogador_x += passo_x
            if pode_mover_pixel(jogador_x, jogador_y + passo_y, tamanho_jogador_base * 0.45):
                jogador_y += passo_y
            angulo = math.atan2(dy, dx)
        time.sleep(0.02)

def atualizar_inimigo():
    global inimigo_x, inimigo_y, angulo_inimigo

    caminho = []
    tempo_recalculo = 0

    while True:
        if tempo_recalculo <= 0:
            inicio = pixel_para_celula(inimigo_x, inimigo_y)
            destino = pixel_para_celula(jogador_x, jogador_y)
            caminho = bfs_caminho(labirinto, inicio, destino)
            tempo_recalculo = 0.5

        if caminho:
            alvo = caminho[0]
            alvo_x = alvo[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
            alvo_y = alvo[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

            vetor_x = alvo_x - inimigo_x
            vetor_y = alvo_y - inimigo_y
            dist = math.hypot(vetor_x, vetor_y)

            if dist != 0:
                dx = vetor_x / dist
                dy = vetor_y / dist
                passo_x = dx * 2
                passo_y = dy * 2

                if pode_mover_pixel(inimigo_x + passo_x, inimigo_y, tamanho_jogador_base * 0.45):
                    inimigo_x += passo_x
                if pode_mover_pixel(inimigo_x, inimigo_y + passo_y, tamanho_jogador_base * 0.45):
                    inimigo_y += passo_y

                angulo_inimigo = math.atan2(dy, dx)

            if dist < 3:
                caminho.pop(0)

        tempo_recalculo -= 0.02
        time.sleep(0.02)

# BFS para caminho do inimigo
def bfs_caminho(labirinto, inicio, destino):
    fila = deque([inicio])
    visitado = set([inicio])
    pai = {}

    while fila:
        atual = fila.popleft()
        if atual == destino:
            caminho = []
            while atual != inicio:
                caminho.append(atual)
                atual = pai[atual]
            caminho.reverse()
            return caminho
        x, y = atual
        for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
            if (0 <= nx < LARGURA_MAPA and 0 <= ny < ALTURA_MAPA and
                labirinto[ny][nx] != '#' and (nx, ny) not in visitado):
                visitado.add((nx, ny))
                pai[(nx, ny)] = atual
                fila.append((nx, ny))
    return []

# Funções utilitárias
def pode_mover_celula(cx, cy):
    return 0 <= cx < LARGURA_MAPA and 0 <= cy < ALTURA_MAPA and labirinto[cy][cx] != '#'

def pode_mover_pixel(px, py, raio):
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

def pixel_para_celula(px, py):
    return int(px // TAMANHO_CELULA_BASE), int(py // TAMANHO_CELULA_BASE)

# === Threads ===
thread_inimigo = threading.Thread(target=atualizar_inimigo)
thread_inimigo.daemon = True
thread_inimigo.start()

thread_jogador = threading.Thread(target=atualizar_jogador)
thread_jogador.daemon = True
thread_jogador.start()

# === Loop principal ===
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    teclas['dx'] = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
    teclas['dy'] = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])

    tamanho_celula_zoom = TAMANHO_CELULA_BASE * zoom
    tamanho_jogador_zoom = tamanho_jogador_base * zoom

    offset_x = jogador_x * zoom - LARGURA_TELA / 2
    offset_y = jogador_y * zoom - ALTURA_TELA / 2
    offset_x = max(0, min(offset_x, LARGURA_MAPA * tamanho_celula_zoom - LARGURA_TELA))
    offset_y = max(0, min(offset_y, ALTURA_MAPA * tamanho_celula_zoom - ALTURA_TELA))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    angulo_lanterna = math.atan2(
        (mouse_y + offset_y) - jogador_y * zoom,
        (mouse_x + offset_x) - jogador_x * zoom
    )

    TELA.fill((0, 0, 0))

    # Desenhar mapa e entidades
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

    def desenhar_entidade(x, y, angulo, cor):
        centro_x = x * zoom - offset_x
        centro_y = y * zoom - offset_y
        metade = tamanho_jogador_zoom / 3
        pontos = []
        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            ox = dx * metade
            oy = dy * metade
            rot_x = ox * math.cos(angulo) - oy * math.sin(angulo)
            rot_y = ox * math.sin(angulo) + oy * math.cos(angulo)
            pontos.append((centro_x + rot_x, centro_y + rot_y))
        pygame.draw.polygon(TELA, cor, pontos)
        frente_x = centro_x + math.cos(angulo) * metade * 1.5
        frente_y = centro_y + math.sin(angulo) * metade * 1.5
        pygame.draw.circle(TELA, COR_BOLINHA, (int(frente_x), int(frente_y)), max(1, int(1 * zoom)))

    desenhar_labirinto(offset_x, offset_y, tamanho_celula_zoom)
    desenhar_entidade(jogador_x, jogador_y, angulo, COR_JOGADOR)
    desenhar_entidade(inimigo_x, inimigo_y, angulo_inimigo, COR_INIMIGO)

    # === Cone de luz ===
    def calcular_cone_de_luz(jogador_x, jogador_y, angulo, offset_x, offset_y, alcance, abertura, num_rays):
        centro_x = jogador_x * zoom - offset_x
        centro_y = jogador_y * zoom - offset_y
        pontos = [(centro_x, centro_y)]
        for i in range(num_rays + 1):
            t = i / num_rays
            ang = angulo - abertura + t * (2 * abertura)
            dx = math.cos(ang)
            dy = math.sin(ang)
            raio_x = centro_x
            raio_y = centro_y
            for _ in range(int(alcance)):
                raio_x += dx
                raio_y += dy
                mapa_x = int((raio_x + offset_x) // TAMANHO_CELULA_BASE)
                mapa_y = int((raio_y + offset_y) // TAMANHO_CELULA_BASE)
                if (0 <= mapa_x < LARGURA_MAPA) and (0 <= mapa_y < ALTURA_MAPA):
                    if labirinto[mapa_y][mapa_x] == '#':
                        break
                else:
                    break
            pontos.append((raio_x, raio_y))
        return pontos

    cone = calcular_cone_de_luz(
        jogador_x, jogador_y, angulo_lanterna, offset_x, offset_y,
        alcance=80 * zoom,
        abertura=math.radians(30),
        num_rays=80
    )

    centro_x = jogador_x * zoom - offset_x
    centro_y = jogador_y * zoom - offset_y
    raio_luz = 25 * zoom

    sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 252))
    pygame.draw.polygon(sombra, (0, 0, 0, 0), cone)
    pygame.draw.circle(sombra, (0, 0, 0, 0), (int(centro_x), int(centro_y)), int(raio_luz))
    TELA.blit(sombra, (0, 0))

    pygame.display.flip()
