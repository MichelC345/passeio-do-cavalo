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

# Variável booleana que determina se o algoritmo extrapolou o tempo
TLE = False
TLE_LIMIT = 10

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

    # Função para verificar se o movimento está dentro do tabuleiro e ainda não foi visitado
    def is_valid_move(self, x, y):
        return 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == -1

class KnightTourDLSSolver(KnightTourProblem):
    def expand(self, position):
        x, y = position
        valid_moves = []
        random_moves = random.sample(self.knight_moves, len(self.knight_moves))
        for dx, dy in random_moves:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                valid_moves.append((nx, ny))
        return valid_moves

    def depth_limited_search(self, depth_limit):
        global generated_nodes
        x, y = self.initial_position
        self.board[x][y] = 0  # Marca o ponto inicial
        generated_nodes += 1
        return self.recursive_dls((x, y), 1, depth_limit)

    def recursive_dls(self, node, move_count, depth_limit):
        global visited_nodes, generated_nodes, start_time
        # No momento que o programa chama a função e acessa esta área, um nó está sendo visitado
        visited_nodes += 1
        self.cont += 1
        actual_time = time.time()-start_time
        if actual_time > TLE_LIMIT: # Verifica se excedeu o tempo limite
            return "timelimit"
        elif self.is_goal(move_count):
            return [node]
        elif depth_limit == 0:
            return "cutoff"
        else:
            #x, y = node
            # Percorre os vizinhos do nó atual
            for child in self.expand(node):
                # A cada vizinho, uma nova chamada é realizada, portanto um novo nó é gerado
                generated_nodes += 1
                nx, ny = child
                self.board[nx][ny] = move_count  # Faz o movimento
                result = self.recursive_dls(child, move_count + 1, depth_limit - 1)
                if result == "timelimit":
                    return "timelimit"
                elif result == "cutoff":
                    self.board[nx][ny] = -1  # Desfaz o movimento (backtracking)
                    continue
                elif result != "failure":
                    return [node] + result
                self.board[nx][ny] = -1  # Desfaz o movimento (backtracking)
            return "failure"

class KnightTourHCSolver(KnightTourProblem):
    def warnsdorff_rule(self, x, y):
        # Calcula o grau de Warnsdorff para a posição (x, y)
        degree = 0
        for dx, dy in self.knight_moves:
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                degree += 1
        return degree
    
    def evaluation(self, x, y):
        # Retorna o custo da posição (x, y)
        return self.warnsdorff_rule(x, y)

    def next_move(self, x, y):
        global visited_nodes, generated_nodes
        # Encontra o próximo movimento
        possible_moves = []
        for dx, dy in self.knight_moves: 
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                cost = self.evaluation(nx, ny)
                possible_moves.append((cost, nx, ny))
                generated_nodes += 1

        possible_moves.sort()  # Ordena pelo custo (menor primeiro)
        if possible_moves:
            _, nx, ny = possible_moves[0]
            return nx, ny
        return None  # Nenhum movimento possível

    def hill_climbing(self):
        global visited_nodes, generated_nodes, start_time
        x, y = self.initial_position
        self.board[x][y] = 0  # Marca o ponto inicial
        move_count = 1
        visited_nodes += 1
        generated_nodes += 1

        while move_count < self.board_size * self.board_size:
            actual_time = time.time()-start_time
            if actual_time > TLE_LIMIT: # Verifica se excedeu o tempo limite
                return "timelimit"
            self.cont += 1  # Incrementa o contador de iterações
            next_move = self.next_move(x, y)
            if next_move is None:
                return False  # Falha em encontrar o caminho
            # Posição atualizada, um novo nó foi visitado
            x, y = next_move
            visited_nodes += 1
            self.board[x][y] = move_count 
            move_count += 1

        return True 


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
        time.sleep(0.05)

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
    global N, generated_nodes, visited_nodes, lin, col, start_time, end_time, TLE
    # Inicialização dos valores
    TLE = False
    possible = False
    generated_nodes = 0
    visited_nodes = 0
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[lin][col] = 0

    initial_position = (lin, col)
    
    # Utiliza-se a biblioteca psutil para obter as informações do processo e computar a memória utilizada
    process = psutil.Process()

    # Caso a solução tenha sido encontrada, informa os estados no front-end e atualiza a variável booleana possible
    if alg == DLS:
        solver = KnightTourDLSSolver(N, initial_position)
        depth_limit = N*N-1
        start_time = time.time()
        path = solver.depth_limited_search(depth_limit)
        # Aqui o algoritmo já terminou de executar, portanto o tempo final é obtido
        end_time = time.time()
        if path == "timelimit":
            TLE = True
        elif path:
            print_board(solver.board)
            possible = True
    elif alg == HC:
        solver = KnightTourHCSolver(N, initial_position)
        start_time = time.time()
        path = solver.hill_climbing()
        # Aqui o algoritmo já terminou de executar, portanto o tempo final é obtido
        end_time = time.time()
        if path == "timelimit":
            TLE = True
        elif path:
            print_board(solver.board)
            possible = True


    elapsed_time = end_time - start_time # Tempo de execução
    memory_used = process.memory_info().rss / (1024 * 1024)  # Armazena a memória em MB

    # Passa os valores obtidos para o front-end
    socketio.emit("update_time", {"execution_time": round(elapsed_time, 4)})
    socketio.emit("update_memory", {"memory_used": round(memory_used, 4)})
    socketio.emit('update_nodes', {
        'generated_nodes': generated_nodes,
        'visited_nodes': visited_nodes
    })
    socketio.emit('execution_finished', {'possible': possible, 'tle': TLE})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
