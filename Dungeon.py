import pygame
import sys
import math
import threading
import time
from collections import deque
import random

pygame.init()

offset_x_final = 0
offset_y_final = 0

LARGURA_JANELA_INICIAL = 800
ALTURA_JANELA_INICIAL = 600

TELA = pygame.display.set_mode((LARGURA_JANELA_INICIAL, ALTURA_JANELA_INICIAL))
LARGURA_TELA, ALTURA_TELA = TELA.get_size()

TAMANHO_CELULA_BASE = 24
zoom = 3.5  #jogo = 3.6

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
    "####################   #####################################",
    "##########           # C#####            C##################",
    "##C     ##       E   ########             ##################",
    "##      ##     CC       #####             ###########    C #",
    "##      ###    ####   #########   ####   ############      #",
    "##      ###    #####P##########   #### N ############      #",
    "####  ############## ##########   ####         ######      #",
    "####  #######                        #######   #######  ####",
    "####  #######                        #######   #######  ####",
    "#                ###############   ########## ######### ####",
    "#   N            ###############                        ####",
    "#  #########   ####################                     ####",
    "#  ##########P###############     ###    ###################",
    "#  #########   ##############      P     ###        ########",
    "#P##                   ######     ###    ###  #     ########",
    "#  #                      P       ##########  #     #####SS#",
    "#  #          N        ######                 ##### #####  #",
    "#                      ###########            ##### #####  #",
    "####                   ####C  ####            #####        #",
    "############    ############ #####            #####        #",
    "#####           ############              N   ##############",
    "#####  #####      ################            ##############",
    "#####  #########  ################                      ####",
    "#####  #########            P                           ####",
    "###     ########  ######## #######                      ####",
    "###     ########  ######## ############################P####",
    "###     ########           ####C  ###################   ####",
    "### ############           ###### ###            #### ######",
    "### ##############  N                                    ###",
    "###C##############                               ####### ###",
    "##################         ##########            ####C   ###",
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

def cortar_transparencia(imagem):
    rect = imagem.get_bounding_rect()
    imagem_cortada = imagem.subsurface(rect).copy()
    return imagem_cortada

try:
    player_image = pygame.image.load('sprites/player.png').convert_alpha()
    monstro_image = pygame.image.load('sprites/monstro.png').convert_alpha()
    chave_image = pygame.image.load('sprites/chave.png').convert_alpha()
    porta_image = pygame.image.load('sprites/porta.png').convert_alpha()
    porta_image = cortar_transparencia(porta_image)
    chave_2_image = pygame.image.load('sprites/chave_2.png').convert_alpha()
    portao_fechado_image = pygame.image.load('sprites/portao_fechado.png').convert_alpha()
    portao_fechado_image = cortar_transparencia(portao_fechado_image)

    textura_parede = pygame.image.load('sprites/parede_1.png').convert()
    textura_chao = pygame.image.load('sprites/chao.png').convert()

    manual_image = pygame.image.load('sprites/manual.png').convert_alpha()

except pygame.error as e:
    print(f"Erro ao carregar imagem: {e}. Certifique-se de que as imagens estão na pasta 'sprites'.")
    pygame.quit()
    sys.exit()

player_image = pygame.transform.smoothscale(player_image, (80, 80))     # Personagem
monstro_image = pygame.transform.smoothscale(monstro_image, (80, 80))   # Inimigo
chave_image = pygame.transform.smoothscale(chave_image, (60, 60))       # Chave
porta_image = pygame.transform.smoothscale(porta_image, (85, 85))       # Porta
portao_fechado_image = pygame.transform.smoothscale(portao_fechado_image, (85, 85))
chave_2_image = pygame.transform.smoothscale(chave_2_image, (60, 60))

