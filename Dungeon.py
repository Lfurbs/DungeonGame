import pygame
import sys
import math
import threading
import time
from collections import deque
import random

pygame.init()

LARGURA_JANELA_INICIAL = 800
ALTURA_JANELA_INICIAL = 600

TELA = pygame.display.set_mode((LARGURA_JANELA_INICIAL, ALTURA_JANELA_INICIAL))
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

TAMANHO_CELULA_BASE = 24
zoom = 1

pygame.display.set_caption("Labirinto")

COR_PAREDE = (50, 50, 50)
COR_CAMINHO = (200, 200, 200)
COR_JOGADOR = (255, 0, 0)
COR_INIMIGO = (0, 0, 255)
COR_BOLINHA = (0, 0, 0)
COR_TEXTO = (255, 255, 255) 
COR_BOTAO_NORMAL = (100, 100, 100) 
COR_BOTAO_HOVER = (150, 150, 150) 

labirinto_map = [
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
]
labirinto = [list(linha) for linha in labirinto_map]

ALTURA_MAPA = len(labirinto)
if ALTURA_MAPA > 0:
    LARGURA_MAPA = len(labirinto[0])
else:
    LARGURA_MAPA = 0
    print("ERRO: Labirinto está vazio, encerrando programa!")
    pygame.quit()
    sys.exit()

for i, row in enumerate(labirinto):
    if len(row) != LARGURA_MAPA:
        print(f"ERRO: Linha {i} tem comprimento {len(row)}, esperado {LARGURA_MAPA}, encerrando programa.")
        pygame.quit()
        sys.exit()

tamanho_jogador_base = TAMANHO_CELULA_BASE // 2

clock = pygame.time.Clock()

is_fullscreen = False

# Funções desenho▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
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


def desenhar_labirinto(offset_x, offset_y, tamanho_celula):
    for y in range(ALTURA_MAPA):
        for x in range(LARGURA_MAPA):
            if not (0 <= y < ALTURA_MAPA and 0 <= x < LARGURA_MAPA):
                continue
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

def desenhar_inimigo(x, y, angulo, offset_x, offset_y, tamanho_inimigo):
    centro_x = x * zoom - offset_x
    centro_y = y * zoom - offset_y
    metade = tamanho_inimigo / 3
    pontos = []
    for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        ox = dx * metade
        oy = dy * metade
        rot_x = ox * math.cos(angulo) - oy * math.sin(angulo)
        rot_y = ox * math.sin(angulo) + oy * math.cos(angulo)
        pontos.append((centro_x + rot_x, centro_y + rot_y))
    pygame.draw.polygon(TELA, COR_INIMIGO, pontos)
    frente_x = centro_x + math.cos(angulo) * metade * 1.5
    frente_y = centro_y + math.sin(angulo) * metade * 1.5
    pygame.draw.circle(TELA, COR_BOLINHA, (int(frente_x), int(frente_y)), max(1, int(1 * zoom)))

# Colisão/conversão▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
def pode_mover_celula(cx, cy):
    if not (0 <= cy < ALTURA_MAPA and 0 <= cx < LARGURA_MAPA):
        return False
    return labirinto[cy][cx] != '#'

def pode_mover_pixel(px, py, raio):
    passos = 16
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

def achar_posicao_inimigo():
    for y in range(ALTURA_MAPA - 1, -1, -1):
        for x in range(LARGURA_MAPA - 1, -1, -1):
            if labirinto[y][x] == ' ':
                return celula_para_pixel(x, y)
    return celula_para_pixel(1, 1)

def bfs_caminho(labirinto, inicio, destino):
    if not pode_mover_celula(inicio[0], inicio[1]) or not pode_mover_celula(destino[0], destino[1]):
        return []

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

