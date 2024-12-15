import pygame
import ast
import time
from SA import simulated_annealing  # Importando o algoritmo SA
from BFS import busca_em_largura  # Importando o algoritmo BFS
# Alunos: André Henrique, Gabriel yudi, Nathan Oliboni, Rafael Pascoali
# Função para carregar a matriz do arquivo .txt
def load_maze(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return ast.literal_eval(content.split('=')[1].strip())

# Configuração inicial do Pygame
pygame.init()
WIDTH, HEIGHT = 1240, 960
CELL_SIZE = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labirinto")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fontes
font = pygame.font.Font(None, 40)
large_font = pygame.font.Font(None, 80)

# Função para desenhar os botões
def draw_button(x, y, width, height, text, active=False):
    color = BLUE if active else GRAY
    pygame.draw.rect(screen, color, (x, y, width, height))
    label = font.render(text, True, BLACK)
    screen.blit(label, (x + 20, y + 10))

# Tela de escolha do tipo de resolução
def resolution_choice():
    running = True
    mode = None
    while running:
        screen.fill(WHITE)

        # Desenhar botões de resolução
        draw_button(100, 100, 300, 50, "Manual")
        draw_button(100, 200, 300, 50, "Simulated Annealing")
        draw_button(100, 300, 300, 50, "Busca em Largura")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 100 <= x <= 400:
                    if 100 <= y <= 150:
                        mode = "manual"
                        running = False
                    elif 200 <= y <= 250:
                        mode = "sa"
                        running = False
                    elif 300 <= y <= 350:
                        mode = "bl"
                        running = False
        clock.tick(30)

    return mode

# Tela de escolha de dificuldade
def difficulty_choice():
    running = True
    maze_file = None
    while running:
        screen.fill(WHITE)

        # Desenhar botões de dificuldade
        draw_button(100, 100, 300, 50, "Fácil (10x10)")
        draw_button(100, 200, 300, 50, "Médio (15x15)")
        draw_button(100, 300, 300, 50, "Difícil (20x20)")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 100 <= x <= 400:
                    if 100 <= y <= 150:
                        maze_file = "easy.txt"
                        running = False
                    elif 200 <= y <= 250:
                        maze_file = "medium.txt"
                        running = False
                    elif 300 <= y <= 350:
                        maze_file = "hard.txt"
                        running = False
        clock.tick(30)

    return maze_file

# Função para desenhar o labirinto
def draw_maze(maze):
    ROWS, COLS = len(maze), len(maze[0])
    for row in range(ROWS):
        for col in range(COLS):
            if maze[row][col] == 1:
                color = BLACK
            elif maze[row][col] == 2:
                color = BLUE  # Saída
            else:
                color = WHITE
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def no_path_screen():
    while True:  # Loop simplificado para focar na interação
        screen.fill(WHITE)

        # Mensagem de erro
        message = large_font.render("Sem caminho disponível!", True, RED)
        message2 = font.render("Tente outra resolução ou labirinto.", True, BLACK)
        
        # Desenhar textos na tela
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 3))
        screen.blit(message2, (WIDTH // 2 - message2.get_width() // 2, HEIGHT // 2))
        
        # Desenhar botão "Voltar ao Menu"
        button_x, button_y, button_width, button_height = WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 50
        draw_button(button_x, button_y, button_width, button_height, "Voltar ao Menu", active=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                    return  # Voltar ao menu principal imediatamente

# Função para a tela de vitória
def victory_screen(total_time, moves, total_iteracoes):
    while True:  # Loop simplificado para focar na interação
        screen.fill(WHITE)

        # Mensagem de vitória
        message = large_font.render("Você venceu!", True, GREEN)
        time_message = font.render(f"Tempo: {total_time:.2f} segundos", True, BLACK)
        moves_message = font.render(f"Movimentos: {moves}", True, BLACK)
        iter_message = font.render(f"Iterações: {total_iteracoes}", True, BLACK)
        
        # Desenhar textos na tela
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, HEIGHT // 3))
        screen.blit(time_message, (WIDTH // 2 - time_message.get_width() // 2, HEIGHT // 2))
        screen.blit(moves_message, (WIDTH // 2 - moves_message.get_width() // 2, HEIGHT // 2 + 50))
        screen.blit(iter_message, (WIDTH // 2 - iter_message.get_width() // 2, HEIGHT // 2 + 100))
        
        # Desenhar botão "Voltar ao Menu"
        button_x, button_y, button_width, button_height = WIDTH // 2 - 150, HEIGHT // 2 + 200, 300, 50
        draw_button(button_x, button_y, button_width, button_height, "Voltar ao Menu", active=True)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if button_x <= x <= button_x + button_width and button_y <= y <= button_y + button_height:
                    return  # Voltar ao menu principal imediatamente
 
                
def manual_game(maze, start, goal):
    player_y, player_x = start  # Corrigido para seguir o padrão (linha, coluna)
    ROWS, COLS = len(maze), len(maze[0])
    moves = 0
    running = True
    start_time = time.time()

    # Chamar busca em largura para verificar se o labirinto é solucionável
    path, iteracoes, tempo_ms = busca_em_largura(maze, start, goal)
    if not path:  # Verifique se o caminho foi encontrado
        print("Erro: O labirinto não é solucionável.")
        no_path_screen()
        return
    
    while running:
        screen.fill(BLACK)
        draw_maze(maze)
        pygame.draw.rect(
            screen, RED, (player_x * CELL_SIZE, player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                # Registrar posição anterior
                new_x, new_y = player_x, player_y

                # Atualizar posição com base no input do jogador
                if event.key == pygame.K_UP:
                    new_y -= 1
                elif event.key == pygame.K_DOWN:
                    new_y += 1
                elif event.key == pygame.K_LEFT:
                    new_x -= 1
                elif event.key == pygame.K_RIGHT:
                    new_x += 1

                # Validar se o movimento é permitido
                if 0 <= new_x < COLS and 0 <= new_y < ROWS and maze[new_y][new_x] != 1:
                    player_x, player_y = new_x, new_y
                    moves += 1

                # Verificar se chegou à saída
                if (player_y, player_x) == goal:  # Comparar com (linha, coluna)
                    total_time = time.time() - start_time
                    victory_screen(total_time, moves, 0)
                    running = False
                    break  # Encerrar o loop após vitória

        clock.tick(30)

# Jogo principal
def game_loop(maze, mode):
    ROWS, COLS = len(maze), len(maze[0])
    start = (0, 0)
    goal = None
    
    # Corrigir como o goal é definido
    for row in range(ROWS):
        for col in range(COLS):
            if maze[row][col] == 2:  # Encontrar a saída
                goal = (row, col)  # Coordenadas (linha, coluna)
                
                
    if goal is None:
        print("Erro: Nenhum objetivo (saída) definido no labirinto.")
        return

    if mode == "sa":
        # Usar o algoritmo Simulated Annealing
        path, total_iteracoes, tempo_ms = simulated_annealing(maze, start, goal)
        print("tempo para encontrar solução (SA): ",tempo_ms,"ms")
        # Validar o caminho gerado pelo algoritmo
        if not path:
            print("Erro: Nenhum caminho encontrado pelo Simulated Annealing.")
            no_path_screen()

        # Mostrar o caminho durante a execução
        running = True

        for pos in path:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            # Renderizar o labirinto e a posição atual
            screen.fill(BLACK)
            draw_maze(maze)
            pygame.draw.rect(
                screen, RED, (pos[1] * CELL_SIZE, pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
            pygame.display.flip()
            clock.tick(10)  # Ajuste a velocidade para dar mais tempo ao SA

            # Verificar se chegou à saída
            if pos == goal:
                victory_screen(tempo_ms/1000, len(path)-1, total_iteracoes)
                running = False
                break  # Interrompe o loop após a vitória

        # Se o loop terminou sem encontrar a saída, exibir uma mensagem
        if running:
            print("Erro: O loop terminou sem alcançar o objetivo.")
    
    elif mode == "bl":
        goal = (col, row)
        path, iteracoes, tempo_ms = busca_em_largura(maze, start, goal)
        print("tempo para encontrar solução (BL): ",tempo_ms,"ms")
        if not path:  # Verifique se o caminho foi encontrado
            print("Erro: Nenhum caminho encontrado pelo BFS.")
            no_path_screen()
            return

        running = True

        for pos in path:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            screen.fill(BLACK)
            draw_maze(maze)
            pygame.draw.rect(
                screen, RED, (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )
            pygame.display.flip()
            clock.tick(5)

            if pos == goal:
                victory_screen(tempo_ms / 1000, len(path)-1, iteracoes)
                running = False
                break

    else:
        # Resolver manualmente
        manual_game(maze, start, goal)

# Iniciar o jogo
running = True
while running:
    mode = resolution_choice()  # Tela de seleção de resolução
    if mode:
        maze_file = difficulty_choice()  # Tela de escolha de dificuldade
        if maze_file:
            maze = load_maze(maze_file)  # Carrega o labirinto
            game_loop(maze, mode)  # Executa o jogo com base no modo escolhido
        else:
            print("Dificuldade não selecionada.")
    else:
        print("Jogo encerrado.")
        running = False
