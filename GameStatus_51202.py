import numpy as np
import logging

class GameStatus:
    def __init__(self, board_state, turn_O):#initialize game state
        self.board_state = board_state
        self.turn_O = turn_O  # True if it's O's turn
        self.winner = None

    def is_terminal(self):#check if game is over
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

    def get_scores(self):#return score based on game outcome
        if self.is_terminal():
            if self.winner == 'Draw':
                return 0  # DRAW
            elif self.winner == 'O':
                return 1000  # 'O' wins
            elif self.winner == 'X':
                return -1000  # 'X' wins 
        else:
            return self.evaluate_board()

        
    def evaluate_board(self):#evaluate board state
        board = self.board_state
        size = board.shape[0]
        score = 0

        lines = []

        #rows and columns
        for i in range(size):
            lines.append(board[i, :]) # Row
            lines.append(board[:, i]) # Column

        #diagonals
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
        #counts
        O_count = np.count_nonzero(line == 1)
        X_count = np.count_nonzero(line == -1)
        empty_count = np.count_nonzero(line == 0)

        #scoring logic
        if O_count == 3 and empty_count == 0:
            score += 1000 #completed triplet for 'O'
        elif O_count == 2 and empty_count == 1:
            score += 100 #potential triplet
        elif O_count == 1 and empty_count == 2:
            score += 10 #weak potential triplet

        if X_count == 3 and empty_count == 0:
            score += 1000 #completed triplet for 'X'
        elif X_count == 2 and empty_count == 1:
            score += 100 #potential triplet
        elif X_count == 1 and empty_count == 2:
            score += 10 #weak potential triplet    

        #block opponents potential triplet
        if O_count == 0 and X_count == 2 and empty_count == 1:
            score += 150 #prioritize blocking x's potential triplet
        if X_count == 0 and O_count == 2 and empty_count == 1:
            score += 150 #prioritize blocking o's potential triplet

        return score
    
    def count_triplets(self, symbol):#count triplets of a symbol
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

    def get_moves(self):#get all possible moves
        moves = []
        size = self.board_state.shape[0]
        # get all empty positions
        empty_positions = np.argwhere(self.board_state == 0)

        # evaluate moves and sort them
        move_scores = []
        for pos in empty_positions:
            x, y = pos
            temp_board = np.copy(self.board_state)
            temp_board[x, y] = 1 if self.turn_O else -1
            temp_state = GameStatus(temp_board, not self.turn_O)
            score = temp_state.evaluate_board()
            move_scores.append((score, (x, y)))

        #sort moves by score in descending order
        move_scores.sort(reverse=self.turn_O)  #maximize if 'O's turn, minimize if 'X's turn

        #extract sorted moves
        moves = [move for score, move in move_scores]
        return moves

    def get_new_state(self, move):#get new game state after a move
        new_board_state = np.copy(self.board_state)
        x, y = move
        new_board_state[x, y] = 1 if self.turn_O else -1
        return GameStatus(new_board_state, not self.turn_O)
    
    def generate_weights(self, size):
        #create coordinate grids
        x = np.arange(size)
        y = np.arange(size)
        xv, yv = np.meshgrid(x, y)
        
        #calculate distances from the center
        center = (size - 1) / 2
        distances = np.sqrt((xv - center) ** 2 + (yv - center) ** 2)
        
        #invert distances to get weights (closer to center = higher weight)
        max_distance = np.max(distances)
        weights = (max_distance - distances) + 1  #add 1 to ensure weights are positive
        
        #normalize weights to have integers
        weights = weights.astype(int)

        return weights
    
    def evaluate_board(self):#evaluate board state
        board = self.board_state
        size = board.shape[0]
        score = 0

        #generate positional weights
        weights = self.generate_weights(size)

        #apply weights to the board
        weighted_board = board * weights

        #evaluate lines
        lines = []

        #rows
        for i in range(size):
            for j in range(size - 2):
                line = weighted_board[i, j:j + 3]
                lines.append(line)

        #columns
        for j in range(size):
            for i in range(size - 2):
                line = weighted_board[i:i + 3, j]
                lines.append(line)

        #diagonals
        for i in range(size - 2):
            for j in range(size - 2):
                diag = np.array([weighted_board[i + k, j + k] for k in range(3)])
                lines.append(diag)
                anti_diag = np.array([weighted_board[i + 2 - k, j + k] for k in range(3)])
                lines.append(anti_diag)

        for line in lines:
            score += self.evaluate_line(line)

        return score
    
    def evaluate_line(self, line):
        score = 0
        #separate the weights and the actual board values
        weights = np.abs(line)
        symbols = np.sign(line)

        #counts
        O_count = np.count_nonzero(symbols == 1)
        X_count = np.count_nonzero(symbols == -1)
        empty_count = np.count_nonzero(symbols == 0)

        #total weight for each symbol
        O_weight = np.sum(weights[symbols == 1])
        X_weight = np.sum(weights[symbols == -1])

        #scoring logic
        if X_count == 0 and O_count > 0:
            score += O_weight ** 2  #square to emphasize higher weights
        elif O_count == 0 and X_count > 0:
            score -= X_weight ** 2  #segative score for opponent

        #blocking opponent's potential triplet
        if O_count == 0 and X_count == 2 and empty_count == 1:
            score -= X_weight * 10  #penalty for potential opponent triplet
        if X_count == 0 and O_count == 2 and empty_count == 1:
            score += O_weight * 10  #reward for potential AI triplet

        return score