def linha_de_visao(x1, y1, x2, y2):
    cx1, cy1 = pixel_para_celula(x1, y1)
    cx2, cy2 = pixel_para_celula(x2, y2)

    dx = abs(cx2 - cx1)
    dy = abs(cy2 - cy1)
    sx = 1 if cx1 < cx2 else -1
    sy = 1 if cy1 < cy2 else -1
    err = dx - dy

    px, py = cx1, cy1

    while True:
        if not pode_mover_celula(px, py):
            return False
        
        if px == cx2 and py == cy2:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            px += sx
        if e2 < dx:
            err += dx
            py += sy
    return True

# Ponto polígono (detecção de luz) ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
def is_point_in_polygon(point, polygon):
    x, y = point
    num_vertices = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(num_vertices + 1):
        p2x, p2y = polygon[i % num_vertices]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    else:
                        xinters = x + 1

                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


# Variáveis globais▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
ESTADO_JOGANDO = 0
ESTADO_GAME_OVER = 1

terminar_thread_inimigo = False
jogador_x, jogador_y = 0.0, 0.0 
inimigo_x, inimigo_y = 0.0, 0.0 

angulo = 0
angulo_inimigo = 0
VEL_PX_POR_SEG = 150
VEL_INIMIGO_PX_POR_SEG = 100

caminho_inimigo = []
indice_caminho = 0
tempo_para_recalcular_inimigo_path = 0.5
tempo_para_recalcular_inimigo_patrol = 1.0

ESTADO_PATRULHA = 0
ESTADO_PERSEGUICAO = 1
ESTADO_FUGA_LUZ = 2 
inimigo_estado = ESTADO_PATRULHA

alvo_patrulha_pixel = None

RAIO_VISAO_INIMIGO = TAMANHO_CELULA_BASE * 8
RAIO_COLISAO_INIMIGO = tamanho_jogador_base * 0.45

TEMPO_MEMORIA_PERSEGUICAO = 3.0 
tempo_sem_ver_jogador = TEMPO_MEMORIA_PERSEGUICAO 

vibração_ativa = False 
FORCA_VIBRACAO_MAX = 5
RAIO_VIBRACAO_MAX = TAMANHO_CELULA_BASE * 20

jogador_morto = False

tempo_restante_fuga = 0.0
alvo_fuga_pixel = None 
caminho_fuga = [] 
indice_caminho_fuga = 0 

angulo_lanterna = 0.0 

# Configurações da lanterna▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
tempo_maximo_lanterna = 5  
tempo_recarga = 5  
tempo_restante_lanterna = tempo_maximo_lanterna
lanterna_ativa = False
tempo_lanterna_contando = False
em_recarga = False
tempo_restante_recarga = 0

# Reinicializção/game over▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
def reset_game():
    global jogador_x, jogador_y, inimigo_x, inimigo_y, angulo, angulo_inimigo, \
           caminho_inimigo, indice_caminho, tempo_para_recalcular_inimigo_path, \
           tempo_para_recalcular_inimigo_patrol, inimigo_estado, alvo_patrulha_pixel, \
           tempo_sem_ver_jogador, vibração_ativa, jogador_morto, estado_jogo_atual, \
           terminar_thread_inimigo, tempo_restante_fuga, \
           alvo_fuga_pixel, caminho_fuga, indice_caminho_fuga, \
           angulo_lanterna

    jogador_x_inicial, jogador_y_inicial = celula_para_pixel(13,8)
    jogador_x = jogador_x_inicial + TAMANHO_CELULA_BASE / 2
    jogador_y = jogador_y_inicial + TAMANHO_CELULA_BASE / 2

    inimigo_x_inicial, inimigo_y_inicial = achar_posicao_inimigo()
    inimigo_x = inimigo_x_inicial + TAMANHO_CELULA_BASE / 2
    inimigo_y = inimigo_y_inicial + TAMANHO_CELULA_BASE / 2

    angulo = 0
    angulo_inimigo = 0

    caminho_inimigo = []
    indice_caminho = 0
    tempo_para_recalcular_inimigo_path = 0.5
    tempo_para_recalcular_inimigo_patrol = 1.0
    inimigo_estado = ESTADO_PATRULHA
    alvo_patrulha_pixel = None
    tempo_sem_ver_jogador = TEMPO_MEMORIA_PERSEGUICAO

    vibração_ativa = False
    jogador_morto = False
    estado_jogo_atual = ESTADO_JOGANDO

    tempo_restante_fuga = 0.0
    alvo_fuga_pixel = None 
    caminho_fuga = [] 
    indice_caminho_fuga = 0 
    angulo_lanterna = 0.0 
    terminar_thread_inimigo = True

