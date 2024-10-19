import numpy as np

class GameStatus:
    def __init__(self, board_state, turn_O):
        self.board_state = board_state
        self.turn_O = turn_O  # True if it's O's turn
        self.winner = None

    def is_terminal(self):
        winner = self.check_winner()
        if winner is not None:
            self.winner = winner
            return True
        elif not np.any(self.board_state == 0):
            self.winner = 'Draw'
            return True
        else:
            return False

    def check_winner(self):
        board = self.board_state
        size = board.shape[0]
        lines = []

        # Rows and columns
        for i in range(size):
            lines.append(board[i, :])  # Row
            lines.append(board[:, i])  # Column

        # Diagonals
        diag1 = np.array([board[i, i] for i in range(size)])
        diag2 = np.array([board[i, size - i - 1] for i in range(size)])
        lines.append(diag1)
        lines.append(diag2)

        for line in lines:
            if np.all(line == 1):
                return 'O'  # 'O' wins
            elif np.all(line == -1):
                return 'X'  # 'X' wins

        return None  # No winner yet

    def get_scores(self, terminal):
        if terminal:
            if self.winner == 'O':
                return 10  # 'O' wins
            elif self.winner == 'X':
                return -10  # 'X' wins
            else:
                return 0  # Draw
        else:
            return 0  # Non-terminal state

    def get_negamax_scores(self, terminal):
        return self.get_scores(terminal)

    def get_moves(self):
        moves = []
        size = self.board_state.shape[0]
        for i in range(size):
            for j in range(size):
                if self.board_state[i, j] == 0:
                    moves.append((i, j))
        return moves

    def get_new_state(self, move):
        new_board_state = np.copy(self.board_state)
        x, y = move
        new_board_state[x, y] = 1 if self.turn_O else -1
        return GameStatus(new_board_state, not self.turn_O)
