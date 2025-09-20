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

    def quiescence(self, board: Board, alpha: float, beta: float) -> int:
        """
        Extends search in volatile positions (captures, checks, promotions).
        Only evaluates when the position is quiet.
        """
        stand_pat = self.evaluate_board(board)

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Only consider captures (and possibly checks)
        for move in self.get_all_moves(board, self.color):
            start_pos, end_pos = move
            piece = board.board[start_pos[0]][start_pos[1]]
            target = board.board[end_pos[0]][end_pos[1]]
            if target is None:  # ignore quiet moves
                continue

            # Make the capture
            new_board = board.clone()
            new_board.move_piece(piece, start_pos, end_pos)

            score = -self.quiescence(new_board, -beta, -alpha)  # negamax style
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def minimax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        current_color: str,
    ) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Performs the Minimax algorithm with Alpha-Beta pruning and transposition table caching.

        Args:
            board (Board): The current board state.
            depth (int): The remaining depth to search.
            alpha (float): The current alpha value for pruning.
            beta (float): The current beta value for pruning.
            maximizing (bool): True if it's the maximizing player's turn, False for minimizing.
            current_color: str, The color of the current player ("w" or "b").

        Returns:
            Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
                A tuple where the first element is the evaluation score of the best move,
                and the second element is the best move in the format ((start_row, start_col), (end_row, end_col)).
                If no move is found, returns (score, None).
        """
        board_key = self.board_hash(board)
        if board_key in self.transposition_table:
            return self.transposition_table[board_key]

        # Depth reached → evaluate
        if depth == 0:
            # Use quiescence instead of immediate evaluation
            score = self.quiescence(board, alpha, beta)
            self.transposition_table[board_key] = (score, None)
            return score, None

        # Generate moves for current player
        moves = self.get_all_moves(board, current_color)

        # No moves → checkmate or stalemate
        if not moves:
            if board.is_check(current_color):  # checkmate
                score = -100000 if current_color == self.color else 100000
            else:  # stalemate
                score = 0
            self.transposition_table[board_key] = (score, None)
            return score, None

        best_move = None

        if maximizing:
            max_eval = float("-inf")
            for move in moves:
                start_pos, end_pos = move
                new_board = board.clone()
                piece = new_board.board[start_pos[0]][start_pos[1]]
                new_board.move_piece(piece, start_pos, end_pos)

                next_color = "b" if current_color == "w" else "w"
                eval_score, _ = self.minimax(
                    new_board, depth - 1, alpha, beta, False, next_color
                )

                if eval_score > max_eval:
                    max_eval, best_move = eval_score, move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            self.transposition_table[board_key] = (max_eval, best_move)
            return max_eval, best_move

        else:
            min_eval = float("inf")
            for move in moves:
                start_pos, end_pos = move
                new_board = board.clone()
                piece = new_board.board[start_pos[0]][start_pos[1]]
                new_board.move_piece(piece, start_pos, end_pos)

                next_color = "b" if current_color == "w" else "w"
                eval_score, _ = self.minimax(
                    new_board, depth - 1, alpha, beta, True, next_color
                )

                if eval_score < min_eval:
                    min_eval, best_move = eval_score, move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
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
        Evaluates the board using:
        - Material
        - Piece-square tables (PSTs)
        - King safety (opening vs endgame)
        - Pawn structure
        - Bishop pair bonus
        - Rook open/semi-open file bonus

        Returns:
            int: A positive score favors AI, negative favors opponent.
        """
        # Material values
        piece_values = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

        # Pawn piece-square table (midgame)
        pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5, 5, 10, 25, 25, 10, 5, 5],
            [0, 0, 0, 20, 20, 0, 0, 0],
            [5, -5, -10, 0, 0, -10, -5, 5],
            [5, 10, 10, -20, -20, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        # Knights
        knight_table = [
            [-50, -40, -30, -30, -30, -30, -40, -50],
            [-40, -20, 0, 0, 0, 0, -20, -40],
            [-30, 0, 10, 15, 15, 10, 0, -30],
            [-30, 5, 15, 20, 20, 15, 5, -30],
            [-30, 0, 15, 20, 20, 15, 0, -30],
            [-30, 5, 10, 15, 15, 10, 5, -30],
            [-40, -20, 0, 5, 5, 0, -20, -40],
            [-50, -40, -30, -30, -30, -30, -40, -50],
        ]

        # Bishops
        bishop_table = [
            [-20, -10, -10, -10, -10, -10, -10, -20],
            [-10, 5, 0, 0, 0, 0, 5, -10],
            [-10, 10, 10, 10, 10, 10, 10, -10],
            [-10, 0, 10, 10, 10, 10, 0, -10],
            [-10, 5, 5, 10, 10, 5, 5, -10],
            [-10, 0, 5, 10, 10, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -10, -10, -10, -10, -20],
        ]

        # Rooks
        rook_table = [
            [0, 0, 0, 5, 5, 0, 0, 0],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [-5, 0, 0, 0, 0, 0, 0, -5],
            [5, 10, 10, 10, 10, 10, 10, 5],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        # Queens
        queen_table = [
            [-20, -10, -10, -5, -5, -10, -10, -20],
            [-10, 0, 5, 0, 0, 0, 0, -10],
            [-10, 5, 5, 5, 5, 5, 0, -10],
            [0, 0, 5, 5, 5, 5, 0, -5],
            [-5, 0, 5, 5, 5, 5, 0, -5],
            [-10, 0, 5, 5, 5, 5, 0, -10],
            [-10, 0, 0, 0, 0, 0, 0, -10],
            [-20, -10, -10, -5, -5, -10, -10, -20],
        ]

        # King midgame table (stay safe)
        king_midgame_table = [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [20, 20, 0, 0, 0, 0, 20, 20],
            [20, 30, 10, 0, 0, 10, 30, 20],
        ]

        # King endgame table (move to center)
        king_endgame_table = [
            [-50, -40, -30, -20, -20, -30, -40, -50],
            [-40, -20, -10, 0, 0, -10, -20, -40],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-20, 0, 30, 40, 40, 30, 0, -20],
            [-20, 0, 30, 40, 40, 30, 0, -20],
            [-30, -10, 20, 30, 30, 20, -10, -30],
            [-40, -20, -10, 0, 0, -10, -20, -40],
            [-50, -40, -30, -20, -20, -30, -40, -50],
        ]

        def is_endgame(board: Board) -> bool:
            """
            Detects if the current position should be treated as endgame.
            Heuristic rules:
            - No queens = usually endgame (unless heavy material still exists).
            - Queen vs no queen but low support material = endgame.
            - Otherwise fallback on total non-pawn material count.
            """

            piece_values = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900}

            queens = {"w": 0, "b": 0}
            non_pawn_material = {"w": 0, "b": 0}

            for row in board.board:
                for piece in row:
                    if not piece:
                        continue
                    if piece.piece_type == "q":
                        queens[piece.color] += 1
                    elif piece.piece_type not in ("p", "k"):
                        non_pawn_material[piece.color] += piece_values[piece.piece_type]

            # --- Rule 1: No queens on the board → endgame
            if queens["w"] == 0 and queens["b"] == 0:
                return True

            # --- Rule 2: One queen only, but little support → endgame
            if queens["w"] == 1 and queens["b"] == 0 and non_pawn_material["w"] <= 800:
                return True
            if queens["b"] == 1 and queens["w"] == 0 and non_pawn_material["b"] <= 800:
                return True

            # --- Rule 3: Total material threshold (backup check)
            total_non_pawn = (
                non_pawn_material["w"]
                + non_pawn_material["b"]
                + queens["w"] * 900
                + queens["b"] * 900
            )
            return total_non_pawn <= 1400

        endgame = is_endgame(board)

        score = 0
        pawn_columns = {"w": [0] * 8, "b": [0] * 8}  # for pawn structure analysis
        bishop_count = {"w": 0, "b": 0}

        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if not piece:
                    continue

                base_value = piece_values[piece.piece_type]

                # Count bishops for bishop pair bonus
                if piece.piece_type == "b":
                    bishop_count[piece.color] += 1

                # --- PST selection ---
                if piece.piece_type == "p":
                    pst_bonus = (
                        pawn_table[row][col]
                        if piece.color == "w"
                        else pawn_table[7 - row][col]
                    )
                    pawn_columns[piece.color][col] += 1

                elif piece.piece_type == "n":
                    pst_bonus = (
                        knight_table[row][col]
                        if piece.color == "w"
                        else knight_table[7 - row][col]
                    )

                elif piece.piece_type == "b":
                    pst_bonus = (
                        bishop_table[row][col]
                        if piece.color == "w"
                        else bishop_table[7 - row][col]
                    )

                elif piece.piece_type == "r":
                    pst_bonus = (
                        rook_table[row][col]
                        if piece.color == "w"
                        else rook_table[7 - row][col]
                    )

                elif piece.piece_type == "q":
                    pst_bonus = (
                        queen_table[row][col]
                        if piece.color == "w"
                        else queen_table[7 - row][col]
                    )

                elif piece.piece_type == "k":
                    table = king_endgame_table if endgame else king_midgame_table
                    pst_bonus = (
                        table[row][col] if piece.color == "w" else table[7 - row][col]
                    )

                else:
                    pst_bonus = 0

                value = base_value + pst_bonus

                if piece.color == self.color:
                    score += value
                else:
                    score -= value

        # --- Pawn structure penalties ---
        for color in ["w", "b"]:
            penalty = 0
            for col in range(8):
                if pawn_columns[color][col] > 1:
                    penalty += 20 * (pawn_columns[color][col] - 1)  # doubled pawns
                if pawn_columns[color][col] > 0:
                    if (col == 0 or pawn_columns[color][col - 1] == 0) and (
                        col == 7 or pawn_columns[color][col + 1] == 0
                    ):
                        penalty += 15  # isolated pawn
            if color == self.color:
                score -= penalty

            else:
                score += penalty

        # --- Passed pawns bonus ---
        for color in ["w", "b"]:
            direction = -1 if color == "w" else 1
            for row in range(8):
                for col in range(8):
                    piece = board.board[row][col]
                    if not piece or piece.piece_type != "p" or piece.color != color:
                        continue

                    # Check enemy pawns ahead on same/adjacent files
                    passed = True
                    for adj_col in [col - 1, col, col + 1]:
                        if 0 <= adj_col < 8:
                            r = row + direction
                            while 0 <= r < 8:
                                enemy = board.board[r][adj_col]
                                if (
                                    enemy
                                    and enemy.piece_type == "p"
                                    and enemy.color != color
                                ):
                                    passed = False
                                    break
                                r += direction
                        if not passed:
                            break

                    if passed:
                        # Stronger as pawn advances & in endgame
                        rank = row if color == "b" else 7 - row
                        bonus = 10 * (7 - rank)  # closer to promotion = bigger bonus
                        if endgame:
                            bonus *= 2

                        if color == self.color:
                            score += bonus
                        else:
                            score -= bonus

        # Bishop pair bonus
        if bishop_count["w"] >= 2:
            score += 40 if self.color == "w" else -40
        if bishop_count["b"] >= 2:
            score += 40 if self.color == "b" else -40

        # Rook open/semi-open file bonus
        for col in range(8):
            has_white_pawn = any(
                board.board[row][col]
                and board.board[row][col].piece_type == "p"
                and board.board[row][col].color == "w"
                for row in range(8)
            )
            has_black_pawn = any(
                board.board[row][col]
                and board.board[row][col].piece_type == "p"
                and board.board[row][col].color == "b"
                for row in range(8)
            )
            for row in range(8):
                piece = board.board[row][col]
                if piece and piece.piece_type == "r":
                    bonus = 0
                    if piece.color == "w":
                        if not has_white_pawn and not has_black_pawn:
                            bonus = 25
                        elif not has_white_pawn:
                            bonus = 15
                    else:
                        if not has_black_pawn and not has_white_pawn:
                            bonus = 25
                        elif not has_black_pawn:
                            bonus = 15

                    if piece.color == self.color:
                        score += bonus
                    else:
                        score -= bonus

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
            _, best_move = self.minimax(
                board, depth, float("-inf"), float("inf"), True, self.color
            )
        return best_move