def desenhar_game_over():
    fonte_titulo = pygame.font.Font(None, 80)
    fonte_botao = pygame.font.Font(None, 50)

    sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 180))
    TELA.blit(sombra, (0,0))

    texto_game_over = fonte_titulo.render("GAME OVER", True, COR_JOGADOR)
    rect_game_over = texto_game_over.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 100))
    TELA.blit(texto_game_over, rect_game_over)

    texto_tentar_novamente = fonte_botao.render("Again?", True, COR_TEXTO)
    rect_tentar_novamente = pygame.Rect(0, 0, 300, 70)
    rect_tentar_novamente.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 20)

    texto_encerrar_jogo = fonte_botao.render("Close game", True, COR_TEXTO)
    rect_encerrar_jogo = pygame.Rect(0, 0, 300, 70)
    rect_encerrar_jogo.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 120)

    mouse_pos = pygame.mouse.get_pos()

    cor_btn_tentar = COR_BOTAO_NORMAL
    if rect_tentar_novamente.collidepoint(mouse_pos):
        cor_btn_tentar = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_tentar, rect_tentar_novamente, border_radius=10)
    TELA.blit(texto_tentar_novamente, texto_tentar_novamente.get_rect(center=rect_tentar_novamente.center))

    cor_btn_encerrar = COR_BOTAO_NORMAL
    if rect_encerrar_jogo.collidepoint(mouse_pos):
        cor_btn_encerrar = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_encerrar, rect_encerrar_jogo, border_radius=10)
    TELA.blit(texto_encerrar_jogo, texto_encerrar_jogo.get_rect(center=rect_encerrar_jogo.center))

    return rect_tentar_novamente, rect_encerrar_jogo

def atualizar_inimigo_thread():
    global inimigo_x, inimigo_y, angulo_inimigo, inimigo_estado, caminho_inimigo, \
           indice_caminho, alvo_patrulha_pixel, tempo_para_recalcular_inimigo_path, \
           tempo_para_recalcular_inimigo_patrol, jogador_x, jogador_y, \
           tempo_sem_ver_jogador, vibração_ativa, jogador_morto, estado_jogo_atual, \
           terminar_thread_inimigo, tempo_restante_fuga, alvo_fuga_pixel, caminho_fuga, indice_caminho_fuga, \
           angulo_lanterna

    while True:
        if terminar_thread_inimigo:
            break

        if estado_jogo_atual != ESTADO_JOGANDO:
            time.sleep(0.1)
            continue

        delta_thread = 0.02

# Detecção de luz (inimigo)▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
        alcance_luz_base = 80
        abertura_luz = math.radians(30)
        
        cone_luz_pontos_mundo = calcular_cone_de_luz(
            jogador_x, jogador_y, angulo_lanterna, 0, 0,
            alcance_luz_base * zoom, abertura_luz, num_rays=80
        )

        centro_inimigo_mundo = (inimigo_x * zoom, inimigo_y * zoom)
        
        inimigo_na_luz = is_point_in_polygon(centro_inimigo_mundo, cone_luz_pontos_mundo)

        if not lanterna_ativa:
            inimigo_na_luz = False

