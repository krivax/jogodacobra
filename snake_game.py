import pygame
import sys
import random
import time
import math
import json
import os

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

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = FOOD_COLOR
        self.type = 'normal'  # normal, special, danger
        self.spawn_time = 0
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
        # Chance de 5% para comida perigosa
        elif random.random() < 0.05:
            self.type = 'danger'
            self.color = DANGER_FOOD_COLOR
            self.spawn_time = time.time()
        else:
            self.type = 'normal'
            self.color = FOOD_COLOR
    
    def draw(self, surface):
        # Se for comida perigosa e já passou 2 segundos, não desenha
        if self.type == 'danger' and time.time() - self.spawn_time > 2:
            return False
            
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

def save_score(name, score):
    # Carregar ranking existente
    ranking = []
    if os.path.exists('ranking.json'):
        try:
            with open('ranking.json', 'r') as f:
                ranking = json.load(f)
        except:
            ranking = []
    
    # Adicionar nova pontuação
    ranking.append({'name': name, 'score': score})
    
    # Ordenar por pontuação (maior para menor)
    ranking = sorted(ranking, key=lambda x: x['score'], reverse=True)
    
    # Manter apenas os top 10
    ranking = ranking[:10]
    
    # Salvar ranking atualizado em JSON
    with open('ranking.json', 'w') as f:
        json.dump(ranking, f)
    
    # Salvar ranking em formato TXT para fácil visualização
    with open('ranking.txt', 'w') as f:
        f.write('=== RANKING DO JOGO DA COBRINHA ===\n\n')
        for i, entry in enumerate(ranking, 1):
            f.write(f"{i}. {entry['name']}: {entry['score']} pontos\n")
    
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
                        # Extrair nome e pontuação da linha
                        parts = line.strip().split(': ')
                        if len(parts) == 2:
                            name = parts[0].split('. ')[1]
                            score = int(parts[1].split(' ')[0])
                            ranking.append({'name': name, 'score': score})
        except:
            # Se falhar, tentar ler do JSON
            if os.path.exists('ranking.json'):
                try:
                    with open('ranking.json', 'r') as f:
                        ranking = json.load(f)
                except:
                    ranking = []
    
    if not ranking:
        draw_text(surface, 'Nenhuma pontuação registrada ainda', 30, WIDTH // 2, HEIGHT // 2)
    else:
        for i, entry in enumerate(ranking):
            draw_text(surface, f"{i+1}. {entry['name']}: {entry['score']} pontos", 25, WIDTH // 2, 120 + i * 40)
    
    draw_text(surface, 'Pressione qualquer tecla para voltar', 20, WIDTH // 2, HEIGHT - 50)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def game_over_screen(surface, score, player_name):
    surface.fill(BACKGROUND_COLOR)
    draw_text(surface, 'GAME OVER', 50, WIDTH // 2, HEIGHT // 4)
    draw_text(surface, f'Pontuação: {score}', 30, WIDTH // 2, HEIGHT // 2 - 30)
    
    # Salvar pontuação e mostrar ranking
    ranking = save_score(player_name, score)
    
    # Mostrar posição no ranking
    for i, entry in enumerate(ranking):
        if entry['name'] == player_name and entry['score'] == score:
            draw_text(surface, f'Sua posição no ranking: {i+1}', 25, WIDTH // 2, HEIGHT // 2 + 10)
            break
    
    draw_text(surface, 'R - Ver ranking completo', 20, WIDTH // 2, HEIGHT * 3 // 4 - 30)
    draw_text(surface, 'Qualquer outra tecla - Jogar novamente', 20, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    show_ranking(surface)
                waiting = False

def get_player_name(surface):
    pygame.key.set_repeat(500, 50)  # Configurar repetição de teclas
    
    input_box = pygame.Rect(WIDTH // 4, HEIGHT // 2, WIDTH // 2, 50)
    color_inactive = INPUT_BOX_COLOR
    color_active = (100, 100, 100)
    color = color_inactive
    active = True
    text = ''
    font = pygame.font.SysFont('arial', 32)
    
    # Botão de iniciar
    button = pygame.Rect(WIDTH // 3, HEIGHT * 3 // 4, WIDTH // 3, 50)
    button_text = 'Iniciar Jogo'
    
    # Botão para ver ranking
    ranking_text = 'Pressione 1 para ver o Ranking'
    
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_ranking(surface)
                    surface.fill(BACKGROUND_COLOR)
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Se o usuário clicou no botão de iniciar
                if button.collidepoint(event.pos) and text.strip():
                    return text.strip()
                # Se o usuário clicou na caixa de entrada
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and text.strip():
                        return text.strip()
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        # Limitar o tamanho do nome
                        if len(text) < 15 and event.unicode.isprintable():
                            text += event.unicode
        
        surface.fill(BACKGROUND_COLOR)
        
        # Título
        draw_text(surface, 'Jogo da Cobrinha', 50, WIDTH // 2, HEIGHT // 4)
        
        # Instruções
        draw_text(surface, 'Digite seu nome:', 30, WIDTH // 2, HEIGHT // 2 - 70)
        
        # Renderizar a caixa de entrada
        pygame.draw.rect(surface, color, input_box, 2)
        text_surface = font.render(text, True, INPUT_TEXT_COLOR)
        width = max(input_box.w, text_surface.get_width() + 10)
        input_box.w = width
        surface.blit(text_surface, (input_box.x + 5, input_box.y + 10))
        
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
    
    return 'Jogador'

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
    
    # Carregar sons
    try:
        sounds = load_sounds()
    except Exception as e:
        print(f"Erro ao carregar sons: {e}")
        sounds = {}
    
    # Iniciar o jogo
    start_game(screen, clock, sounds)

def start_game(screen, clock, sounds=None):
    # Obter nome do jogador
    player_name = get_player_name(screen)
    
    # Carregar sons se não foram fornecidos
    if sounds is None:
        try:
            sounds = load_sounds()
        except Exception as e:
            print(f"Erro ao carregar sons: {e}")
            sounds = {}
    
    snake = Snake()
    food = Food()
    
    # Variável para controlar quando tocar o som de movimento
    last_move_sound_time = 0
    move_sound_delay = 0.1  # Delay entre sons de movimento (em segundos)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.change_direction(UP)
                elif event.key == pygame.K_DOWN:
                    snake.change_direction(DOWN)
                elif event.key == pygame.K_LEFT:
                    snake.change_direction(LEFT)
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction(RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    # Voltar ao menu quando ESC for pressionado
                    return start_game(screen, clock)
        
        # Guardar estado anterior para verificar se houve movimento
        prev_head = snake.get_head_position() if snake.positions else None
        prev_alive = snake.alive
        prev_lives = snake.lives
        
        # Mover a cobra
        snake.move()
        
        # Tocar som de movimento se a cobra se moveu e está viva
        current_time = time.time()
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
        
        # Verificar colisão com a comida
        if snake.get_head_position() == food.position:
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
            elif food.type == 'danger':
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
            
            food.randomize_position(snake.positions)
        
        # Verificar se a comida perigosa expirou
        if food.type == 'danger' and time.time() - food.spawn_time > 2:
            food.randomize_position(snake.positions)
        
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
        
        # Desenhar velocidade no lado direito
        speed_percent = int((snake.speed_multiplier - 1.0) * 100)
        speed_text = f'Velocidade: +{speed_percent}%'
        speed_surface = font.render(speed_text, True, TEXT_COLOR)
        speed_rect = speed_surface.get_rect()
        speed_rect.topright = (WIDTH - 10, 10)
        
        # Desenhar fundo para todos os textos
        bg_height = 40
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(0, 0, WIDTH, bg_height))
        pygame.draw.line(screen, (100, 100, 100), (0, bg_height), (WIDTH, bg_height), 2)
        
        # Desenhar os textos
        screen.blit(score_surface, score_rect)
        screen.blit(speed_surface, speed_rect)
        
        # Desenhar a comida
        if not food.draw(screen):
            food.randomize_position(snake.positions)
        
        # Desenhar a cobra
        snake.draw(screen)
        
        pygame.display.update()
        
        # Verificar se o jogo acabou
        if not snake.alive:
            game_over_screen(screen, snake.score, player_name)
            snake.reset()
            food.randomize_position(snake.positions)
        
        # Ajustar FPS com base no multiplicador de velocidade
        base_fps = 10
        adjusted_fps = base_fps * snake.speed_multiplier
        clock.tick(adjusted_fps)  # FPS ajustado

if __name__ == '__main__':
    main()