textura_parede = pygame.transform.scale(textura_parede, (int(TAMANHO_CELULA_BASE * zoom), int(TAMANHO_CELULA_BASE * zoom)))
textura_chao = pygame.transform.scale(textura_chao, (int(TAMANHO_CELULA_BASE * zoom), int(TAMANHO_CELULA_BASE * zoom)))

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

            mapa_x = int((raio_x + offset_x) / (TAMANHO_CELULA_BASE * zoom))
            mapa_y = int((raio_y + offset_y) / (TAMANHO_CELULA_BASE * zoom))

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

            rect = pygame.Rect(
                x * tamanho_celula - offset_x,
                y * tamanho_celula - offset_y,
                tamanho_celula,
                tamanho_celula
            )

            if celula == '#':
                textura = pygame.transform.scale(textura_parede, (int(tamanho_celula), int(tamanho_celula)))
                TELA.blit(textura, rect)
            else:
                textura = pygame.transform.scale(textura_chao, (int(tamanho_celula), int(tamanho_celula)))
                TELA.blit(textura, rect)

            # Desenhar itens sobre o chão
            if celula == 'C':
                TELA.blit(chave_image, rect)
            elif celula == 'P':
                TELA.blit(porta_image, rect)
            elif celula == 'E':
                TELA.blit(chave_2_image, rect)
            elif celula == 'S':
                TELA.blit(portao_fechado_image, rect)
  
labirinto_original = [list(linha) for linha in labirinto_map]

def desenhar_jogador(x, y, angulo, offset_x, offset_y, tamanho_jogador_img, image):
    centro_x = x * zoom - offset_x
    centro_y = y * zoom - offset_y
    
    rotated_image = pygame.transform.rotate(image, -math.degrees(angulo))
    new_rect = rotated_image.get_rect(center=(int(centro_x), int(centro_y)))
    
    TELA.blit(rotated_image, new_rect.topleft)

def desenhar_inimigo(x, y, angulo, offset_x, offset_y, tamanho_inimigo_img, image):
    centro_x = x * zoom - offset_x
    centro_y = y * zoom - offset_y
    
    rect_original = image.get_rect(center=(int(centro_x), int(centro_y)))
    
    TELA.blit(image, rect_original.topleft)

# Colisão/conversão▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
def pode_mover_celula(cx, cy, ignorar_porta=False):
    if not (0 <= cy < ALTURA_MAPA and 0 <= cx < LARGURA_MAPA):
        return False

    celula = labirinto[cy][cx]

    if celula == '#':
        return False
    elif celula == 'P':
        # Porta bloqueia monstros e jogador sem chave
        return ignorar_porta  # só passa se for ignorar_porta=True
    return True