# Transição de estados (inimigo)▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
        if inimigo_na_luz and inimigo_estado != ESTADO_FUGA_LUZ:
            print("inimigo atingido pela luz, fugindo...")
            inimigo_estado = ESTADO_FUGA_LUZ
            tempo_restante_fuga = 3.0 
            vibração_ativa = False
            inicio_fuga_celula = pixel_para_celula(inimigo_x, inimigo_y)
            dir_oposta_x_raw = inimigo_x - jogador_x
            dir_oposta_y_raw = inimigo_y - jogador_y
            
            mag = math.hypot(dir_oposta_x_raw, dir_oposta_y_raw)
            if mag == 0:
                dir_oposta_x_raw, dir_oposta_y_raw = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                mag = 1.0

            dir_oposta_x_norm = dir_oposta_x_raw / mag
            dir_oposta_y_norm = dir_oposta_y_raw / mag

            distancia_alvo_fuga = random.uniform(10, 16) 
            
            alvo_fuga_x_pixel = inimigo_x + dir_oposta_x_norm * (TAMANHO_CELULA_BASE * distancia_alvo_fuga)
            alvo_fuga_y_pixel = inimigo_y + dir_oposta_y_norm * (TAMANHO_CELULA_BASE * distancia_alvo_fuga)
    
            alvo_fuga_celula_temp = pixel_para_celula(alvo_fuga_x_pixel, alvo_fuga_y_pixel)
            
            alvo_fuga_celula_temp = (max(0, min(alvo_fuga_celula_temp[0], LARGURA_MAPA - 1)),
                                     max(0, min(alvo_fuga_celula_temp[1], ALTURA_MAPA - 1)))

            caminho_fuga_temp = []
            tentativas_alvo_fuga = 0
            max_tentativas_alvo_fuga = 10
            
            while not caminho_fuga_temp and tentativas_alvo_fuga < max_tentativas_alvo_fuga:
                if tentativas_alvo_fuga > 0:
                    rand_cx = random.randint(0, LARGURA_MAPA - 1)
                    rand_cy = random.randint(0, ALTURA_MAPA - 1)
                    alvo_fuga_celula_temp = (rand_cx, rand_cy)

                caminho_fuga_temp = bfs_caminho(labirinto, inicio_fuga_celula, alvo_fuga_celula_temp)
                tentativas_alvo_fuga += 1

            caminho_fuga = caminho_fuga_temp
            indice_caminho_fuga = 0
            alvo_fuga_pixel = celula_para_pixel(alvo_fuga_celula_temp[0], alvo_fuga_celula_temp[1])
            alvo_fuga_pixel = (alvo_fuga_pixel[0] + TAMANHO_CELULA_BASE / 2, alvo_fuga_pixel[1] + TAMANHO_CELULA_BASE / 2)
            
        elif inimigo_estado != ESTADO_FUGA_LUZ:
            distancia_jogador_inimigo_thread = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)
            
            jogador_visivel_agora = False
            if distancia_jogador_inimigo_thread <= RAIO_VISAO_INIMIGO:
                if linha_de_visao(inimigo_x, inimigo_y, jogador_x, jogador_y):
                    jogador_visivel_agora = True
            
            if jogador_visivel_agora:
                tempo_sem_ver_jogador = 0.0
                if inimigo_estado != ESTADO_PERSEGUICAO:
                    print("inimigo avistou jogador, perseguindo...")
                    vibração_ativa = True
                inimigo_estado = ESTADO_PERSEGUICAO
            else:
                tempo_sem_ver_jogador += delta_thread
                if inimigo_estado == ESTADO_PERSEGUICAO and tempo_sem_ver_jogador < TEMPO_MEMORIA_PERSEGUICAO:
                    pass
                else:
                    if inimigo_estado == ESTADO_PERSEGUICAO:
                        print("inimigo perdeu jogador de vista, patrulhando...")
                        vibração_ativa = False
                    inimigo_estado = ESTADO_PATRULHA
        
        if inimigo_estado == ESTADO_FUGA_LUZ:
            tempo_restante_fuga -= delta_thread
            
            if tempo_restante_fuga <= 0:
                inimigo_estado = ESTADO_PATRULHA
                print("fuga encerrada, patrulhando...")
                alvo_patrulha_pixel = None 
                caminho_inimigo = [] 
                tempo_para_recalcular_inimigo_patrol = 0.0 
            
            if not caminho_fuga or indice_caminho_fuga >= len(caminho_fuga):
                inicio_fuga_celula = pixel_para_celula(inimigo_x, inimigo_y)
                alvo_fuga_x_pixel = inimigo_x + random.uniform(-1,1) * (TAMANHO_CELULA_BASE * 10)
                alvo_fuga_y_pixel = inimigo_y + random.uniform(-1,1) * (TAMANHO_CELULA_BASE * 10)
                alvo_fuga_celula_temp = pixel_para_celula(alvo_fuga_x_pixel, alvo_fuga_y_pixel)
                alvo_fuga_celula_temp = (max(0, min(alvo_fuga_celula_temp[0], LARGURA_MAPA - 1)),
                                         max(0, min(alvo_fuga_celula_temp[1], ALTURA_MAPA - 1)))
                
                caminho_fuga_temp = []
                tentativas_recalc_fuga = 0
                while not caminho_fuga_temp and tentativas_recalc_fuga < 5: 
                    caminho_fuga_temp = bfs_caminho(labirinto, inicio_fuga_celula, alvo_fuga_celula_temp)
                    if not caminho_fuga_temp: 
                        rand_cx = random.randint(0, LARGURA_MAPA - 1)
                        rand_cy = random.randint(0, ALTURA_MAPA - 1)
                        alvo_fuga_celula_temp = (rand_cx, rand_cy)
                    tentativas_recalc_fuga += 1

                caminho_fuga = caminho_fuga_temp
                indice_caminho_fuga = 0
                if not caminho_fuga:
                    inimigo_estado = ESTADO_PATRULHA
                    print("erro: não conseguiu recalcular caminho, patrulhando...")
                    alvo_patrulha_pixel = None
                    caminho_inimigo = []
                    tempo_para_recalcular_inimigo_patrol = 0.0

            if caminho_fuga and indice_caminho_fuga < len(caminho_fuga):
                alvo_celula_fuga = caminho_fuga[indice_caminho_fuga]
                alvo_x = alvo_celula_fuga[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
                alvo_y = alvo_celula_fuga[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

                vetor_x = alvo_x - inimigo_x
                vetor_y = alvo_y - inimigo_y
                dist = math.hypot(vetor_x, vetor_y)

                if dist < 3:
                    indice_caminho_fuga += 1
                
                if dist > 0:
                    dx_fuga = vetor_x / dist
                    dy_fuga = vetor_y / dist

                    passo_fuga_x = dx_fuga * VEL_INIMIGO_PX_POR_SEG * delta_thread
                    passo_fuga_y = dy_fuga * VEL_INIMIGO_PX_POR_SEG * delta_thread

                    if pode_mover_pixel(inimigo_x + passo_fuga_x, inimigo_y, RAIO_COLISAO_INIMIGO):
                        inimigo_x += passo_fuga_x
                    if pode_mover_pixel(inimigo_x, inimigo_y + passo_fuga_y, RAIO_COLISAO_INIMIGO):
                        inimigo_y += passo_fuga_y

                    angulo_inimigo = math.atan2(dy_fuga, dx_fuga)
                else:
                    pass


        elif inimigo_estado == ESTADO_PERSEGUICAO:
            tempo_para_recalcular_inimigo_path -= delta_thread
            if tempo_para_recalcular_inimigo_path <= 0:
                inicio_celula = pixel_para_celula(inimigo_x, inimigo_y)
                destino_celula = pixel_para_celula(jogador_x, jogador_y)
                caminho_inimigo = bfs_caminho(labirinto, inicio_celula, destino_celula)
                indice_caminho = 0 
                tempo_para_recalcular_inimigo_path = 0.5 

            if caminho_inimigo and indice_caminho < len(caminho_inimigo):
                alvo_celula = caminho_inimigo[indice_caminho]
                alvo_x = alvo_celula[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
                alvo_y = alvo_celula[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

                vetor_x = alvo_x - inimigo_x
                vetor_y = alvo_y - inimigo_y
                dist = math.hypot(vetor_x, vetor_y)

                if dist < 3:
                    indice_caminho += 1
                else:
                    if dist > 0:
                        dx_inimigo = vetor_x / dist
                        dy_inimigo = vetor_y / dist
                    else:
                        dx_inimigo, dy_inimigo = 0, 0

                    passo_inimigo_x = dx_inimigo * VEL_INIMIGO_PX_POR_SEG * delta_thread
                    passo_inimigo_y = dy_inimigo * VEL_INIMIGO_PX_POR_SEG * delta_thread

                    if pode_mover_pixel(inimigo_x + passo_inimigo_x, inimigo_y, RAIO_COLISAO_INIMIGO):
                        inimigo_x += passo_inimigo_x
                    if pode_mover_pixel(inimigo_x, inimigo_y + passo_inimigo_y, RAIO_COLISAO_INIMIGO):
                        inimigo_y += passo_inimigo_y

                    if dx_inimigo != 0 or dy_inimigo != 0:
                        angulo_inimigo = math.atan2(dy_inimigo, dx_inimigo)
            else:
                if not jogador_visivel_agora and inimigo_estado == ESTADO_PERSEGUICAO:
                    inimigo_estado = ESTADO_PATRULHA
                    vibração_ativa = False
                alvo_patrulha_pixel = None

        elif inimigo_estado == ESTADO_PATRULHA:
            tempo_para_recalcular_inimigo_patrol -= delta_thread
            if alvo_patrulha_pixel is None or tempo_para_recalcular_inimigo_patrol <= 0:
                encontrou_alvo = False
                tentativas = 0
                while not encontrou_alvo and tentativas < 50:
                    rand_cx = random.randint(0, LARGURA_MAPA - 1)
                    rand_cy = random.randint(0, ALTURA_MAPA - 1)
                    
                    temp_alvo_x, temp_alvo_y = celula_para_pixel(rand_cx, rand_cy)
                    temp_alvo_x += TAMANHO_CELULA_BASE / 2
                    temp_alvo_y += TAMANHO_CELULA_BASE / 2

                    if pode_mover_celula(rand_cx, rand_cy):
                        caminho_aleatorio = bfs_caminho(labirinto, pixel_para_celula(inimigo_x, inimigo_y), (rand_cx, rand_cy))
                        if caminho_aleatorio:
                            alvo_patrulha_pixel = (temp_alvo_x, temp_alvo_y)
                            caminho_inimigo = caminho_aleatorio
                            indice_caminho = 0
                            encontrou_alvo = True
                            tempo_para_recalcular_inimigo_patrol = random.uniform(3.0, 7.0)
                    tentativas += 1
                if not encontrou_alvo: 
                    caminho_inimigo = []
                    alvo_patrulha_pixel = None
                    tempo_para_recalcular_inimigo_patrol = 1.0

            if caminho_inimigo and indice_caminho < len(caminho_inimigo):
                alvo_celula = caminho_inimigo[indice_caminho]
                alvo_x = alvo_celula[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
                alvo_y = alvo_celula[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

                vetor_x = alvo_x - inimigo_x
                vetor_y = alvo_y - inimigo_y
                dist = math.hypot(vetor_x, vetor_y)

                if dist < 3:
                    indice_caminho += 1
                else:
                    if dist > 0:
                        dx_inimigo = vetor_x / dist
                        dy_inimigo = vetor_y / dist
                    else:
                        dx_inimigo, dy_inimigo = 0, 0

                    passo_inimigo_x = dx_inimigo * VEL_INIMIGO_PX_POR_SEG * delta_thread
                    passo_inimigo_y = dy_inimigo * VEL_INIMIGO_PX_POR_SEG * delta_thread

                    if pode_mover_pixel(inimigo_x + passo_inimigo_x, inimigo_y, RAIO_COLISAO_INIMIGO):
                        inimigo_x += passo_inimigo_x
                    if pode_mover_pixel(inimigo_x, inimigo_y + passo_inimigo_y, RAIO_COLISAO_INIMIGO):
                        inimigo_y += passo_inimigo_y

                    if dx_inimigo != 0 or dy_inimigo != 0:
                        angulo_inimigo = math.atan2(dy_inimigo, dx_inimigo)
            else:
                alvo_patrulha_pixel = None
                caminho_inimigo = []

        raio_colisao_jogador = tamanho_jogador_base * 0.45
        raio_colisao_inimigo = RAIO_COLISAO_INIMIGO
        
        distancia_px_jogador_inimigo = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)
        if distancia_px_jogador_inimigo < (raio_colisao_jogador + raio_colisao_inimigo) * 1.05:
            jogador_morto = True
            estado_jogo_atual = ESTADO_GAME_OVER

        time.sleep(delta_thread)

# Inicialização do jogo▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
thread_inimigo_obj = None
estado_jogo_atual = ESTADO_JOGANDO

reset_game()

# Loop principal▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
while True:
    delta = clock.tick(60) / 1000

# Configurações de tempo da lanterna▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
    tempo_passado = delta

    if tempo_lanterna_contando:
        tempo_restante_lanterna -= tempo_passado
        if tempo_restante_lanterna <= 0:
            tempo_restante_lanterna = 0
            lanterna_ativa = False
            tempo_lanterna_contando = False
            em_recarga = True
            tempo_restante_recarga = tempo_recarga

    if em_recarga:
        tempo_restante_recarga -= tempo_passado
        if tempo_restante_recarga <= 0:
            tempo_restante_recarga = 0
            em_recarga = False
            tempo_restante_lanterna = tempo_maximo_lanterna

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if not em_recarga:
                    if tempo_restante_lanterna > 0:
                        lanterna_ativa = not lanterna_ativa
                        tempo_lanterna_contando = lanterna_ativa
        if event.type == pygame.QUIT:
            if thread_inimigo_obj and thread_inimigo_obj.is_alive():
                terminar_thread_inimigo = True
                thread_inimigo_obj.join()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    TELA = pygame.display.set_mode((LARGURA_JANELA_INICIAL, ALTURA_JANELA_INICIAL))
                LARGURA_TELA, ALTURA_TELA = TELA.get_size()
        
        if estado_jogo_atual == ESTADO_GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if rect_tentar_novamente.collidepoint(mouse_pos):
                    terminar_thread_inimigo = True
                    if thread_inimigo_obj and thread_inimigo_obj.is_alive():
                        thread_inimigo_obj.join()

                    reset_game()
                    
                elif rect_encerrar_jogo.collidepoint(mouse_pos):
                    if thread_inimigo_obj and thread_inimigo_obj.is_alive():
                        terminar_thread_inimigo = True
                        thread_inimigo_obj.join()
                    pygame.quit()
                    sys.exit()

    if estado_jogo_atual == ESTADO_JOGANDO:
        if thread_inimigo_obj is None or not thread_inimigo_obj.is_alive():
            terminar_thread_inimigo = False
            thread_inimigo_obj = threading.Thread(target=atualizar_inimigo_thread)
            thread_inimigo_obj.daemon = True
            thread_inimigo_obj.start()

        teclas = pygame.key.get_pressed()

        dx = (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT])
        dy = (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP])

        if dx != 0 or dy != 0:
            dist = math.hypot(dx, dy)
            if dist > 0:
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

        offset_x_base = jogador_x * zoom - LARGURA_TELA / 2
        offset_y_base = jogador_y * zoom - ALTURA_TELA / 2

        offset_x_final = offset_x_base
        offset_y_final = offset_y_base

        mouse_x, mouse_y = pygame.mouse.get_pos()
        angulo_lanterna = math.atan2(
            (mouse_y + offset_y_final) - jogador_y * zoom,
            (mouse_x + offset_x_final) - jogador_x * zoom
        )
    
# Lógica vibração▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
        distancia_jogador_inimigo_para_vibracao = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)

        if vibração_ativa:
            if distancia_jogador_inimigo_para_vibracao < RAIO_VIBRACAO_MAX:
                forca_vibracao = FORCA_VIBRACAO_MAX * (1 - min(1, distancia_jogador_inimigo_para_vibracao / RAIO_VIBRACAO_MAX))
                
                offset_vibracao_x = random.uniform(-forca_vibracao, forca_vibracao)
                offset_vibracao_y = random.uniform(-forca_vibracao, forca_vibracao)

                offset_x_final += offset_vibracao_x
                offset_y_final += offset_vibracao_y

        max_offset_x = max(0, LARGURA_MAPA * tamanho_celula_zoom - LARGURA_TELA)
        max_offset_y = max(0, ALTURA_MAPA * tamanho_celula_zoom - ALTURA_TELA)

        offset_x_final = max(0, min(offset_x_final, max_offset_x))
        offset_y_final = max(0, min(offset_y_final, max_offset_y))

        TELA.fill((0, 0, 0))
        desenhar_labirinto(offset_x_final, offset_y_final, tamanho_celula_zoom)
        desenhar_jogador(jogador_x, jogador_y, angulo, offset_x_final, offset_y_final, tamanho_jogador_zoom)
        desenhar_inimigo(inimigo_x, inimigo_y, angulo_inimigo, offset_x_final, offset_y_final, tamanho_jogador_zoom)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        angulo_lanterna = math.atan2(
            (mouse_y + offset_y_final) - jogador_y * zoom,
            (mouse_x + offset_x_final) - jogador_x * zoom
        )

        if lanterna_ativa:
            cone = calcular_cone_de_luz(
                jogador_x, jogador_y, angulo_lanterna, offset_x_final, offset_y_final,
                alcance=80 * zoom,
                abertura=math.radians(30),
                num_rays=80
            )

            centro_x = jogador_x * zoom - offset_x_final
            centro_y = jogador_y * zoom - offset_y_final
            raio_luz = 25 * zoom

            sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 252))

            pygame.draw.polygon(sombra, (0, 0, 0, 0), cone) 
            pygame.draw.circle(sombra, (0, 0, 0, 0), (int(centro_x), int(centro_y)), int(raio_luz))  

            TELA.blit(sombra, (0, 0))
        else:
            centro_x = jogador_x * zoom - offset_x_final
            centro_y = jogador_y * zoom - offset_y_final

            sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 252))
            pygame.draw.circle(sombra, (0, 0, 0, 0), (int(centro_x), int(centro_y)), int(25 * zoom))
            TELA.blit(sombra, (0, 0))
            
