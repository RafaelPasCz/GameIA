import random
import math
import time
import os
import psutil
from threading import Thread
from collections import deque
#def pathfind(ponto,objetivo,maze):

stop_monitoring = False #flag para interromper avaliação de RAM

def monitor_memory():
    """Obtém o uso atual de memória do programa em MB."""
    print("entrou2")
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss #/ (1024 * 1024)

def monitor_total_memory(interval=0.1):
    print("entrou")
    """Monitora o uso de memória acumulado ao longo do tempo."""
    global stop_monitoring
    total_memory_used = 0  # Para acumular o uso total de RAM
    
    process = psutil.Process(os.getpid())
    while not stop_monitoring:  # Monitora enquanto o flag de parada não for ativado
        try:
            current_memory = process.memory_info().rss #/ (1024 * 1024)
            total_memory_used += current_memory * interval  # Acumula proporcional ao intervalo
            time.sleep(interval)  # Espera pelo intervalo definido
        except psutil.NoSuchProcess:
            break  # Encerra se o processo não existir mais

    return total_memory_used
    
def custo(caminho, objetivo):
    if not caminho:
        return math.inf  
    
    ultimo_ponto = caminho[-1]
    distancia_objetivo = math.sqrt((ultimo_ponto[0] - objetivo[0])**2 + (ultimo_ponto[1] - objetivo[1])**2)
    return len(caminho) + distancia_objetivo  # Combina comprimento do caminho com proximidade ao objetivo

# Função de vizinhança (movimentos possíveis)
def definir_caminho(maze, comeco):

    linhas, cols = len(maze), len(maze[0])
    movs = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimentos: cima, baixo, esquerda, direita
    visitado = [[False for _ in range(cols)] for _ in range(linhas)]
    fila = deque([(comeco, [comeco])])  # (posição atual, caminho percorrido)

    while fila:
        (x, y), caminho = fila.popleft() #pega uma posição da fila
        
        if maze[x][y] == 2:
            return caminho #se a posição é o fim do labirinto, retorna o cmainho

        visitado[x][y] = True #se não, atual é parte de visitado

        for dx, dy in movs:
            nx, ny = x + dx, y + dy # avalia posições possíveis
            if 0 <= nx < linhas and 0 <= ny < cols and not visitado[nx][ny] and maze[nx][ny] != 1:
                fila.append(((nx, ny), caminho + [(nx, ny)])) #utiliza a busca em largura para encontrar uma solução inicial para SA

    return []

def get_vizinho(maze, caminho):
    linhas, cols = len(maze), len(maze[0])
    movs = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Movimentos: cima, baixo, esquerda, direita
    # Escolhe um ponto aleatório no caminho onde é possível um desvio
    for _ in range(100):  # Limita tentativas para evitar loops infinitos
        idx = random.randint(0, len(caminho) - 2)  # Evita o ponto inicial e o objetivo
        x, y = caminho[idx]

        # Verifica se há vizinhos válidos para desvio
        vizinhos_validos = []
        for (dx, dy) in movs:
            (nx, ny) = (x + dx, y + dy)
            if (
                0 <= nx < linhas and 0 <= ny < cols and
                maze[nx][ny] == 0 and (nx, ny) != caminho[idx - 1] and (nx, ny) != caminho[idx + 1]
            ):
                vizinhos_validos.append((nx, ny)) #de novo usa busca em largura a partir do ponto do desvio

        if vizinhos_validos:
            novo_comeco = random.choice(vizinhos_validos)

            # Recalcula o caminho a partir do novo ponto
            novo_caminho_comeco = caminho[:idx + 1] + [novo_comeco] #cria o novo caminho, com o novo começo
            novo_caminho_resto = definir_caminho(maze, novo_comeco) #e junta com o resto do novo caminho

            if novo_caminho_resto:
                return novo_caminho_comeco + novo_caminho_resto[1:]  # Remove duplicação do novo_start

    # Caso nenhum desvio válido seja encontrado
    return caminho

# Algoritmo Simulated Annealing
def simulated_annealing(maze, inicio, objetivo, temp_inicial=1000, taxa_resfriamento=0.99):
    nos_gerados = 0
    nos_visitados = 0

    # Iniciar monitoramento em paralelo
    total_memory_used = [0]  # Usar lista para compartilhamento entre threads
    def monitor_task():
        total_memory_used[0] = monitor_total_memory()

   
    monitor_thread = Thread(target=monitor_task, daemon=True) #inicia thread de monitoramento de RAM
    monitor_thread.start() 


    max_iter = len(maze) * len(maze[0])  # Ajusta max_iter de acordo com o tamanho do labirinto
    atual = definir_caminho(maze, inicio)   # atual deve ser uma tupla (x, y)
    temperatura = temp_inicial
    melhor = atual
    melhor_custo = custo(atual, objetivo)
    if melhor_custo == math.inf:
        return [], 0, 0 #se o melhor custo é infinito, retorna null
    
    caminho = atual  # Para desenhar o caminho
    iteracoes = 0
    start_time = time.perf_counter()
    while iteracoes < max_iter and temperatura > 1:

        vizinho = get_vizinho(maze, atual) #cria o caminho desviado
        nos_gerados = nos_gerados + 1
       # next_pos = random.choice(vizinhos)

        # Certifique-se de que next_pos é uma lista
        if not isinstance(vizinho, list):
            raise ValueError(f"vizinho deve ser do tipo lista, mas é do tipo {type(vizinho)}")

        # Calcular o custo do próximo estado
        next_custo = custo(vizinho, objetivo)

        # Calcular a diferença de custo
        delta_custo = next_custo - melhor_custo

        # Decidir se move para o próximo estado
        if delta_custo < 0 or random.uniform(0, 1) < math.exp(-delta_custo / temperatura):
            atual = vizinho
            nos_visitados = nos_visitados + 1
            # Atualizar melhor solução
            if next_custo < melhor_custo:
                melhor = vizinho
                melhor_custo = next_custo

        # Resfriar a temperatura
        temperatura *= taxa_resfriamento
        iteracoes += 1
        #print(f"Iteração: {iteracoes}, Temperatura: {temperatura}, Custo: {melhor_custo}")
        
    
        if atual == objetivo:
            break
    global stop_monitoring
    stop_monitoring = True
    monitor_thread.join() #termina o monitoramento de memória
    print(f"Memória total acumulada durante a execução: {total_memory_used[0]} Bytes")
    print("total de nos gerados durante o processo: ",nos_gerados)
    print("total de nos visitados durante o preocesso: ",nos_visitados)
    end_time = time.perf_counter()
    exec_ms = (end_time - start_time) * 1000
    return melhor, iteracoes, exec_ms
