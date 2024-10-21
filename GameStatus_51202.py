#GameStatus_51202.property
import numpy as np

class GameStatus:
    def __init__(self, board_state, turn_O):
        self.board_state = board_state
        self.turn_O = turn_O  # True if it's O's turn
        self.winner = None

    def is_terminal(self):
        size = self.board_state.shape[0]
        if size == 3: # check 3x3 grid for winner
            winner = self.check_winner()
            if winner:
                self.winner = winner
                return True
            elif not np.any(self.board_state == 0): #if board is full
                self.winner = 'Draw'
                return True
            else:
                return False
        else: #for larger grids, only end game when board full
            if not np.any(self.board_state == 0): #if board full
                O_triplets = self.count_triplets(1) #count triplets of O
                X_triplets = self.count_triplets(-1) #count triplets of X

                if O_triplets > X_triplets:
                    self.winner = 'O'  # 'O' wins
                elif X_triplets > O_triplets:
                    self.winner = 'X'  # 'X' wins'
                else:
                    self.winner = 'Draw'
                return True
            return False

    def check_winner(self):
        board = self.board_state
        size = board.shape[0]

        if size == 3:
            # Check rows and columns
            for i in range(3):
                if np.all(board[i, :] == 1):
                    return 'O'
                elif np.all(board[i, :] == -1):
                    return 'X'
                if np.all(board[:, i] == 1):
                    return 'O'
                elif np.all(board[:, i] == -1):
                    return 'X'
            # Check diagonals
            if np.all(np.diag(board) == 1):
                return 'O'
            elif np.all(np.diag(board) == -1):
                return 'X'
            if np.all(np.diag(np.fliplr(board)) == 1):
                return 'O'
            elif np.all(np.diag(np.fliplr(board)) == -1):
                return 'X'
        # grids > 3x3, do not return a winner based on a single triplet
        return None

    def get_scores(self):
        if self.is_terminal():
            if self.winner == 'Draw':
                return 0  # DRAW
            elif self.winner == 'O':
                return 1000  # 'O' wins
            elif self.winner == 'X':
                return -1000  # 'X' wins 
        else:
            return self.evaluate_board()

        
    def evaluate_board(self):
        board = self.board_state
        size = board.shape[0]
        score = 0

        lines = []

        # Rows and columns
        for i in range(size):
            lines.append(board[i, :]) # Row
            lines.append(board[:, i]) # Column

        # Diagonals
        for i in range(size - 2):
            for j in range(size - 2):#check diagonals and anti-diagonal
                diag = np.array([board[i + k, j + k] for k in range(3)])
                anti_diag = np.array([board[i + 2 - k, j + k] for k in range(3)])
                lines.append(diag)
                lines.append(anti_diag)

        for line in lines:
            score += self.evaluate_line(line)
        return score
    
    def evaluate_line(self, line):
        score = 0
        #scoring for 'O'
        if np.count_nonzero(line == 1) == 3:
            score += 100
        elif np.count_nonzero(line == 1) == 2 and np.count_nonzero(line == 0) == 1:
            score += 10
        elif np.count_nonzero(line == 1) == 1 and np.count_nonzero(line == 0) == 2:
            score += 1
        #scoring for X
        if np.count_nonzero(line == -1) == 3:
            score -= 100
        elif np.count_nonzero(line == -1) == 2 and np.count_nonzero(line == 0) == 1:
            score -= 10
        elif np.count_nonzero(line == -1) == 1 and np.count_nonzero(line == 0) == 2:
            score -= 1
        return score
    
    def count_triplets(self, symbol):
        board = self.board_state
        size = board.shape[0]
        triplet_count = 0

        #check rows and columns for triplets
        for i in range(size):
            for j in range(size - 2): #ensure check for 3 consecutive cells
                if np.all(board[i, j:j + 3] == symbol): #horizontal triplet
                    triplet_count += 1
                if np.all(board[j:j + 3, i] == symbol): #vertical triplet
                    triplet_count += 1

        #check diagonals for triplets
        for i in range(size - 2):
            for j in range(size - 2):
                if np.all([board[i + k, j + k] == symbol for k in range(3)]): #main diagonal triplet
                    triplet_count += 1
                if np.all([board[i + 2 - k, j + k] == symbol for k in range(3)]): #anti-diagonal triplet
                    triplet_count += 1

        return triplet_count

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