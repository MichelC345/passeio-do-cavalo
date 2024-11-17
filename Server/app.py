from flask import Flask
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Board dimensions
N = 5

# Possible moves for a knight
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

def is_valid_move(x, y, board):
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

def depth_limited_search(board, x, y, move_count, depth_limit):
    if move_count == depth_limit:
        print("ok")
        return True

    for dx, dy in KNIGHT_MOVES:
        next_x, next_y = x + dx, y + dy

        if is_valid_move(next_x, next_y, board):
            #print(f"Move: {move_count}, Position: ({x}, {y})")
            board[next_x][next_y] = move_count
            # Send the current board state to the frontend
            socketio.emit('update_board', {'board': board})
            time.sleep(0.5)  # Add delay for visualization

            if depth_limited_search(board, next_x, next_y, move_count + 1, depth_limit):
                return True

            board[next_x][next_y] = -1

    print('Nenhuma solução encontrada para o tabuleiro ', N, 'x', N)
    return False

@app.route('/start')
def start_knights_tour():
    board = [[-1 for _ in range(N)] for _ in range(N)]
    board[0][0] = 0
    depth_limited_search(board, 0, 0, 1, N * N)
    return "Knight's Tour Completed"

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
