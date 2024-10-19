from GameStatus_51202 import GameStatus

def minimax(game_state: GameStatus, depth: int, maximizingPlayer: bool, alpha=float('-inf'), beta=float('inf')):
    terminal = game_state.is_terminal()
    if (depth == 0) or (terminal):
        newScores = game_state.get_scores(terminal)
        return newScores, None

    if maximizingPlayer:
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
                break  # Alpha-beta pruning
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
        return minEval, best_move