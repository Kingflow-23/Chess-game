from typing import Tuple, Optional, List

from src.board import Board


class ComputerPlayer:
    """
    Represents a computer-controlled chess player using the Minimax algorithm with Alpha-Beta pruning,
    enhanced with a transposition table for caching evaluated board states.
    """

    def __init__(self, color: str) -> None:
        """
        Initializes the computer player with the given color and creates an empty transposition table.

        Args:
            color (str): The player's color ("w" for white, "b" for black).
        """

        self.color = color
        self.opponent_color = "w" if color == "b" else "b"
        self.transposition_table = {}  # Stores evaluated board states

    def board_hash(self, board: Board) -> int:
        """
        Generates a hash for the current board state.

        This implementation converts the board's 2D list into a string representation,
        replacing empty squares with "-", and then hashes that string.

        Args:
            board (Board): The current board state.

        Returns:
            int: A hash value representing the board state.
        """
        board_str = "".join(
            "".join(piece.piece_type if piece is not None else "-" for piece in row)
            for row in board.board
        )
        return hash(board_str)

    def minimax(
        self, board: Board, depth: int, alpha: float, beta: float, maximizing: bool
    ) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Performs the Minimax algorithm with Alpha-Beta pruning and transposition table caching.

        Args:
            board (Board): The current board state.
            depth (int): The remaining depth to search.
            alpha (float): The current alpha value for pruning.
            beta (float): The current beta value for pruning.
            maximizing (bool): True if it's the maximizing player's turn, False for minimizing.

        Returns:
            Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
                A tuple where the first element is the evaluation score of the best move,
                and the second element is the best move in the format ((start_row, start_col), (end_row, end_col)).
                If no move is found, returns (score, None).
        """
        board_key = self.board_hash(board)
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]

        if (
            depth == 0
            or board.is_checkmate(self.color)
            or board.is_checkmate(self.opponent_color)
        ):
            score = self.evaluate_board(board)
            self.transposition_table[board_key] = (score, None)
            return score, None

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

            self.transposition_table[board_key] = (max_eval, best_move)
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

            self.transposition_table[board_key] = (min_eval, best_move)
            return min_eval, best_move

    def get_all_moves(
        self, board: Board, color: str
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Generates all legal moves for the given color on the current board.

        Args:
            board (Board): The current board state.
            color (str): The color for which to generate moves ("w" or "b").

        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, int]]]: A list of moves, where each move is represented as
            ((start_row, start_col), (end_row, end_col)).
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color == color:
                    for destination in piece.valid_moves(board):
                        moves.append(((row, col), destination))
        return moves

    def evaluate_board(self, board: Board) -> int:
        """
        Evaluates the board using a simple material-based heuristic.

        Each piece is assigned a value (pawns = 1, knights/bishops = 3, rooks = 5, queen = 9, king = 1000).
        The score is calculated as the sum of the AI's piece values minus the sum of the opponent's piece values.

        Args:
            board (Board): The board state to evaluate.

        Returns:
            int: A numerical score where a positive value indicates an advantage for the AI,
                 and a negative value indicates an advantage for the opponent.
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

    def get_best_move(
        self, board: Board
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Determines the best move for the AI by performing iterative deepening
        from a starting depth (e.g., 4) up to a maximum depth (e.g., 5).

        Args:
            board (Board): The current board state.

        Returns:
            Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
                The best move found, represented as ((start_row, start_col), (end_row, end_col)).
                Returns None if no move is found.
        """
        best_move = None
        for depth in range(4, 6):
            self.transposition_table.clear()
            _, best_move = self.minimax(board, depth, float("-inf"), float("inf"), True)
        return best_move
