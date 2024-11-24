from flask import Flask
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

N = 5  # Board dimensions
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

def is_valid_move(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

def depth_limited_search(board, x, y, move_count, depth_limit):
    if move_count == depth_limit:
        #updates.append([row[:] for row in board])
        return True

    for dx, dy in KNIGHT_MOVES:
        next_x, next_y = x + dx, y + dy

        if is_valid_move(next_x, next_y, board):
            board[next_x][next_y] = move_count
            #updates.append([row[:] for row in board])  # Record current state

            if depth_limited_search(board, next_x, next_y, move_count + 1, depth_limit):
                return True

            board[next_x][next_y] = -1  # Backtrack
            #updates.append([row[:] for row in board])  # Record backtrack state

    return False

def print_board(board):
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

'''def solve_knights_tour():
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[0][0] = 0
    updates = []
    
    if depth_limited_search(board, 0, 0, 1, N * N, updates):
        print_board(board)
        return updates  # All board states
    else:
        return []'''

@app.route('/start')
def start_knights_tour():
    socketio.start_background_task(run_knights_tour)
    return "Knight's Tour started"

def run_knights_tour():
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[0][0] = 0
    
    if depth_limited_search(board, 0, 0, 1, N * N):
        print_board(board)
        #return updates  # All board states

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
