from flask import Flask
from flask_socketio import SocketIO, emit
import time
import psutil

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

N = 5  # Board dimensions
generated_nodes = 0 # Quantidade de movimentos necessários
visited_nodes = 0

KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

def is_valid_move(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

def depth_limited_search(board, x, y, move_count, depth_limit):
    global generated_nodes, visited_nodes

    if move_count == depth_limit:
        #updates.append([row[:] for row in board])
        return True
    
    visited_nodes += 1

    for dx, dy in KNIGHT_MOVES:
        next_x, next_y = x + dx, y + dy

        if is_valid_move(next_x, next_y, board):
            generated_nodes += 1 #Para cada movimento válido, incrementa 1
            board[next_x][next_y] = move_count
            #updates.append([row[:] for row in board])  # Record current state

            if depth_limited_search(board, next_x, next_y, move_count + 1, depth_limit):
                return True

            board[next_x][next_y] = -1  # Backtrack
            #updates.append([row[:] for row in board])  # Record backtrack state

    return False

def print_board(board):
    global generated_nodes
    """
    Print the chessboard in a readable format.
    """
    #for row in board:
       # print(" ".join(f"{cell:2}" for cell in row))
    updates = []
    movement = [None] * N*N
    for i in range(N):
        for j in range (N):
            #print(board[i][j])
            movement[board[i][j]] = (i, j)
    board = [[-1 for _ in range(N)] for _ in range(N)]
    mov_count = 0
    for i, j in movement:
        #print(i, j)
        board[i][j] = mov_count
        updates.append([row[:] for row in board])
        mov_count += 1

    for update in updates:
        socketio.emit('update_board', {'board': update})
        time.sleep(0.5)  # Delay for frontend visualization
    # Atualiza número de movimentos
    #socketio.emit('update_movements', {'movements': generated_nodes})
    socketio.emit('update_nodes', {
        'generated_nodes': generated_nodes,
        'visited_nodes': visited_nodes
    })

'''def solve_knights_tour():
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[0][0] = 0
    updates = []
    
    if depth_limited_search(board, 0, 0, 1, N * N, updates):
        print_board(board)
        return updates  # All board states
    else:
        return []'''

#@app.route('/start')
@socketio.on("start")
def start_knights_tour():
    socketio.start_background_task(run_knights_tour)
    return "Knight's Tour started"

def run_knights_tour():
    global generated_nodes
    generated_nodes = 0 # Inicializa quantidade de movimentos
    visited_nodes = 0
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[0][0] = 0
    
    process = psutil.Process()
    start_time = time.time()

    if depth_limited_search(board, 0, 0, 1, N * N):
        print_board(board)
        #return updates  # All board states

    end_time = time.time()
    elapsed_time = end_time - start_time
    memory_used = process.memory_info().rss / (1024 * 1024)  # Memory in MB

    socketio.emit("update_time", {"execution_time": f"{elapsed_time:.2f} seconds"})
    socketio.emit("update_memory", {"memory_used": f"{memory_used:.2f} MB"})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
