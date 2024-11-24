# Board dimensions
N = 5
cont = 0

# Possible moves for a knight
KNIGHT_MOVES = [
    (2, 1), (1, 2), (-1, 2), (-2, 1),
    (-2, -1), (-1, -2), (1, -2), (2, -1)
]

def is_valid_move(x, y, board):
    """
    Check if the move is valid: within bounds and not already visited.
    """
    return 0 <= x < N and 0 <= y < N and board[x][y] == -1

def depth_limited_search(board, x, y, move_count, depth_limit):
    global cont
    """
    Perform depth-limited search for the Knight's Tour.
    """
    cont = cont + 1
    if move_count == depth_limit:
        return True  # All squares visited, solution found

    # Try all possible knight moves
    for dx, dy in KNIGHT_MOVES:
        next_x, next_y = x + dx, y + dy

        if is_valid_move(next_x, next_y, board):
            # Make the move
            board[next_x][next_y] = move_count

            # Recur with the updated board
            if depth_limited_search(board, next_x, next_y, move_count + 1, depth_limit):
                return True

            # Backtrack
            board[next_x][next_y] = -1

    return False

def solve_knights_tour(start_x, start_y):
    """
    Solve the Knight's Tour problem using depth-limited search.
    """
    print('Iniciando algoritmo...')
    # Initialize the chessboard
    board = [[-1 for _ in range(N)] for _ in range(N)]

    # Starting position
    board[start_x][start_y] = 0

    # Perform depth-limited search
    if depth_limited_search(board, start_x, start_y, 1, N * N):
        print_board(board)
        print("movimentos: ", cont)
        return board
    else:
        print("movimentos: ", cont)
        return None

def print_board(board):
    """
    Print the chessboard in a readable format.
    """
    for row in board:
        print(" ".join(f"{cell:2}" for cell in row))

# Starting position (e.g., top-left corner)
start_x, start_y = 0, 0
solve_knights_tour(start_x, start_y)
'''solution = solve_knights_tour(start_x, start_y)

if solution:
    print("Knight's Tour solution:")
    print_board(solution)
else:
    print("No solution exists.")'''
