import pygame
import sys
import math
from collections import deque
import random

# --- Inicialização do Pygame e Configurações da Tela ---
pygame.init()

LARGURA_JANELA_INICIAL = 800
ALTURA_JANELA_INICIAL = 600

TELA = pygame.display.set_mode((LARGURA_JANELA_INICIAL, ALTURA_JANELA_INICIAL))
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

TAMANHO_CELULA_BASE = 24
zoom = 1.5

pygame.display.set_caption("Labirinto")

# Constantes globais

COR_PAREDE = (50, 50, 50)
COR_CAMINHO = (200, 200, 200)
COR_JOGADOR = (255, 0, 0)
COR_INIMIGO = (0, 0, 255)
COR_BOLINHA = (0, 0, 0)
COR_TEXTO = (255, 255, 255) 
COR_BOTAO_NORMAL = (100, 100, 100) 
COR_BOTAO_HOVER = (150, 150, 150) 

ESTADO_JOGANDO = 0
ESTADO_FIM_DE_JOGO = 1

ESTADO_PATRULHA = 0
ESTADO_PERSEGUICAO = 1

VEL_PX_POR_SEG = 150
VEL_INIMIGO_PX_POR_SEG = 100
RAIO_VISAO_INIMIGO = TAMANHO_CELULA_BASE * 8
TEMPO_MEMORIA_PERSEGUICAO = 3.0 
RAIO_VIBRACAO_MAX = TAMANHO_CELULA_BASE * 10 
FORCA_VIBRACAO_MAX = 5 


# Mapa
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
if ALTURA_MAPA > 0:
    LARGURA_MAPA = len(labirinto[0])  
else:
    LARGURA_MAPA = 0
    print("ERRO: Labirinto está vazio, encerrando programa.")
    pygame.quit()
    sys.exit()

for i, row in enumerate(labirinto):
    if len(row) != LARGURA_MAPA:
        print(f"ERRO: Linha {i} tem comprimento {len(row)}, esperado {LARGURA_MAPA}, encerrando programa.")
        pygame.quit()
        sys.exit()

tamanho_jogador_base = TAMANHO_CELULA_BASE // 2

clock = pygame.time.Clock()

# --- Funções de Desenho ---
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

# --- Funções de Colisão e Conversão de Coordenadas ---
def pode_mover_celula(cx, cy):
    if not (0 <= cy < ALTURA_MAPA and 0 <= cx < LARGURA_MAPA):
        return False
    return labirinto[cy][cx] != '#'

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

# IA do Inimigo
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

# Funções de Inicialização/Reinicialização
def inicializar_jogo():
    global jogador_x, jogador_y, inimigo_x, inimigo_y, angulo, angulo_inimigo, \
           caminho_inimigo, indice_caminho, tempo_para_recalcular_inimigo_path, \
           tempo_para_recalcular_inimigo_patrol, inimigo_estado, alvo_patrulha_pixel, \
           tempo_sem_ver_jogador, estado_atual_do_jogo

    jogador_x, jogador_y = celula_para_pixel(1, 1)
    jogador_x += TAMANHO_CELULA_BASE / 2
    jogador_y += TAMANHO_CELULA_BASE / 2

    inimigo_x, inimigo_y = achar_posicao_inimigo()
    inimigo_x += TAMANHO_CELULA_BASE / 2
    inimigo_y += TAMANHO_CELULA_BASE / 2

    angulo = 0
    angulo_inimigo = 0
    caminho_inimigo = []
    indice_caminho = 0
    tempo_para_recalcular_inimigo_path = 0.5
    tempo_para_recalcular_inimigo_patrol = 1.0
    inimigo_estado = ESTADO_PATRULHA
    alvo_patrulha_pixel = None 
    tempo_sem_ver_jogador = TEMPO_MEMORIA_PERSEGUICAO
    estado_atual_do_jogo = ESTADO_JOGANDO

is_fullscreen = False

fonte_titulo = pygame.font.Font(None, 74)
fonte_botoes = pygame.font.Font(None, 50)