# Barra lanterna▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
        barra_largura = 200
        barra_altura = 20
        barra_x = 20
        barra_y = 20

        pygame.draw.rect(TELA, (50, 50, 50), (barra_x, barra_y, barra_largura, barra_altura))

        if em_recarga:
            porcentagem = 1 - (tempo_restante_recarga / tempo_recarga)
            cor_barra = (255, 165, 0) 
        else:
            porcentagem = tempo_restante_lanterna / tempo_maximo_lanterna
            cor_barra = (255, 255, 0)

        pygame.draw.rect(TELA, cor_barra, (barra_x, barra_y, int(barra_largura * porcentagem), barra_altura))

        pygame.draw.rect(TELA, (255, 255, 255), (barra_x, barra_y, barra_largura, barra_altura), 2)

        fonte = pygame.font.Font(None, 24)
        if em_recarga:
            texto = f"Recarregando... {tempo_restante_recarga:.1f}s"
        else:
            texto = f"Lanterna: {tempo_restante_lanterna:.1f}s"

        render_texto = fonte.render(texto, True, (255, 255, 255))
        TELA.blit(render_texto, (barra_x, barra_y + barra_altura + 5))
#▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
    elif estado_jogo_atual == ESTADO_GAME_OVER:
        rect_tentar_novamente, rect_encerrar_jogo = desenhar_game_over()


    pygame.display.flip()