def pode_mover_pixel(px, py, raio, ignorar_porta=False):
    passos = 16
    for i in range(passos):
        angle = 2 * math.pi * i / passos
        check_x = px + math.cos(angle) * raio
        check_y = py + math.sin(angle) * raio
        cx = int(check_x // TAMANHO_CELULA_BASE)
        cy = int(check_y // TAMANHO_CELULA_BASE)
        if not pode_mover_celula(cx, cy, ignorar_porta=ignorar_porta):
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

def encontrar_posicoes_monstros():
    posicoes = []
    for y in range(ALTURA_MAPA):
        for x in range(LARGURA_MAPA):
            if labirinto[y][x] == 'N':
                px, py = celula_para_pixel(x, y)
                posicoes.append((px + TAMANHO_CELULA_BASE // 2, py + TAMANHO_CELULA_BASE // 2))
    return posicoes


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
                pode_mover_celula(nx, ny, ignorar_porta=False) and (nx, ny) not in visitado):
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
        if not pode_mover_celula(px, py, ignorar_porta=False):
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
ESTADO_TELA_INICIAL = -1
ESTADO_VITORIA = 2
ESTADO_INSTRUCOES = 3

# Estados dos monstros (mantidos como constantes)
ESTADO_PATRULHA = 0
ESTADO_PERSEGUICAO = 1
ESTADO_FUGA_LUZ = 2

# Controle de tempo do jogo
tempo_inicio = None
tempo_fim = None

# Jogador
jogador_x, jogador_y = 0.0, 0.0
angulo = 0
angulo_lanterna = 0.0
jogador_morto = False
quantidade_chaves = 0
quantidade_chaves_verdes = 0

# Configurações gerais
VEL_PX_POR_SEG = 110  # Velocidade do jogador
RAIO_VISAO_INIMIGO = TAMANHO_CELULA_BASE * 8  # exemplo de valor

VEL_MONSTRO_POR_SEG = 125 #velocidade do monstro  

# Vibração
vibração_ativa = False
FORCA_VIBRACAO_MAX = 5
RAIO_VIBRACAO_MAX = TAMANHO_CELULA_BASE * 20

# Configurações da lanterna
tempo_maximo_lanterna = 5    # segundos
tempo_recarga = 5            # segundos
tempo_restante_lanterna = tempo_maximo_lanterna
lanterna_ativa = False
tempo_lanterna_contando = False
em_recarga = False
tempo_restante_recarga = 0

estado_jogo_atual = ESTADO_TELA_INICIAL

monstros = []

cone_luz_global = []

from threading import Semaphore

semaforo_perseguicao = Semaphore(1)

# Configurações da lanterna▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
tempo_maximo_lanterna = 5   
tempo_recarga = 5   
tempo_restante_lanterna = tempo_maximo_lanterna
lanterna_ativa = False
tempo_lanterna_contando = False
em_recarga = False
tempo_restante_recarga = 0

estado_jogo_atual = ESTADO_TELA_INICIAL

class Monstro:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.estado = ESTADO_PATRULHA
        self.caminho = []
        self.indice_caminho = 0
        self.vibracao_ativa = False
                
        self.necessita_nova_fuga = False

        self.thread = threading.Thread(target=self.atualizar)
        self.thread.daemon = True
        self.terminar = False
        self.thread.start()

    def atualizar(self):
        global jogador_morto, estado_jogo_atual, cone_luz_global, offset_x_final, offset_y_final

        while not self.terminar:
            if estado_jogo_atual != ESTADO_JOGANDO:
                time.sleep(0.1)
                continue

            # Verifica se está dentro da luz
            if lanterna_ativa and cone_luz_global:
                ponto_monstro_tela = (self.x * zoom - offset_x_final, self.y * zoom - offset_y_final)
                centro_x = jogador_x * zoom - offset_x_final
                centro_y = jogador_y * zoom - offset_y_final

                dx = ponto_monstro_tela[0] - centro_x
                dy = ponto_monstro_tela[1] - centro_y

                distancia = math.hypot(dx, dy)
                angulo_para_monstro = math.atan2(dy, dx)
                diferenca_angulo = abs((angulo_lanterna - angulo_para_monstro + math.pi) % (2 * math.pi) - math.pi)

                # Se o monstro está na frente da lanterna e próximo
                if lanterna_ativa and distancia < 80 * zoom and diferenca_angulo < math.radians(15):
                    if self.estado != ESTADO_FUGA_LUZ:
                        if self.estado == ESTADO_PERSEGUICAO:
                            if semaforo_perseguicao._value < 1:
                                try:
                                    semaforo_perseguicao.release()
                                except ValueError:
                                    pass
                        self.estado = ESTADO_FUGA_LUZ
                        self.vibracao_ativa = False
                        self.necessita_nova_fuga = True
                else:
                    if self.estado == ESTADO_FUGA_LUZ:
                        self.estado = ESTADO_PATRULHA
                        self.necessita_nova_fuga = False
                        self.caminho = []
                        self.indice_caminho = 0
                        self.patrulhar()


            else:
                if math.hypot(jogador_x - self.x, jogador_y - self.y) < RAIO_VISAO_INIMIGO and linha_de_visao(self.x, self.y, jogador_x, jogador_y):
                    if self.estado != ESTADO_PERSEGUICAO and self.estado != ESTADO_FUGA_LUZ:
                        if semaforo_perseguicao.acquire(blocking=False):
                            self.estado = ESTADO_PERSEGUICAO
                            self.vibracao_ativa = True

                else:
                    if self.estado == ESTADO_PERSEGUICAO:
                        self.estado = ESTADO_PATRULHA
                        self.vibracao_ativa = False
                        if semaforo_perseguicao._value < 1:
                            try:
                                semaforo_perseguicao.release()
                            except ValueError:
                                pass

            # Comportamento
            if self.estado == ESTADO_PATRULHA:
                if not self.caminho or self.indice_caminho >= len(self.caminho):
                    self.patrulhar()

            elif self.estado == ESTADO_PERSEGUICAO:
                self.perseguir()

            self.mover_ao_alvo()

            # Colisão com jogador
            if self.estado != ESTADO_FUGA_LUZ:
                distancia = math.hypot(jogador_x - self.x, jogador_y - self.y)
                if distancia < 20:
                    jogador_morto = True
                    estado_jogo_atual = ESTADO_GAME_OVER

            if self.necessita_nova_fuga:
                sucesso = self.fugir_do_jogador()
                if not sucesso:
                    # Se a fuga falhar, tenta outra direção aleatória
                    for _ in range(5):
                        angulo = random.uniform(0, 2 * math.pi)
                        dx = math.cos(angulo)
                        dy = math.sin(angulo)
                        destino_x = self.x + dx * TAMANHO_CELULA_BASE * 6
                        destino_y = self.y + dy * TAMANHO_CELULA_BASE * 6

                        destino = pixel_para_celula(destino_x, destino_y)
                        inicio = pixel_para_celula(self.x, self.y)
                        caminho = bfs_caminho(labirinto, inicio, destino)
                        if caminho:
                            self.caminho = caminho
                            self.indice_caminho = 0
                            break
                self.necessita_nova_fuga = False

            if self.estado == ESTADO_PATRULHA and (not self.caminho or self.indice_caminho >= len(self.caminho)):
                self.patrulhar()

            time.sleep(0.02)

    def patrulhar(self):
        tentativas = 20  # número máximo de tentativas
        for _ in range(tentativas):
            destino = (random.randint(1, LARGURA_MAPA-2), random.randint(1, ALTURA_MAPA-2))

            # Verifica se o destino está longe do jogador
            destino_px = destino[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
            destino_py = destino[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
            distancia_do_jogador = math.hypot(destino_px - jogador_x, destino_py - jogador_y)

            if distancia_do_jogador < TAMANHO_CELULA_BASE * 5:
                continue  # Pula destinos muito próximos do jogador

            inicio = pixel_para_celula(self.x, self.y)
            caminho = bfs_caminho(labirinto, inicio, destino)
            if caminho:  # só aceita caminho válido
                self.caminho = caminho
                self.indice_caminho = 0
                return

        # Se não achou nenhum caminho, evita travar:
        self.caminho = []
        self.indice_caminho = 0


    def perseguir(self):
        destino = pixel_para_celula(jogador_x, jogador_y)
        inicio = pixel_para_celula(self.x, self.y)
        self.caminho = bfs_caminho(labirinto, inicio, destino)
        self.indice_caminho = 0

    def mover_ao_alvo(self):
        if self.caminho and self.indice_caminho < len(self.caminho):
            alvo = self.caminho[self.indice_caminho]
            alvo_x = alvo[0] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2
            alvo_y = alvo[1] * TAMANHO_CELULA_BASE + TAMANHO_CELULA_BASE / 2

            vetor_x = alvo_x - self.x
            vetor_y = alvo_y - self.y
            dist = math.hypot(vetor_x, vetor_y)

            if dist < 3:
                self.indice_caminho += 1
            elif dist > 0:
                dx = vetor_x / dist
                dy = vetor_y / dist

                passo_x = dx * VEL_MONSTRO_POR_SEG * 0.02 
                passo_y = dy * VEL_MONSTRO_POR_SEG * 0.02


                if pode_mover_pixel(self.x + passo_x, self.y, tamanho_jogador_base * 0.45):
                    self.x += passo_x
                if pode_mover_pixel(self.x, self.y + passo_y, tamanho_jogador_base * 0.45):
                    self.y += passo_y

                self.angulo = math.atan2(dy, dx)

        elif not self.caminho:
            # Movimento de emergência aleatório quando parado
            dx = random.choice([-1, 0, 1])
            dy = random.choice([-1, 0, 1])
            passo_x = dx * 2
            passo_y = dy * 2

            # Só move se não bater em parede
            if pode_mover_pixel(self.x + passo_x, self.y, tamanho_jogador_base * 0.45):
                self.x += passo_x
            if pode_mover_pixel(self.x, self.y + passo_y, tamanho_jogador_base * 0.45):
                self.y += passo_y

    def desenhar(self, offset_x, offset_y):
        desenhar_inimigo(self.x, self.y, self.angulo, offset_x, offset_y, tamanho_jogador_base * zoom, monstro_image)

    def fugir_do_jogador(self):
        dx = self.x - jogador_x
        dy = self.y - jogador_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
        else:
            dx = random.choice([-1, 1])
            dy = random.choice([-1, 1])

        tentativas = 5
        for _ in range(tentativas):
            fator = TAMANHO_CELULA_BASE * (6 + random.uniform(0, 3))
            destino_x = self.x + dx * fator
            destino_y = self.y + dy * fator

            destino = pixel_para_celula(destino_x, destino_y)
            inicio = pixel_para_celula(self.x, self.y)
            caminho = bfs_caminho(labirinto, inicio, destino)

            if caminho:
                self.caminho = caminho
                self.indice_caminho = 0
                return True

        self.caminho = []
        self.indice_caminho = 0
        return False


# Reinicializção/game over▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
def reset_game():
    global jogador_x, jogador_y, angulo, angulo_lanterna, tempo_inicio, tempo_fim
    global vibração_ativa, jogador_morto, estado_jogo_atual
    global quantidade_chaves, em_recarga, tempo_restante_lanterna, tempo_restante_recarga
    global monstros
    global labirinto
    global quantidade_chaves_verdes
    
    # Libera o semáforo no reset caso esteja travado
    while semaforo_perseguicao._value < 1:
        try:
            semaforo_perseguicao.release()
        except ValueError:
            break

    for monstro in monstros:
        monstro.terminar = True
        if monstro.thread.is_alive():
            monstro.thread.join()  
    monstros.clear()
    
    tempo_inicio = time.time()
    tempo_fim = None

    jogador_x_inicial, jogador_y_inicial = celula_para_pixel(13, 8)
    jogador_x = jogador_x_inicial + TAMANHO_CELULA_BASE / 2
    jogador_y = jogador_y_inicial + TAMANHO_CELULA_BASE / 2

    angulo = 0
    angulo_lanterna = 0.0

    vibração_ativa = False
    jogador_morto = False
    estado_jogo_atual = ESTADO_JOGANDO
    
    quantidade_chaves = 0
    quantidade_chaves_verdes = 0
    em_recarga = False
    tempo_restante_lanterna = tempo_maximo_lanterna
    tempo_restante_recarga = 0

    labirinto = [linha.copy() for linha in labirinto_original]

    # Cria novos monstros com base nas posições do mapa
    monstros = []
    posicoes = encontrar_posicoes_monstros()
    for px, py in posicoes:
        monstros.append(Monstro(px, py))

def desenhar_tela_inicial():
    fonte_titulo = pygame.font.Font(None, 100)
    fonte_botao = pygame.font.Font(None, 60)

    TELA.fill((0, 0, 0))

    mouse_pos = pygame.mouse.get_pos()

    texto_titulo = fonte_titulo.render("Dungeon Game", True, COR_TEXTO)
    rect_titulo = texto_titulo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 150))
    TELA.blit(texto_titulo, rect_titulo)

    # PLAY
    texto_play = fonte_botao.render("PLAY", True, COR_TEXTO)
    rect_play = pygame.Rect(0, 0, 250, 80)
    rect_play.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 50)

    # INSTRUÇÕES
    texto_instr = fonte_botao.render("INSTRUÇÕES", True, COR_TEXTO)
    rect_instr = pygame.Rect(0, 0, 300, 80)
    rect_instr.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 150)

    # SAIR
    texto_sair = fonte_botao.render("SAIR", True, COR_TEXTO)
    rect_sair = pygame.Rect(0, 0, 250, 80)
    rect_sair.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 250)

    cor_btn_sair = COR_BOTAO_NORMAL
    if rect_sair.collidepoint(mouse_pos):
        cor_btn_sair = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_sair, rect_sair, border_radius=12)
    TELA.blit(texto_sair, texto_sair.get_rect(center=rect_sair.center))

    cor_btn_play = COR_BOTAO_NORMAL
    if rect_play.collidepoint(mouse_pos):
        cor_btn_play = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_play, rect_play, border_radius=12)
    TELA.blit(texto_play, texto_play.get_rect(center=rect_play.center))

    cor_btn_instr = COR_BOTAO_NORMAL
    if rect_instr.collidepoint(mouse_pos):
        cor_btn_instr = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_instr, rect_instr, border_radius=12)
    TELA.blit(texto_instr, texto_instr.get_rect(center=rect_instr.center))

    return rect_play, rect_instr, rect_sair

