class ComputerPlayer:

    def __init__(self, color):
        """
        Initialize the computer player.

        Parameters:
            color: The player's color ("w" or "b").
        """

        self.color = color
        self.opponent_color = "w" if color == "b" else "b"

    def minimax(self, board, depth, alpha, beta, maximizing):
        if (
            depth == 0
            or board.is_checkmate(self.color)
            or board.is_checkmate(self.opponent_color)
        ):
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = float("-inf")
            for move in self.get_all_moves(board, self.color):
                start_pos, end_pos = move

                new_board = board.clone()
                piece = new_board.board[start_pos[0]][
                    start_pos[1]
                ]  # Fetch the piece from the cloned board

                new_board.move_piece(piece, start_pos, end_pos)

                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False)
                if eval_score > max_eval:
                    max_eval, best_move = eval_score, move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Prune
            return max_eval, best_move

        else:
            min_eval = float("inf")
            for move in self.get_all_moves(board, self.opponent_color):
                start_pos, end_pos = move

                new_board = board.clone()
                piece = new_board.board[start_pos[0]][
                    start_pos[1]
                ]  # Fetch the piece from the cloned board

                new_board.move_piece(piece, start_pos, end_pos)

                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True)
                if eval_score < min_eval:
                    min_eval, best_move = eval_score, move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Prune
            return min_eval, best_move

    def get_all_moves(self, board, color):
        """
        Generates all possible moves for the given color.
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color == color:
                    for destination in piece.valid_moves(board):
                        moves.append(((row, col), destination))
        return moves

    def evaluate_board(self, board):
        """
        Evaluates the board and returns a score.
        Positive values favor the AI player, negative values favor the opponent.
        """
        piece_values = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 1000}
        score = 0

        for row in board.board:
            for piece in row:
                if piece:
                    value = piece_values[piece.piece_type]
                    if piece.color == self.color:
                        score += value  # AI pieces add value
                    else:
                        score -= value  # Opponent pieces subtract value

        return score

    def get_best_move(self, board):
        """
        Finds the best move using Minimax.
        """
        _, best_move = self.minimax(
            board, depth=5, alpha=float("-inf"), beta=float("inf"), maximizing=True
        )
        return best_move