inicializar_jogo() 

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
        
        if estado_atual_do_jogo == ESTADO_FIM_DE_JOGO:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if tentar_denovo_rect.collidepoint(mouse_pos):
                    inicializar_jogo()
                
                if encerrar_jogo_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

    # Lógica do Jogo 
    if estado_atual_do_jogo == ESTADO_JOGANDO:
        delta = clock.tick(60) / 1000 

        tempo_para_recalcular_inimigo_path -= delta
        tempo_para_recalcular_inimigo_patrol -= delta
        tempo_sem_ver_jogador += delta

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

        # Visão/estado inimigo
        distancia_jogador_inimigo = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)
        
        jogador_foi_visto_agora = False
        if distancia_jogador_inimigo <= RAIO_VISAO_INIMIGO:
            if linha_de_visao(inimigo_x, inimigo_y, jogador_x, jogador_y):
                jogador_foi_visto_agora = True
        
        if jogador_foi_visto_agora:
            tempo_sem_ver_jogador = 0.0
            if inimigo_estado != ESTADO_PERSEGUICAO:
                print("Inimigo avistou o jogador! Perseguindo...")
                inimigo_estado = ESTADO_PERSEGUICAO
        else:
            if inimigo_estado == ESTADO_PERSEGUICAO:
                if tempo_sem_ver_jogador >= TEMPO_MEMORIA_PERSEGUICAO:
                    print("Inimigo perdeu o jogador de vista (tempo de memória expirou). Patrulhando...")
                    inimigo_estado = ESTADO_PATRULHA
            else:
                pass

        # Patrulha/perseguição
        if inimigo_estado == ESTADO_PERSEGUICAO:
            if tempo_para_recalcular_inimigo_path <= 0:
                inicio_celula = pixel_para_celula(inimigo_x, inimigo_y)
                destino_celula = pixel_para_celula(jogador_x, jogador_y) 
                caminho_inimigo = bfs_caminho(labirinto, inicio_celula, destino_celula)
                indice_caminho = 0 
                tempo_para_recalcular_inimigo_path = 0.5 

        elif inimigo_estado == ESTADO_PATRULHA:
            tempo_para_recalcular_inimigo_patrol -= delta
            if alvo_patrulha_pixel is None or tempo_para_recalcular_inimigo_patrol <= 0:
                encontrou_alvo = False
                tentativas = 0
                while not encontrou_alvo and tentativas < 50:
                    rand_cx = random.randint(0, LARGURA_MAPA - 1)
                    rand_cy = random.randint(0, ALTURA_MAPA - 1)
                    
                    if pode_mover_celula(rand_cx, rand_cy):
                        temp_alvo_x, temp_alvo_y = celula_para_pixel(rand_cx, rand_cy)
                        temp_alvo_x += TAMANHO_CELULA_BASE / 2
                        temp_alvo_y += TAMANHO_CELULA_BASE / 2

                        caminho_aleatorio = bfs_caminho(labirinto, pixel_para_celula(inimigo_x, inimigo_y), (rand_cx, rand_cy))
                        if caminho_aleatorio:
                            alvo_patrulha_pixel = (temp_alvo_x, temp_alvo_y)
                            caminho_inimigo = caminho_aleatorio
                            indice_caminho = 0
                            encontrou_alvo = True
                            tempo_para_recalcular_inimigo_patrol = 5.0 
                    tentativas += 1
                if not encontrou_alvo: 
                    caminho_inimigo = []
                    alvo_patrulha_pixel = None

        if caminho_inimigo and indice_caminho < len(caminho_inimigo):
            alvo_celula = caminho_inimigo[indice_caminho] 
            alvo_x = alvo_celula[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
            alvo_y = alvo_celula[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

            vetor_x = alvo_x - inimigo_x 
            vetor_y = alvo_y - inimigo_y 
            dist = math.hypot(vetor_x, vetor_y) 

            if dist < 2: 
                indice_caminho += 1
            else:
                if dist > 0:
                    dx_inimigo = vetor_x / dist
                    dy_inimigo = vetor_y / dist
                else:
                    dx_inimigo, dy_inimigo = 0, 0

                passo_inimigo_x = dx_inimigo * VEL_INIMIGO_PX_POR_SEG * delta 
                passo_inimigo_y = dy_inimigo * VEL_INIMIGO_PX_POR_SEG * delta 

                if pode_mover_pixel(inimigo_x + passo_inimigo_x, inimigo_y, tamanho_jogador_base * 0.45):
                    inimigo_x += passo_inimigo_x
                if pode_mover_pixel(inimigo_x, inimigo_y + passo_inimigo_y, tamanho_jogador_base * 0.45):
                    inimigo_y += passo_inimigo_y

                if dx_inimigo != 0 or dy_inimigo != 0:
                    angulo_inimigo = math.atan2(dy_inimigo, dx_inimigo)
        else:
            if inimigo_estado == ESTADO_PATRULHA:
                alvo_patrulha_pixel = None 

        # Colisão
        distancia_colisao = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)
        if distancia_colisao < (tamanho_jogador_base * 0.45 + tamanho_jogador_base * 0.45):
            estado_atual_do_jogo = ESTADO_FIM_DE_JOGO # Muda para o estado de fim de jogo

        # --- Atualização da Câmera (Offset de Visualização) ---
        tamanho_celula_zoom = TAMANHO_CELULA_BASE * zoom
        tamanho_jogador_zoom = tamanho_jogador_base * zoom

        offset_x = jogador_x * zoom - LARGURA_TELA / 2
        offset_y = jogador_y * zoom - ALTURA_TELA / 2

        max_offset_x = max(0, LARGURA_MAPA * tamanho_celula_zoom - LARGURA_TELA)
        max_offset_y = max(0, ALTURA_MAPA * tamanho_celula_zoom - ALTURA_TELA)

        offset_x = max(0, min(offset_x, max_offset_x))
        offset_y = max(0, min(offset_y, max_offset_y))

        # Vibração
        offset_vibracao_x = 0
        offset_vibracao_y = 0

        if inimigo_estado == ESTADO_PERSEGUICAO: 
            distancia_real_jogador_inimigo = math.hypot(jogador_x - inimigo_x, jogador_y - inimigo_y)
            if distancia_real_jogador_inimigo < RAIO_VIBRACAO_MAX:
                forca_vibracao = FORCA_VIBRACAO_MAX * (1 - min(1, distancia_real_jogador_inimigo / RAIO_VIBRACAO_MAX))
                offset_vibracao_x = random.uniform(-forca_vibracao, forca_vibracao)
                offset_vibracao_y = random.uniform(-forca_vibracao, forca_vibracao)

        offset_x += offset_vibracao_x
        offset_y += offset_vibracao_y

        # --- Desenho na Tela (durante o jogo) ---
        TELA.fill((0, 0, 0)) 
        desenhar_labirinto(offset_x, offset_y, tamanho_celula_zoom)
        desenhar_jogador(jogador_x, jogador_y, angulo, offset_x, offset_y, tamanho_jogador_zoom)
        desenhar_inimigo(inimigo_x, inimigo_y, angulo_inimigo, offset_x, offset_y, tamanho_jogador_zoom)

    # Game over place holder
    elif estado_atual_do_jogo == ESTADO_FIM_DE_JOGO:
        TELA.fill((0, 0, 0))

        texto_fim_de_jogo = fonte_titulo.render("GAME OVER", True, COR_TEXTO)
        texto_retangulo = texto_fim_de_jogo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 100))
        TELA.blit(texto_fim_de_jogo, texto_retangulo)

        tentar_denovo_texto = fonte_botoes.render("Tentar de novo", True, COR_TEXTO)
        tentar_denovo_rect = tentar_denovo_texto.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 20))
        
        mouse_pos = pygame.mouse.get_pos()
        if tentar_denovo_rect.collidepoint(mouse_pos):
            pygame.draw.rect(TELA, COR_BOTAO_HOVER, tentar_denovo_rect.inflate(20, 10))
        else:
            pygame.draw.rect(TELA, COR_BOTAO_NORMAL, tentar_denovo_rect.inflate(20, 10))
        TELA.blit(tentar_denovo_texto, tentar_denovo_rect)

        encerrar_jogo_texto = fonte_botoes.render("Encerrar jogo", True, COR_TEXTO)
        encerrar_jogo_rect = encerrar_jogo_texto.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 100))

        if encerrar_jogo_rect.collidepoint(mouse_pos):
            pygame.draw.rect(TELA, COR_BOTAO_HOVER, encerrar_jogo_rect.inflate(20, 10))
        else:
            pygame.draw.rect(TELA, COR_BOTAO_NORMAL, encerrar_jogo_rect.inflate(20, 10))
        TELA.blit(encerrar_jogo_texto, encerrar_jogo_rect)
        
    pygame.display.flip()