def desenhar_instrucoes():
    TELA.fill((0, 0, 0))

    largura_img, altura_img = manual_image.get_size()

    fator = ALTURA_TELA / altura_img

    nova_largura = int(largura_img * fator)
    nova_altura = ALTURA_TELA  # porque queremos preencher altura total

    manual_scaled = pygame.transform.scale(manual_image, (nova_largura, nova_altura))
    rect_manual = manual_scaled.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))

    TELA.blit(manual_scaled, rect_manual)


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

    texto_encerrar_jogo = fonte_botao.render("Voltar ao Menu", True, COR_TEXTO)
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

def desenhar_vitoria():
    fonte_titulo = pygame.font.Font(None, 80)
    fonte_botao = pygame.font.Font(None, 50)

    sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    sombra.fill((0, 0, 0, 180))
    TELA.blit(sombra, (0,0))

    texto_vitoria = fonte_titulo.render("Parabéns!", True, (0, 255, 0))
    rect_vitoria = texto_vitoria.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 150))
    TELA.blit(texto_vitoria, rect_vitoria)

    texto_msg = fonte_botao.render("Você concluiu a Dungeon!", True, COR_TEXTO)
    rect_msg = texto_msg.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 80))
    TELA.blit(texto_msg, rect_msg)

    if tempo_inicio is not None and tempo_fim is not None:
        tempo_total = tempo_fim - tempo_inicio
        texto_tempo = fonte_botao.render(f"Tempo: {tempo_total:.2f} segundos", True, COR_TEXTO)
        rect_tempo = texto_tempo.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 30))
        TELA.blit(texto_tempo, rect_tempo)

    texto_voltar_menu = fonte_botao.render("Voltar ao Menu", True, COR_TEXTO)
    rect_voltar_menu = pygame.Rect(0, 0, 300, 70)
    rect_voltar_menu.center = (LARGURA_TELA // 2, ALTURA_TELA // 2 + 140)

    mouse_pos = pygame.mouse.get_pos()

    cor_btn_voltar = COR_BOTAO_NORMAL
    if rect_voltar_menu.collidepoint(mouse_pos):
        cor_btn_voltar = COR_BOTAO_HOVER
    pygame.draw.rect(TELA, cor_btn_voltar, rect_voltar_menu, border_radius=10)
    TELA.blit(texto_voltar_menu, texto_voltar_menu.get_rect(center=rect_voltar_menu.center))

    return None, rect_voltar_menu

# Inicialização do jogo▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
thread_inimigo_obj = None
estado_jogo_atual = ESTADO_TELA_INICIAL

rect_play = pygame.Rect(0, 0, 0, 0)
rect_instr = pygame.Rect(0, 0, 0, 0)

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

            if event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    TELA = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    TELA = pygame.display.set_mode((LARGURA_JANELA_INICIAL, ALTURA_JANELA_INICIAL))
                LARGURA_TELA, ALTURA_TELA = TELA.get_size()

        if event.type == pygame.QUIT:
            if thread_inimigo_obj and thread_inimigo_obj.is_alive():
                terminar_thread_inimigo = True
                thread_inimigo_obj.join()
            pygame.quit()
            sys.exit()


        if estado_jogo_atual == ESTADO_TELA_INICIAL:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if rect_play.collidepoint(mouse_pos):
                    reset_game()
                    pygame.time.wait(100)
                elif rect_instr.collidepoint(mouse_pos):
                    estado_jogo_atual = ESTADO_INSTRUCOES
                elif rect_sair.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        elif estado_jogo_atual == ESTADO_GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if rect_tentar_novamente.collidepoint(mouse_pos):
                    terminar_thread_inimigo = True
                    if thread_inimigo_obj and thread_inimigo_obj.is_alive():
                        thread_inimigo_obj.join()
                    reset_game()

                elif rect_encerrar_jogo.collidepoint(mouse_pos):
                    # Finaliza os monstros
                    for monstro in monstros:
                        monstro.terminar = True
                        if monstro.thread.is_alive():
                            monstro.thread.join()
                    monstros.clear()
                    estado_jogo_atual = ESTADO_TELA_INICIAL

        elif estado_jogo_atual == ESTADO_VITORIA:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if rect_voltar_menu and rect_voltar_menu.collidepoint(mouse_pos):
                    # Finaliza os threads dos monstros
                    for monstro in monstros:
                        monstro.terminar = True
                        if monstro.thread.is_alive():
                            monstro.thread.join()
                    monstros.clear()
                    estado_jogo_atual = ESTADO_TELA_INICIAL

        elif estado_jogo_atual == ESTADO_INSTRUCOES:
            if event.type == pygame.MOUSEBUTTONDOWN:
                estado_jogo_atual = ESTADO_TELA_INICIAL


    if estado_jogo_atual == ESTADO_JOGANDO:
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

            if pode_mover_pixel(jogador_x + passo_x, jogador_y, tamanho_jogador_base * 0.45, ignorar_porta=(quantidade_chaves > 0)):
                jogador_x += passo_x
            if pode_mover_pixel(jogador_x, jogador_y + passo_y, tamanho_jogador_base * 0.45, ignorar_porta=(quantidade_chaves > 0)):
                jogador_y += passo_y


            angulo = math.atan2(dy, dx)

            # Coordenadas do jogador no mapa
            celula_jogador_x, celula_jogador_y = pixel_para_celula(jogador_x, jogador_y)

            # Coletar chave
            if labirinto[celula_jogador_y][celula_jogador_x] == 'C':
                labirinto[celula_jogador_y][celula_jogador_x] = ' '
                quantidade_chaves += 1

            if labirinto[celula_jogador_y][celula_jogador_x] == 'E':
                labirinto[celula_jogador_y][celula_jogador_x] = ' '
                quantidade_chaves_verdes += 1


            # Usar chave na porta
            elif labirinto[celula_jogador_y][celula_jogador_x] == 'P':
                if quantidade_chaves > 0:
                    labirinto[celula_jogador_y][celula_jogador_x] = ' '
                    quantidade_chaves -= 1

            elif labirinto[celula_jogador_y][celula_jogador_x] == 'S':
                if quantidade_chaves_verdes > 0:
                    tempo_fim = time.time()
                    estado_jogo_atual = ESTADO_VITORIA

        # Estes cálculos devem vir DEPOIS do if de movimento, mas FORA dele:
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

        mouse_moved = False
        novo_mouse_x, novo_mouse_y = pygame.mouse.get_pos()
        if (novo_mouse_x, novo_mouse_y) != (mouse_x, mouse_y):
            mouse_moved = True
        mouse_x, mouse_y = novo_mouse_x, novo_mouse_y

        if lanterna_ativa:
            cone_luz_global = calcular_cone_de_luz(
                jogador_x, jogador_y, angulo_lanterna, offset_x_final, offset_y_final,
                alcance=80 * zoom,
                abertura=math.radians(30),
                num_rays=40
            )
        else:
            cone_luz_global = []

# Lógica vibração▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
        for monstro in monstros:
            distancia_jogador_inimigo_para_vibracao = math.hypot(jogador_x - monstro.x, jogador_y - monstro.y)

            if monstro.vibracao_ativa:
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
        desenhar_jogador(jogador_x, jogador_y, angulo, offset_x_final, offset_y_final, tamanho_jogador_zoom, player_image)

        for monstro in monstros:
            monstro.desenhar(offset_x_final, offset_y_final)

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
            sombra.fill((0, 0, 0, 180))

            pygame.draw.polygon(sombra, (0, 0, 0, 0), cone) 
            pygame.draw.circle(sombra, (0, 0, 0, 0), (int(centro_x), int(centro_y)), int(raio_luz))  

            TELA.blit(sombra, (0, 0))
        else:
            centro_x = jogador_x * zoom - offset_x_final
            centro_y = jogador_y * zoom - offset_y_final

            sombra = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            sombra.fill((0, 0, 0, 180))
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
            texto = f"Charging... {tempo_restante_recarga:.1f}s"
        else:
            texto = f"Lantern: {tempo_restante_lanterna:.1f}s"

        render_texto = fonte.render(texto, True, (255, 255, 255))
        TELA.blit(render_texto, (barra_x, barra_y + barra_altura + 5))

        # Texto de chaves na tela
        texto_chaves = f"Chaves: {quantidade_chaves}"
        render_chaves = fonte.render(texto_chaves, True, (255, 255, 255))
        TELA.blit(render_chaves, (barra_x, barra_y + barra_altura + 30))

        texto_chaves_verdes = f"Chave Final: {quantidade_chaves_verdes}"
        render_chaves_verdes = fonte.render(texto_chaves_verdes, True, (0, 255, 0))
        TELA.blit(render_chaves_verdes, (barra_x, barra_y + barra_altura + 50))


#▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
    if estado_jogo_atual == ESTADO_TELA_INICIAL:
        rect_play, rect_instr, rect_sair = desenhar_tela_inicial()

    elif estado_jogo_atual == ESTADO_INSTRUCOES:
        desenhar_instrucoes()

    elif estado_jogo_atual == ESTADO_GAME_OVER:
        rect_tentar_novamente, rect_encerrar_jogo = desenhar_game_over()

    elif estado_jogo_atual == ESTADO_VITORIA:
        rect_reiniciar, rect_voltar_menu = desenhar_vitoria()

    pygame.display.flip()
