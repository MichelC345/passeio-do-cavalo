import sys
import time

class KnightTourProblem:
    def __init__(self, board_size, initial_position):
        self.board_size = board_size
        self.initial_position = initial_position
        self.board = [[-1 for _ in range(board_size)] for _ in range(board_size)]
        self.knight_moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        self.cont = 0  # Contador de iterações

    def is_valid_move(self, x, y):
        # Verifica se o movimento está dentro do tabuleiro e ainda não foi visitado
        return 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == -1

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
        # Encontra o próximo movimento
        possible_moves = []
        for dx, dy in self.knight_moves: 
            nx, ny = x + dx, y + dy
            if self.is_valid_move(nx, ny):
                cost = self.evaluation(nx, ny)
                possible_moves.append((cost, nx, ny))

        possible_moves.sort()  # Ordena pelo custo (menor primeiro)
        if possible_moves:
            _, nx, ny = possible_moves[0]
            return nx, ny
        return None  # Nenhum movimento possível

    def solucao(self):
        x, y = self.initial_position
        self.board[x][y] = 0  # Marca o ponto inicial
        move_count = 1

        while move_count < self.board_size * self.board_size:
            self.cont += 1  # Incrementa o contador de iterações
            next_move = self.next_move(x, y)
            if next_move is None:
                return False  # Falha em encontrar o caminho
            x, y = next_move
            self.board[x][y] = move_count 
            move_count += 1

        return True 

    def print_board(self):
        for row in self.board:
            print(" ".join(f"{cell:2}" for cell in row))

def main(board_size, initial_position):
    start_time = time.time()
    horse = KnightTourProblem(board_size, initial_position)
    success = horse.solucao()
    end_time = time.time()

    result = {
        "execution_time": end_time - start_time,
        "movements": horse.cont,
        "status": "success" if success else "failure",
        "board": horse.board
    }

    print(f"Posição inicial: {initial_position}")
    print(f"Tempo de execução: {result['execution_time']:} segundos")
    print(f"Movimentos: {result['movements']}")
    if result["status"] == "success":
        print("Caminho encontrado:")
        horse.print_board()
    else:
        print("Falha ao encontrar um caminho para o cavalo.")


if __name__ == "__main__":
    try:
        board_size = int(sys.argv[1])
        initial_position = tuple(map(int, sys.argv[2:4]))
    except (IndexError, ValueError):
        print("Uso: python knight_tour.py <board_size> <initial_x> <initial_y>")
        sys.exit(1)

    main(board_size, initial_position)
