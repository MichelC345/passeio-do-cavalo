from flask import Flask
from flask_socketio import SocketIO, emit
import psutil, random, time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Variáveis globais
N = 5 # Dimensões da borda, por padrão 5
generated_nodes = 0 # Quantidade de nós gerados
visited_nodes = 0 # Nós visitados
lin = 0
col = 0

DLS = False
HC = True

# Array que determina os possíveis movimentos que o cavalo pode fazer
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

class KnightTourProblem:
    def __init__(self, board_size, initial_position):
        self.board_size = board_size
        self.initial_position = initial_position
        self.board = [[-1 for _ in range(board_size)] for _ in range(board_size)]
        self.total_moves = board_size * board_size
        self.cont = 0
        self.knight_moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
    
    def is_goal(self, move_count):
        return move_count == self.total_moves

    # Função para verificar se o movimento está dentro dos limites da borda e se ainda não foi verificado
    def is_valid_move(self, x, y):
        # Verifica se o movimento está dentro do tabuleiro e ainda não foi visitado
        return 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == -1

    def expand(self, position):
        x, y = position
        valid_moves = []
        random_moves = random.sample(self.knight_moves, len(self.knight_moves))
        for dx, dy in random_moves:
            nx, ny = x + dx, y + dy
            #if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx][ny] == -1:
            if self.is_valid_move(nx, ny):
                valid_moves.append((nx, ny))
        return valid_moves
    

def depth_limited_search(problem, depth_limit):
    x, y = problem.initial_position
    problem.board[x][y] = 0  # Marca o ponto inicial
    return recursive_dls((x, y), problem, 1, depth_limit)

def recursive_dls(node, problem, move_count, depth_limit):
    global visited_nodes, generated_nodes
    # No momento que chama a função e acessa esta área, um nó está sendo visitado
    # Portanto, incrementa visited_nodes
    visited_nodes += 1
    problem.cont += 1
    if problem.is_goal(move_count):
        return [node]
    elif depth_limit == 0:
        return "cutoff"
    else:
        #x, y = node
        # Percorre os vizinhos do nó atual
        for child in problem.expand(node):
            nx, ny = child
            problem.board[nx][ny] = move_count  # Faz o movimento
            # A cada vizinho, uma nova chamada é realizada, portanto um novo nó é gerado
            generated_nodes += 1
            result = recursive_dls(child, problem, move_count + 1, depth_limit - 1)
            if result == "cutoff":
                problem.board[nx][ny] = -1  # Desfaz o movimento (backtracking)
                continue
            elif result != "failure":
                return [node] + result
            problem.board[nx][ny] = -1  # Desfaz o movimento (backtracking)
        return "failure"

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
    # Para cada movimento, atualiza a borda na respectiva posição e armazena isso no array de atualizações
    for i, j in movement:
        board[i][j] = mov_count
        updates.append([row[:] for row in board])
        mov_count += 1

    # Atualiza o front-end exibindo passo a passo os estados da solução
    for update in updates:
        socketio.emit('update_board', {'board': update})
        time.sleep(0.5)

# A rota /start determina o início do algoritmo de busca
@socketio.on("start")
def start_knights_tour(data):
    global N, lin, col
    N = data.get("n", 5) # Recebe o tamanho de N. Por padrão será 5.
    # Linha e coluna. Por padrão serão 0.
    lin = data.get("lin", 0)
    col = data.get("col", 0)
    alg = data.get("alg") # Recebe o tipo de algoritmo a ser executado
    if alg == "DLS":
        socketio.start_background_task(run_knights_tour, DLS)
    else:
        socketio.start_background_task(run_knights_tour, HC)
    

def run_knights_tour(alg):
    global N, generated_nodes, visited_nodes, lin, col
    # Inicialização dos valores
    possible = False
    generated_nodes = 0
    visited_nodes = 0
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[lin][col] = 0

    initial_position = (lin, col)
    depth_limit = N*N-1
    problem = KnightTourProblem(N, initial_position)
    
    # Utiliza-se a biblioteca psutil para obter as informações do processo e computar a memória utilizada
    process = psutil.Process()
    # A biblioteca time é utilizada para obter o tempo de execução
    start_time = time.time()

    # Caso a solução tenha sido encontrada, informa os estados no front-end e atualiza a variável booleana possible
    if alg == DLS:
        path = depth_limited_search(problem, depth_limit)
        # Aqui o algoritmo já terminou de executar, portanto o tempo final é obtido
        end_time = time.time()
        if path:
            #print("Movimentos: ", problem.cont)
            #print("Path found:")
            print_board(problem.board)
            possible = True
            #for row in problem.board:
            #    print(" ".join(f"{cell:2}" for cell in row))
        '''if depth_limited_search(board, lin, col, 1, N * N):
            print_board(board)
            possible = True'''
    '''elif alg == HC:
        if hill_climbing(board, lin, col, 1, N * N):
            print_board(board)
            possible = True'''

    elapsed_time = end_time - start_time # Tempo de execução
    memory_used = process.memory_info().rss / (1024 * 1024)  # Armazena a memória em MB

    # Passa os valores obtidos para o front-end
    socketio.emit("update_time", {"execution_time": round(elapsed_time, 2)})
    socketio.emit("update_memory", {"memory_used": round(memory_used, 2)})
    socketio.emit('update_nodes', {
        'generated_nodes': generated_nodes,
        'visited_nodes': visited_nodes
    })
    socketio.emit('execution_finished', {'possible': possible})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
