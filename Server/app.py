from flask import Flask
from flask_socketio import SocketIO, emit
import time
import psutil

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variáveis globais
N = 5 # Dimensões da borda, por padrão 5
generated_nodes = 0 # Quantidade de nós gerados
visited_nodes = 0 # Nós visitados
lin = 0
col = 0

# Array que determina os possíveis movimentos que o cavalo pode fazer
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

# Função para verificar se o movimento está dentro dos limites da borda e se ainda não foi verificado
def is_valid_move(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

# Função para executar a busca
def depth_limited_search(board, x, y, move_count, depth_limit):
    global generated_nodes, visited_nodes

    # Caso o movimento esteja dentro do limite estabelecido N*N, significa que todo o tabuleiro foi percorrido
    # Portanto solução válida
    if move_count == depth_limit:
        return True
    
    # Para cada chamada de método, um nó visitado
    visited_nodes += 1

    # Verifica os possíveis movimentos dada a posição x,y atual
    for dx, dy in KNIGHT_MOVES:
        next_x, next_y = x + dx, y + dy

        # Caso o movimento seja válido
        if is_valid_move(next_x, next_y, board):
            generated_nodes += 1 # Para cada movimento válido, incrementa 1
            board[next_x][next_y] = move_count # Atualiza respectiva posição da borda

            # Executa algoritmo de busca e retorna verdadeiro caso tenha sido concluída com sucesso
            if depth_limited_search(board, next_x, next_y, move_count + 1, depth_limit):
                return True

            # Redefine a mesma posição como não visitada para não ser incoerente nas demais chamadas
            board[next_x][next_y] = -1  # Backtrack

    # Caso nenhuma busca tenha sido concluída com sucesso, não foram encontradas soluções
    return False

# Função para exibir a solução passo a passo no front-end
def print_board(board):
    global generated_nodes
    
    # Array de atualizações para armazenar todos os estados da solução
    updates = []
    # Matriz de movimentos vai armazenar os movimentos 0, 1, 2, ..., N*N, conforme a solução obtida
    movement = [None] * N*N
    for i in range(N):
        for j in range (N):
            movement[board[i][j]] = (i, j)
    board = [[-1 for _ in range(N)] for _ in range(N)]
    mov_count = 0
    # Para cada movimento, atualiza a borda na posição respectiva e armazena isso no array de atualizações
    for i, j in movement:
        board[i][j] = mov_count
        updates.append([row[:] for row in board])
        mov_count += 1

    # Atualiza o front-end exibindo passo a passo os estados da solução
    for update in updates:
        socketio.emit('update_board', {'board': update})
        time.sleep(0.5)

# A rota /start determina o início do algoritmo
@socketio.on("start")
def start_knights_tour(data):
    global N, lin, col
    N = data.get("n", 5) # Recebe o tamanho de N. Por padrão será 5.
    lin = data.get("lin", 0)
    col = data.get("col", 0)
    socketio.start_background_task(run_knights_tour)

def run_knights_tour():
    global N, generated_nodes, visited_nodes, lin, col
    # Inicialização dos valores
    possible = False
    generated_nodes = 0
    visited_nodes = 0
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[lin][col] = 0
    
    # Utiliza-se a biblioteca psutil para obter as informações do processo e computar a memória utilizada
    process = psutil.Process()
    # A biblioteca time é utilizada para obter o tempo de execução
    start_time = time.time()

    # Caso a solução tenha sido encontrada, informa os estados no front-end e atualiza a variável booleana possible
    if depth_limited_search(board, lin, col, 1, N * N):
        print_board(board)
        possible = True

    end_time = time.time()
    elapsed_time = end_time - start_time # Tempo de execução
    memory_used = process.memory_info().rss / (1024 * 1024)  # Armazena a memória em MB

    # Passa os valores obtidos para o front-end
    socketio.emit("update_time", {"execution_time": elapsed_time})
    socketio.emit("update_memory", {"memory_used": memory_used})
    socketio.emit('update_nodes', {
        'generated_nodes': generated_nodes,
        'visited_nodes': visited_nodes
    })
    socketio.emit('execution_finished', {'possible': possible})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
