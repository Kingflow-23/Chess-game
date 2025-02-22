class ComputerPlayer:
    def __init__(self, color, depth=3):
        """
        Initialize the computer player.

        :param color: The player's color (e.g., "white" or "black").
        :param depth: The search depth for Minimax.
        """
        self.color = color
        self.depth = depth  # Depth of search in the Minimax algorithm

    def make_move(self, board):
        """
        Determines the best move using Minimax with Alpha-Beta pruning.

        :param board: The current game board state.
        :return: The best move to make.
        """
        best_move = None
        best_score = float("-inf") if self.color == "white" else float("inf")

        for move in board.get_valid_moves(self.color):
            board_copy = board.copy()
            board_copy.apply_move(move)

            # Use Minimax to evaluate the move
            score = self.minimax(
                board_copy,
                self.depth,
                float("-inf"),
                float("inf"),
                self.color == "black",
            )

            # Maximizing player (e.g., white)
            if self.color == "white" and score > best_score:
                best_score = score
                best_move = move

            # Minimizing player (e.g., black)
            elif self.color == "black" and score < best_score:
                best_score = score
                best_move = move

        return best_move

    def evaluate_board(self, board):
        """
        Evaluates the board to return a heuristic score.

        :param board: The current game board state.
        :return: A numerical score representing board strength.
        """
        score = board.evaluate()  # This method should be defined in the board class
        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Implements the Minimax algorithm with Alpha-Beta pruning.

        :param board: The current board state.
        :param depth: Remaining depth to explore.
        :param alpha: Best already explored option along the path to the root for maximizer.
        :param beta: Best already explored option along the path to the root for minimizer.
        :param is_maximizing: Boolean flag for the player's turn.
        :return: Best evaluation score for the current state.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if is_maximizing:
            max_eval = float("-inf")
            for move in board.get_valid_moves("white"):
                board_copy = board.copy()
                board_copy.apply_move(move)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:  # Prune branches
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for move in board.get_valid_moves("black"):
                board_copy = board.copy()
                board_copy.apply_move(move)
                eval = self.minimax(board_copy, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:  # Prune branches
                    break
            return min_eval
