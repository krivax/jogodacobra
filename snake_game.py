import pygame
import sys
import random
import time
import math
import json
import os
# import requests  # Comentado temporariamente

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()  # Inicialização do mixer para sons

# Constantes
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Cores
BACKGROUND_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)  # Verde
FOOD_COLOR = (255, 165, 0)  # Laranja
SPECIAL_FOOD_COLOR = (255, 215, 0)  # Dourado
DANGER_FOOD_COLOR = (128, 128, 128)  # Cinza
TEXT_COLOR = (255, 255, 255)  # Branco
INPUT_BOX_COLOR = (50, 50, 50)  # Cinza escuro para caixa de entrada
INPUT_TEXT_COLOR = (255, 255, 255)  # Branco para texto de entrada
BUTTON_COLOR = (0, 100, 0)  # Verde escuro para botões
BUTTON_HOVER_COLOR = (0, 150, 0)  # Verde mais claro para hover
BORDER_COLOR = (255, 255, 255)  # Branco para as bordas (alterado para branco)

# Área segura para o contador de pontuação (em número de células da grade)
SAFE_ZONE_HEIGHT = 2

# Direções
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.length = 1
        # Garantir que a cobra comece abaixo da área segura
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + SAFE_ZONE_HEIGHT)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0
        self.lives = 2  # Agora a cobra tem 2 vidas
        self.alive = True
        self.speed_multiplier = 1.0  # Multiplicador de velocidade inicial
    
    def get_head_position(self):
        return self.positions[0]
    
    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def move(self):
        if not self.alive:
            return
            
        head = self.get_head_position()
        x, y = self.direction
        new_x = head[0] + x
        new_y = head[1] + y
        new_position = (new_x, new_y)
        
        # Verificar colisão com as paredes ou área do contador
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT or new_y < SAFE_ZONE_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.alive = False
                # Som de morte será tocado na função principal
            else:
                # Reposicionar a cobra no centro após perder uma vida
                self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + SAFE_ZONE_HEIGHT)]
                # Som de perda de vida será tocado na função principal
            return
        
        # Verificar colisão com o próprio corpo
        if new_position in self.positions[1:]:
            self.lives -= 1
            if self.lives <= 0:
                self.alive = False
                # Som de morte será tocado na função principal
            else:
                # Reposicionar a cobra no centro após perder uma vida
                self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + SAFE_ZONE_HEIGHT)]
                # Som de perda de vida será tocado na função principal
            return
        
        # Som de movimento será tocado na função principal
        
        self.positions.insert(0, new_position)
        if len(self.positions) > self.length:
            self.positions.pop()
    
    def draw(self, surface):
        for i, p in enumerate(self.positions):
            if i == 0:  # Cabeça da cobra (arredondada)
                pygame.draw.circle(surface, SNAKE_COLOR, 
                                  (p[0] * GRID_SIZE + GRID_SIZE // 2, 
                                   p[1] * GRID_SIZE + GRID_SIZE // 2), 
                                  GRID_SIZE // 2)
            else:  # Corpo da cobra
                rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), 
                                  (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(surface, SNAKE_COLOR, rect)

class DangerFood:
    def __init__(self):
        self.position = (0, 0)
        self.color = DANGER_FOOD_COLOR
        self.spawn_time = 0
        self.active = False
        self.randomize_position([])
    
    def randomize_position(self, snake_positions):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(SAFE_ZONE_HEIGHT, GRID_HEIGHT - 1))
        # Evitar que a comida apareça onde a cobra está
        while self.position in snake_positions:
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                            random.randint(SAFE_ZONE_HEIGHT, GRID_HEIGHT - 1))
        self.spawn_time = time.time()
        self.active = True
    
    def draw(self, surface):
        if not self.active:
            return False
            
        if time.time() - self.spawn_time > 2:
            self.active = False
            return False
            
        # Desenhar caveira
        center_x = self.position[0] * GRID_SIZE + GRID_SIZE // 2
        center_y = self.position[1] * GRID_SIZE + GRID_SIZE // 2
        radius = GRID_SIZE // 2
        
        # Cabeça da caveira (círculo)
        pygame.draw.circle(surface, DANGER_FOOD_COLOR, (center_x, center_y), radius)
        
        # Olhos
        eye_radius = radius // 3
        pygame.draw.circle(surface, BACKGROUND_COLOR, (center_x - radius//2, center_y - radius//4), eye_radius)
        pygame.draw.circle(surface, BACKGROUND_COLOR, (center_x + radius//2, center_y - radius//4), eye_radius)
        
        # Nariz (triângulo)
        nose_points = [
            (center_x, center_y),
            (center_x - radius//3, center_y + radius//3),
            (center_x + radius//3, center_y + radius//3)
        ]
        pygame.draw.polygon(surface, BACKGROUND_COLOR, nose_points)
        
        # Boca (linha curva)
        mouth_rect = pygame.Rect(center_x - radius//2, center_y + radius//4, radius, radius//2)
        pygame.draw.arc(surface, BACKGROUND_COLOR, mouth_rect, 0, math.pi, 2)
        
        # Dentes
        tooth_width = radius // 4
        for i in range(3):
            x = center_x - radius//2 + i * tooth_width
            pygame.draw.rect(surface, BACKGROUND_COLOR, 
                           (x, center_y + radius//2, tooth_width//2, radius//4))
        
        return True

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = FOOD_COLOR
        self.type = 'normal'  # normal, special
        self.randomize_position([])
    
    def randomize_position(self, snake_positions):
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(SAFE_ZONE_HEIGHT, GRID_HEIGHT - 1))
        # Evitar que a comida apareça onde a cobra está
        while self.position in snake_positions:
            self.position = (random.randint(0, GRID_WIDTH - 1), 
                            random.randint(SAFE_ZONE_HEIGHT, GRID_HEIGHT - 1))
        
        # Chance de 10% para comida especial
        if random.random() < 0.1:
            self.type = 'special'
            self.color = SPECIAL_FOOD_COLOR
        else:
            self.type = 'normal'
            self.color = FOOD_COLOR
    
    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), 
                      (GRID_SIZE, GRID_SIZE))
        
        if self.type == 'special':
            # Desenha um símbolo especial (estrela)
            center = (self.position[0] * GRID_SIZE + GRID_SIZE // 2, 
                     self.position[1] * GRID_SIZE + GRID_SIZE // 2)
            radius = GRID_SIZE // 2
            points = []
            for i in range(5):
                # Pontos externos da estrela
                x = center[0] + radius * math.cos(math.pi/2 + i * 2*math.pi/5)
                y = center[1] - radius * math.sin(math.pi/2 + i * 2*math.pi/5)
                points.append((x, y))
                # Pontos internos da estrela
                x = center[0] + radius/2 * math.cos(math.pi/2 + (i+0.5) * 2*math.pi/5)
                y = center[1] - radius/2 * math.sin(math.pi/2 + (i+0.5) * 2*math.pi/5)
                points.append((x, y))
            pygame.draw.polygon(surface, self.color, points)
        else:
            pygame.draw.rect(surface, self.color, rect)
        
        return True

def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont('arial', size)
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def save_score(name, code, score):
    # Carregar ranking existente
    ranking = []
    if os.path.exists('ranking.json'):
        try:
            with open('ranking.json', 'r') as f:
                ranking = json.load(f)
                # Adicionar código padrão para entradas antigas
                for entry in ranking:
                    if 'code' not in entry:
                        entry['code'] = '0000'
        except:
            ranking = []
    
    # Adicionar nova pontuação
    ranking.append({'name': name, 'code': code, 'score': score})
    
    # Ordenar por pontuação (maior para menor)
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)
    
    # Manter apenas os top 10
    ranking = ranking[:10]
    
    # Salvar ranking atualizado em JSON
    with open('ranking.json', 'w') as f:
        json.dump(ranking, f)
    
    # Salvar ranking em formato TXT para fácil visualização
    with open('ranking.txt', 'w', encoding='utf-8') as f:
        f.write('=== RANKING DO JOGO DA COBRINHA ===\n\n')
        for i, entry in enumerate(ranking, 1):
            f.write(f"{i}. {entry['name']} ({entry['code']}): {entry['score']} pontos\n")
    
    return ranking

def show_ranking(surface):
    surface.fill(BACKGROUND_COLOR)
    draw_text(surface, 'RANKING', 50, WIDTH // 2, 50)
    
    ranking = []
    # Tentar ler do arquivo TXT primeiro
    if os.path.exists('ranking.txt'):
        try:
            with open('ranking.txt', 'r') as f:
                lines = f.readlines()
                # Pular o cabeçalho
                for line in lines[2:]:
                    if line.strip():
                        # Extrair nome, código e pontuação da linha
                        parts = line.strip().split(': ')
                        if len(parts) == 2:
                            name_code = parts[0].split('. ')[1]
                            if '(' in name_code and ')' in name_code:
                                name = name_code.split(' (')[0]
                                code = name_code.split('(')[1].split(')')[0]
                            else:
                                name = name_code
                                code = '0000'  # Código padrão para rankings antigos
                            score = int(parts[1].split(' ')[0])
                            ranking.append({'name': name, 'code': code, 'score': score})
        except:
            # Se falhar, tentar ler do JSON
            if os.path.exists('ranking.json'):
                try:
                    with open('ranking.json', 'r') as f:
                        ranking = json.load(f)
                        # Adicionar código padrão para entradas antigas
                        for entry in ranking:
                            if 'code' not in entry:
                                entry['code'] = '0000'
                except:
                    ranking = []
    
    if not ranking:
        draw_text(surface, 'Nenhuma pontuação registrada ainda', 30, WIDTH // 2, HEIGHT // 2)
    else:
        # Mostrar todos os rankings
        for i, entry in enumerate(ranking):
            draw_text(surface, f"{i+1}. {entry['name']} ({entry['code']}): {entry['score']} pontos", 25, WIDTH // 2, 120 + i * 40)
    
    draw_text(surface, 'Pressione ESC para voltar', 20, WIDTH // 2, HEIGHT - 50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False

def log_api_result(player_name, player_code, pontos, is_victory, status_code, response_text, sucesso):
    from datetime import datetime
    with open('api_log.txt', 'a', encoding='utf-8') as log_file:
        data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'SUCESSO' if sucesso else 'FALHA'
        log_file.write(f"[{data_hora}] {status} | Jogador: {player_name} | Código: {player_code} | Pontos: {pontos} | Vitória: {is_victory} | Status HTTP: {status_code} | Resposta: {response_text}\n")

def send_score_to_api(player_name, player_code, score, is_victory):
    # Função temporariamente desativada
    print("Envio para API temporariamente desativado")
    return
    
    # Código comentado temporariamente
    """
    try:
        # Preparar os dados para enviar à API
        pontos = 10 if is_victory else 5
        data = {
            "jogador": player_name,
            "jogo": "jogo da cobra",
            "ponto": pontos,
            "codigo": player_code
        }
        
        # URL da API
        api_url = "https://aula-h986.onrender.com/scores"
        
        # Enviar requisição POST para a API
        response = requests.post(api_url, json=data)
        
        # Considerar sucesso se status for 200 ou 201
        if response.status_code in (200, 201):
            print("Pontuação enviada com sucesso para a API!")
            print(f"Resposta da API: {response.text}")
            log_api_result(player_name, player_code, pontos, is_victory, response.status_code, response.text, True)
        else:
            print(f"Erro ao enviar pontuação para a API. Status code: {response.status_code}")
            print(f"Resposta da API: {response.text}")
            log_api_result(player_name, player_code, pontos, is_victory, response.status_code, response.text, False)
            
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        log_api_result(player_name, player_code, 10 if is_victory else 5, is_victory, 'ERRO', str(e), False)
    """

def test_api_connection():
    # Função temporariamente desativada
    print("\n=== Teste de API temporariamente desativado ===")
    return
    
    # Código comentado temporariamente
    """
    print("\n=== Testando conexão com a API ===")
    try:
        # Dados de teste
        test_data = {
            "jogador": "Teste",
            "jogo": "jogo da cobra",
            "ponto": 10,
            "codigo": "TESTE123"
        }
        
        # URL da API
        api_url = "https://aula-h986.onrender.com/scores"
        
        print("Enviando dados de teste para a API...")
        print(f"Dados: {test_data}")
        
        # Enviar requisição POST para a API
        response = requests.post(api_url, json=test_data)
        
        # Verificar se a requisição foi bem sucedida
        if response.status_code in (200, 201):
            print("✅ Teste bem sucedido! API respondeu corretamente.")
            print(f"Resposta da API: {response.text}")
        else:
            print(f"❌ Erro na comunicação com a API. Status code: {response.status_code}")
            print(f"Resposta da API: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
    
    print("=== Fim do teste ===\n")
    """

def game_over_screen(surface, score, player_name, player_code):
    surface.fill(BACKGROUND_COLOR)
    draw_text(surface, 'GAME OVER', 50, WIDTH // 2, HEIGHT // 4)
    draw_text(surface, f'Pontuação: {score}', 30, WIDTH // 2, HEIGHT // 2 - 30)
    
    # Enviar pontuação para a API (derrota = 5 pontos)
    send_score_to_api(player_name, player_code, score, False)
    
    # Salvar pontuação e mostrar ranking
    ranking = save_score(player_name, player_code, score)
    
    # Mostrar posição no ranking
    for i, entry in enumerate(ranking):
        if entry['name'] == player_name and entry['code'] == player_code and entry['score'] == score:
            draw_text(surface, f'Sua posição no ranking: {i+1}', 25, WIDTH // 2, HEIGHT // 2 + 10)
            break
    
    draw_text(surface, 'Top 4 Ranking:', 20, WIDTH // 2, HEIGHT * 3 // 4 - 60)
    # Mostrar apenas os top 4 do ranking
    for i, entry in enumerate(ranking):
        if i < 4:
            draw_text(surface, f"{i+1}. {entry['name']} ({entry['code']}): {entry['score']} pontos", 20, WIDTH // 2, HEIGHT * 3 // 4 - 30 + i * 25)
    
    draw_text(surface, 'Pressione R para ver ranking completo', 20, WIDTH // 2, HEIGHT - 80)
    draw_text(surface, 'Pressione ESC para voltar ao menu', 20, WIDTH // 2, HEIGHT - 50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                elif event.key == pygame.K_r:
                    show_ranking(surface)
                    # Redesenhar a tela de game over após voltar do ranking
                    surface.fill(BACKGROUND_COLOR)
                    draw_text(surface, 'GAME OVER', 50, WIDTH // 2, HEIGHT // 4)
                    draw_text(surface, f'Pontuação: {score}', 30, WIDTH // 2, HEIGHT // 2 - 30)
                    draw_text(surface, f'Sua posição no ranking: {i+1}', 25, WIDTH // 2, HEIGHT // 2 + 10)
                    draw_text(surface, 'Top 4 Ranking:', 20, WIDTH // 2, HEIGHT * 3 // 4 - 60)
                    for i, entry in enumerate(ranking):
                        if i < 4:
                            draw_text(surface, f"{i+1}. {entry['name']} ({entry['code']}): {entry['score']} pontos", 20, WIDTH // 2, HEIGHT * 3 // 4 - 30 + i * 25)
                    draw_text(surface, 'Pressione R para ver ranking completo', 20, WIDTH // 2, HEIGHT - 80)
                    draw_text(surface, 'Pressione ESC para voltar ao menu', 20, WIDTH // 2, HEIGHT - 50)
                    pygame.display.update()

def victory_screen(surface, score, player_name, player_code):
    surface.fill(BACKGROUND_COLOR)
    draw_text(surface, 'PARABÉNS!', 50, WIDTH // 2, HEIGHT // 4)
    draw_text(surface, 'Você venceu!', 40, WIDTH // 2, HEIGHT // 4 + 60)
    draw_text(surface, f'Pontuação: {score}', 30, WIDTH // 2, HEIGHT // 2 - 30)
    
    # Enviar pontuação para a API (vitória = 10 pontos)
    send_score_to_api(player_name, player_code, score, True)
    
    # Salvar pontuação e mostrar ranking
    ranking = save_score(player_name, player_code, score)
    
    # Mostrar posição no ranking
    for i, entry in enumerate(ranking):
        if entry['name'] == player_name and entry['code'] == player_code and entry['score'] == score:
            draw_text(surface, f'Sua posição no ranking: {i+1}', 25, WIDTH // 2, HEIGHT // 2 + 10)
            break
    
    draw_text(surface, 'Top 4 Ranking:', 20, WIDTH // 2, HEIGHT * 3 // 4 - 60)
    # Mostrar apenas os top 4 do ranking
    for i, entry in enumerate(ranking):
        if i < 4:
            draw_text(surface, f"{i+1}. {entry['name']} ({entry['code']}): {entry['score']} pontos", 20, WIDTH // 2, HEIGHT * 3 // 4 - 30 + i * 25)
    
    draw_text(surface, 'Pressione R para ver ranking completo', 20, WIDTH // 2, HEIGHT - 80)
    draw_text(surface, 'Pressione ESC para voltar ao menu', 20, WIDTH // 2, HEIGHT - 50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                elif event.key == pygame.K_r:
                    show_ranking(surface)
                    # Redesenhar a tela de vitória após voltar do ranking
                    surface.fill(BACKGROUND_COLOR)
                    draw_text(surface, 'PARABÉNS!', 50, WIDTH // 2, HEIGHT // 4)
                    draw_text(surface, 'Você venceu!', 40, WIDTH // 2, HEIGHT // 4 + 60)
                    draw_text(surface, f'Pontuação: {score}', 30, WIDTH // 2, HEIGHT // 2 - 30)
                    draw_text(surface, f'Sua posição no ranking: {i+1}', 25, WIDTH // 2, HEIGHT // 2 + 10)
                    draw_text(surface, 'Top 4 Ranking:', 20, WIDTH // 2, HEIGHT * 3 // 4 - 60)
                    for i, entry in enumerate(ranking):
                        if i < 4:
                            draw_text(surface, f"{i+1}. {entry['name']} ({entry['code']}): {entry['score']} pontos", 20, WIDTH // 2, HEIGHT * 3 // 4 - 30 + i * 25)
                    draw_text(surface, 'Pressione R para ver ranking completo', 20, WIDTH // 2, HEIGHT - 80)
                    draw_text(surface, 'Pressione ESC para voltar ao menu', 20, WIDTH // 2, HEIGHT - 50)
                    pygame.display.update()

def get_player_name(surface):
    pygame.key.set_repeat(500, 50)  # Configurar repetição de teclas
    
    # Caixas de entrada para nome e código (ajustar espaçamento)
    name_box = pygame.Rect(WIDTH // 4, HEIGHT // 2 - 20, WIDTH // 2, 50)
    code_box = pygame.Rect(WIDTH // 4, HEIGHT // 2 + 70, WIDTH // 2, 50)
    
    color_inactive = INPUT_BOX_COLOR
    color_active = (100, 100, 100)
    name_color = color_inactive
    code_color = color_inactive
    name_active = True
    code_active = False
    name_text = ''
    code_text = ''
    font = pygame.font.SysFont('arial', 32)
    
    # Botão de iniciar
    button = pygame.Rect(WIDTH // 3, HEIGHT * 3 // 4, WIDTH // 3, 50)
    button_text = 'Iniciar Jogo'
    
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Alternar entre as caixas de entrada
                    name_active = not name_active
                    code_active = not code_active
                    name_color = color_active if name_active else color_inactive
                    code_color = color_active if code_active else color_inactive
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Se o usuário clicou no botão de iniciar
                if button.collidepoint(event.pos) and name_text.strip() and code_text.strip():
                    return name_text.strip(), code_text.strip()
                # Se o usuário clicou em alguma das caixas de entrada
                if name_box.collidepoint(event.pos):
                    name_active = True
                    code_active = False
                elif code_box.collidepoint(event.pos):
                    name_active = False
                    code_active = True
                else:
                    name_active = False
                    code_active = False
                name_color = color_active if name_active else color_inactive
                code_color = color_active if code_active else color_inactive
            if event.type == pygame.KEYDOWN:
                if name_active:
                    if event.key == pygame.K_RETURN and name_text.strip():
                        name_active = False
                        code_active = True
                        name_color = color_inactive
                        code_color = color_active
                    elif event.key == pygame.K_BACKSPACE:
                        name_text = name_text[:-1]
                    else:
                        # Limitar o tamanho do nome
                        if len(name_text) < 15 and event.unicode.isprintable():
                            name_text += event.unicode
                elif code_active:
                    if event.key == pygame.K_RETURN and code_text.strip():
                        if name_text.strip():
                            return name_text.strip(), code_text.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        code_text = code_text[:-1]
                    else:
                        # Limitar o tamanho do código
                        if len(code_text) < 10 and event.unicode.isprintable():
                            code_text += event.unicode
        
        surface.fill(BACKGROUND_COLOR)
        
        # Título
        draw_text(surface, 'Jogo da Cobrinha', 50, WIDTH // 2, 50)
        
        # Instruções e campos
        draw_text(surface, 'Digite seu nome:', 30, WIDTH // 2, HEIGHT // 2 - 60)
        pygame.draw.rect(surface, name_color, name_box, 2)
        name_surface = font.render(name_text, True, INPUT_TEXT_COLOR)
        width = max(name_box.w, name_surface.get_width() + 10)
        name_box.w = width
        surface.blit(name_surface, (name_box.x + 5, name_box.y + 10))
        
        draw_text(surface, 'Digite seu código:', 30, WIDTH // 2, HEIGHT // 2 + 30)
        pygame.draw.rect(surface, code_color, code_box, 2)
        code_surface = font.render(code_text, True, INPUT_TEXT_COLOR)
        width = max(code_box.w, code_surface.get_width() + 10)
        code_box.w = width
        surface.blit(code_surface, (code_box.x + 5, code_box.y + 10))
        
        # Renderizar o botão
        mouse = pygame.mouse.get_pos()
        if button.x <= mouse[0] <= button.x + button.w and button.y <= mouse[1] <= button.y + button.h:
            pygame.draw.rect(surface, BUTTON_HOVER_COLOR, button)
        else:
            pygame.draw.rect(surface, BUTTON_COLOR, button)
        
        button_surf = font.render(button_text, True, TEXT_COLOR)
        surface.blit(button_surf, (button.x + (button.w - button_surf.get_width()) // 2, 
                                 button.y + (button.h - button_surf.get_height()) // 2))
        
        pygame.display.update()
    
    return 'Jogador', '0000'

# Carregar sons
def load_sounds():
    # Definir caminhos para os arquivos de som
    sound_files = {
        'move': 'move_sound.wav',
        'eat': 'eat_sound.wav',
        'special_eat': 'special_eat_sound.wav',
        'lose_life': 'lose_life_sound.wav',
        'death': 'death_sound.wav'
    }
    
    # Dicionário para armazenar os sons
    sounds = {}
    
    # Tentar carregar os sons, se não existirem, criar arquivos vazios
    for sound_name, file_path in sound_files.items():
        try:
            # Verificar se o arquivo existe antes de tentar carregá-lo
            if os.path.exists(file_path):
                print(f"Carregando som 8-bit: {file_path}")
                sounds[sound_name] = pygame.mixer.Sound(file_path)
                # Ajustar volume para sons 8-bit
                sounds[sound_name].set_volume(0.4)
            else:
                raise FileNotFoundError(f"Arquivo {file_path} não encontrado")
        except Exception as e:
            # Se o arquivo não existir ou houver erro ao carregar, criar um som 8-bit
            print(f"Erro ao carregar som {file_path}: {e}. Criando som 8-bit.")
            # Criar um som 8-bit com onda senoidal suave
            buffer = bytearray()
            import math
            for i in range(4410):  # 0.1 segundo de som a 44100Hz
                # Criar uma onda senoidal suave para som mais agradável
                if sound_name == 'move':
                    # Som de movimento mais suave e curto
                    value = int(32767 * math.sin(2 * math.pi * 440 * i / 44100) * math.exp(-i / 2000))
                elif sound_name == 'eat':
                    # Som de comida mais agudo
                    value = int(32767 * math.sin(2 * math.pi * 880 * i / 44100) * math.exp(-i / 3000))
                elif sound_name == 'special_eat':
                    # Som de comida especial com frequência modulada
                    freq = 660 + 220 * math.sin(2 * math.pi * 5 * i / 44100)
                    value = int(32767 * math.sin(2 * math.pi * freq * i / 44100) * math.exp(-i / 4000))
                elif sound_name == 'lose_life':
                    # Som de perda de vida mais grave e longo
                    value = int(32767 * math.sin(2 * math.pi * 220 * i / 44100) * math.exp(-i / 6000))
                else:  # death
                    # Som de morte com frequência descendente
                    freq = 440 * math.exp(-i / 4000)
                    value = int(32767 * math.sin(2 * math.pi * freq * i / 44100) * math.exp(-i / 8000))
                buffer.extend([value & 0xFF, (value >> 8) & 0xFF])
            
            sound_obj = pygame.mixer.Sound(buffer=buffer)
            sound_obj.set_volume(0.3)  # Volume baixo para não incomodar
            sounds[sound_name] = sound_obj
            
            # Salvar o som para uso futuro
            with open(file_path, 'wb') as f:
                f.write(buffer)
    
    return sounds

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Jogo da Cobrinha')
    
    # Testar conexão com a API antes de iniciar o jogo
    test_api_connection()
    
    # Carregar sons
    try:
        sounds = load_sounds()
    except Exception as e:
        print(f"Erro ao carregar sons: {e}")
        sounds = {}
    
    # Iniciar o jogo
    start_game(screen, clock, sounds)

def start_game(screen, clock, sounds=None):
    while True:
        # Obter nome do jogador
        player_name, player_code = get_player_name(screen)
        
        # Carregar sons se não foram fornecidos
        if sounds is None:
            try:
                sounds = load_sounds()
            except Exception as e:
                print(f"Erro ao carregar sons: {e}")
                sounds = {}
        
        snake = Snake()
        food = Food()
        danger_foods = [DangerFood() for _ in range(3)]  # Criar 3 caveiras
        last_danger_spawn = time.time()
        danger_spawn_delay = 1.0  # Spawn uma nova caveira a cada segundo
        
        # Variável para controlar quando tocar o som de movimento
        last_move_sound_time = 0
        move_sound_delay = 0.1  # Delay entre sons de movimento (em segundos)
        
        # Variáveis para controlar o início do jogo
        game_started = False
        start_time = None
        game_duration = 45  # segundos
        
        running = True
        while running:
            # Calcular tempo restante apenas se o jogo já começou
            current_time = time.time()
            if game_started:
                elapsed_time = current_time - start_time
                remaining_time = max(0, game_duration - elapsed_time)
            else:
                remaining_time = game_duration
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                        if not game_started:
                            game_started = True
                            start_time = time.time()
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                        if not game_started:
                            game_started = True
                            start_time = time.time()
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                        if not game_started:
                            game_started = True
                            start_time = time.time()
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)
                        if not game_started:
                            game_started = True
                            start_time = time.time()
                    elif event.key == pygame.K_ESCAPE:
                        running = False  # Volta para tela inicial
                    elif event.key == pygame.K_F6:
                        show_ranking(screen)
            
            # Guardar estado anterior para verificar se houve movimento
            prev_head = snake.get_head_position() if snake.positions else None
            prev_alive = snake.alive
            prev_lives = snake.lives
            
            # Mover a cobra apenas se o jogo já começou
            if game_started:
                snake.move()
            
            # Tocar som de movimento se a cobra se moveu e está viva
            if prev_head != snake.get_head_position() and snake.alive and current_time - last_move_sound_time > move_sound_delay:
                if 'move' in sounds:
                    sounds['move'].play()
                last_move_sound_time = current_time
            
            # Verificar se perdeu vida ou morreu
            if prev_alive and (not snake.alive):
                # Cobra morreu
                if 'death' in sounds:
                    sounds['death'].play()
            elif prev_lives > snake.lives:
                # Perdeu uma vida mas não morreu
                if 'lose_life' in sounds:
                    sounds['lose_life'].play()
            
            # Verificar colisão com a comida apenas se o jogo já começou
            if game_started and snake.get_head_position() == food.position:
                if food.type == 'normal':
                    snake.length += 1
                    snake.score += 1
                    # Aumentar velocidade em 2%
                    snake.speed_multiplier *= 1.02
                    # Tocar som de comida normal
                    if 'eat' in sounds:
                        sounds['eat'].play()
                elif food.type == 'special':
                    snake.length += 1
                    snake.score += 50
                    # Aumentar velocidade em 5%
                    snake.speed_multiplier *= 1.05
                    # Tocar som de comida especial
                    if 'special_eat' in sounds:
                        sounds['special_eat'].play()
                
                food.randomize_position(snake.positions)
            
            # Verificar colisão com as caveiras
            for danger_food in danger_foods:
                if danger_food.active and snake.get_head_position() == danger_food.position:
                    snake.lives -= 1
                    if snake.lives <= 0:
                        snake.alive = False
                        # Tocar som de morte
                        if 'death' in sounds:
                            sounds['death'].play()
                    else:
                        # Reposicionar a cobra no centro após perder uma vida
                        snake.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2 + SAFE_ZONE_HEIGHT)]
                        # Tocar som de perda de vida
                        if 'lose_life' in sounds:
                            sounds['lose_life'].play()
                    danger_food.active = False
            
            # Spawn de novas caveiras
            if game_started and current_time - last_danger_spawn > danger_spawn_delay:
                for danger_food in danger_foods:
                    if not danger_food.active:
                        danger_food.randomize_position(snake.positions)
                        break
                last_danger_spawn = current_time
            
            screen.fill(BACKGROUND_COLOR)
            
            # Desenhar bordas brancas para mostrar os limites
            pygame.draw.rect(screen, BORDER_COLOR, pygame.Rect(0, SAFE_ZONE_HEIGHT * GRID_SIZE, WIDTH, HEIGHT - SAFE_ZONE_HEIGHT * GRID_SIZE), 2)
            
            # Desenhar a pontuação e informações no topo
            font = pygame.font.SysFont('arial', 20)
            
            # Desenhar vidas como corações no lado esquerdo
            heart_size = 20
            heart_spacing = 25
            for i in range(snake.lives):
                # Desenhar coração
                heart_x = 10 + (i * heart_spacing)
                heart_y = 10
                # Parte superior do coração (dois círculos)
                pygame.draw.circle(screen, (255, 0, 0), (heart_x + heart_size//4, heart_y + heart_size//4), heart_size//4)
                pygame.draw.circle(screen, (255, 0, 0), (heart_x + heart_size*3//4, heart_y + heart_size//4), heart_size//4)
                # Parte inferior do coração (triângulo)
                points = [
                    (heart_x + heart_size//4 - heart_size//4, heart_y + heart_size//4),
                    (heart_x + heart_size//2, heart_y + heart_size),
                    (heart_x + heart_size*3//4 + heart_size//4, heart_y + heart_size//4)
                ]
                pygame.draw.polygon(screen, (255, 0, 0), points)
                # Preenchimento adicional para um coração mais suave
                pygame.draw.circle(screen, (255, 0, 0), (heart_x + heart_size//2, heart_y + heart_size//2), heart_size//3)
            
            # Desenhar pontuação e vidas no centro
            score_text = f'Pontuação: {snake.score} | Vidas: {snake.lives}'
            score_surface = font.render(score_text, True, TEXT_COLOR)
            score_rect = score_surface.get_rect()
            score_rect.midtop = (WIDTH // 2, 10)
            
            # Desenhar timer no lado direito
            timer_text = f'Tempo: {int(remaining_time)}s'
            timer_surface = font.render(timer_text, True, TEXT_COLOR)
            timer_rect = timer_surface.get_rect()
            timer_rect.topright = (WIDTH - 10, 10)
            
            # Desenhar fundo para todos os textos
            bg_height = 40
            pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, WIDTH, bg_height))
            pygame.draw.line(screen, (100, 100, 100), (0, bg_height), (WIDTH, bg_height), 2)
            
            # Desenhar os textos
            screen.blit(score_surface, score_rect)
            screen.blit(timer_surface, timer_rect)
            
            # Desenhar a comida
            food.draw(screen)
            
            # Desenhar as caveiras
            for danger_food in danger_foods:
                danger_food.draw(screen)
            
            # Desenhar a cobra
            snake.draw(screen)
            
            # Desenhar mensagem de início se o jogo ainda não começou
            if not game_started:
                draw_text(screen, 'Pressione qualquer seta para começar', 30, WIDTH // 2, HEIGHT // 2)
            
            pygame.display.update()
            
            # Verificar se o jogo acabou
            if not snake.alive:
                game_over_screen(screen, snake.score, player_name, player_code)
                running = False
            elif game_started and remaining_time <= 0:
                # Jogador venceu!
                victory_screen(screen, snake.score, player_name, player_code)
                running = False
            
            # Ajustar FPS com base no multiplicador de velocidade
            base_fps = 10
            adjusted_fps = base_fps * snake.speed_multiplier
            clock.tick(adjusted_fps)  # FPS ajustado

if __name__ == '__main__':
    main()