import random
import math
import time
import os
import psutil
from threading import Thread
from collections import deque
from collections import deque
import time

stop_monitoring = False

def monitor_memory():
    #Obtém o uso atual de memória do programa em Bytes
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss 

def monitor_total_memory(interval=0.1):
    #Monitora o uso de RAM e soma a um valor acumulado
    global stop_monitoring
    total_memory_used = 0  # Para acumular o uso total de RAM
    
    process = psutil.Process(os.getpid())
    while not stop_monitoring:  # Monitora enquanto o flag de parada não for ativado
        try:
            current_memory = process.memory_info().rss # em Bytes
            total_memory_used += current_memory * interval  # Acumula proporcional ao intervalo
            time.sleep(interval)  # Espera pelo intervalo definido
        except psutil.NoSuchProcess:
            break  # Encerra se o processo não existir mais

    return total_memory_used #retorna o total de memória utilizado

# Busca em Largura para encontrar o caminho no labirinto
def busca_em_largura(labirinto, inicio, objetivo):
    nos_gerados=0
    nos_visitados=0

    # Iniciar monitoramento em paralelo
    total_memory_used = [0]  # Usar lista para compartilhamento entre threads
    def monitor_task():
        total_memory_used[0] = monitor_total_memory()
    monitor_thread = Thread(target=monitor_task, daemon=True) #inicia thread de monitoramento de RAM
    monitor_thread.start() 

    atual = inicio
    iteracoes = 0
    queue = deque([[inicio]]) #inicializa fila para busca de caminho
    visited = set([inicio])
    r, c = len(labirinto), len(labirinto[0]) #define os limites do labirinto, para não andar alem das paredes finais
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] #define as direções que o personagem pode tomar
    start_time = time.perf_counter() #inicia o timer para analise de performance
    while queue:
        iteracoes = iteracoes + 1
        path = queue.popleft() #inicia o caminho
        nos_visitados = nos_visitados + 1
        atual = path[-1]
        for dx, dy in directions:
            if labirinto[atual[1]][atual[0]] == 2: #se encontrou o final
                end_time = time.perf_counter() #termina timer se chega ao fim
                time.sleep(1) #para ter tempo de calcular o uso de RAM
                global stop_monitoring
                stop_monitoring = True #para de monitorar a RAM
                monitor_thread.join() #termina a thread de monitoramento
                print(f"Memória total acumulada durante a execução: {total_memory_used[0]} Bytes")
                exec_ms = (end_time - start_time) * 1000 #transforma o tempo para ms
                print("nos gerados durante o processo: ",nos_gerados)
                print("nos viistados durante o processo: ", nos_visitados)
                return path, iteracoes, exec_ms
            vizinho = (atual[0] + dx, atual[1] + dy)
          # se o vizinho não está fora dos limites  definidos e não é uma parede e não foi visitado
            if (0 <= vizinho[0] < c and 0 <= vizinho[1] < r and labirinto[vizinho[1]][vizinho[0]] != 1 and vizinho not in visited):
                visited.add(vizinho)            #adiciona o vizinho ao vetor de visitados
                novas_posicoes = list(path)     
                nos_gerados = nos_gerados + len(novas_posicoes)
                novas_posicoes.append(vizinho)   #adiciona vizinhos válidos a fila, para posterior análise
                queue.append(novas_posicoes)
    return None, iteracoes, 0
