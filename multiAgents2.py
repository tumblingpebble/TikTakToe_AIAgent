#multiAgents2.py
from GameStatus_51202 import GameStatus
import logging

def minimax(game_state: GameStatus, depth: int, maximizingPlayer: bool, alpha=float('-inf'), beta=float('inf')):#minimax algorithm
    terminal = game_state.is_terminal()

    if terminal:#if game over
        score = game_state.get_scores()
        return score, None #return score when game over
    
    if (depth == 0):#if depth limit reached
        score = game_state.get_scores()
        return score, None

    if maximizingPlayer:#maximizing player
        maxEval = float('-inf')
        best_move = None
        for move in game_state.get_moves():
            child_state = game_state.get_new_state(move)
            eval_score, _ = minimax(child_state, depth - 1, False, alpha, beta)
            if eval_score > maxEval:
                maxEval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  #alpha-beta pruning
        #log the decision at this level
        logging.debug(f"Maximizing player evaluated move {best_move} with score {maxEval} at depth {depth}")    
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in game_state.get_moves():
            child_state = game_state.get_new_state(move)
            eval_score, _ = minimax(child_state, depth - 1, True, alpha, beta)
            if eval_score < minEval:
                minEval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        #log the decision at this level
        logging.debug(f"Minimizing player evaluated move {best_move} with score {minEval} at depth {depth}")
        return minEval, best_move

def negamax(game_state: GameStatus, depth: int, color, alpha=float('-inf'), beta=float('inf')):#negamax algorithm
    terminal = game_state.is_terminal()
    if depth == 0 or terminal:
        score = color * game_state.get_scores()
        return score, None
    
    max_value = float('-inf')#initialize max value
    best_move = None#initialize best move

    for move in game_state.get_moves():#get all possible moves
        child_state = game_state.get_new_state(move)
        # Alternate the player
        eval_score, _ = negamax(child_state, depth - 1, -color, -beta, -alpha)
        eval_score = -eval_score  # Negate the score after recursive call

        # Log the evaluation of this move
        logging.debug(f"Evaluated move {move} with score {eval_score} at depth {depth}.")

        if eval_score > max_value:#update max value
            max_value = eval_score
            best_move = move

        alpha = max(alpha, eval_score)#update alpha
        if alpha >= beta:
            # Log alpha-beta pruning
            logging.debug(f"Alpha-beta pruning at move {move} with alpha {alpha} and beta {beta}.")
            break

    return max_value, best_move
