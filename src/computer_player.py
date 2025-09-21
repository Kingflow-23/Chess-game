from typing import Tuple, Optional, List

from src.board import Board
from src.pieces import (
    King,
    Pawn,
    Rook,
    Queen,
    Bishop,
    Knight,
)  # import all piece classes used


class ComputerPlayer:
    """
    Computer chess player using Negamax (Negamax = Minimax in zero-sum symmetric form)
    with alpha-beta pruning, quiescence search, iterative deepening, transposition table,
    PST-based evaluation and light-weight make/undo for the search.

    Important behavior:
      - Prefers faster mate (score = MATE_SCORE - depth).
      - Applies a penalty to stalemate for side to move to avoid forcing stalemate when winning.
    """

    # scoring constants
    MATE_SCORE = 100000
    STALEMATE_PENALTY = 30000  # penalty applied to the side that stalemates (encourages avoiding stalemate)

    # --- Class-level PSTs to avoid rebuilding each evaluation ---
    piece_values = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

    # Piece-square tables
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

    def __init__(self, color: str) -> None:
        """
        Initializes the computer player with the given color and creates an empty transposition table.

        Args:
            color (str): The player's color ("w" for white, "b" for black).
        """

        self.color = color
        self.opponent_color = "w" if color == "b" else "b"
        self.transposition_table = {}  # Stores evaluated board states

        # --- Position repetition tracking ---
        self.position_counts = {}  # key: position key, value: occurrence count

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

    def get_position_key(self, board: Board, turn: str) -> str:
        # Piece placement
        board_str = ""
        for row in board.board:
            for piece in row:
                if piece:
                    board_str += piece.color + piece.piece_type
                else:
                    board_str += "--"

        # Castling rights (assumes board.rook_moved is a dict like {"w_kingside": False, ...})
        castling_str = "".join([k for k, v in board.rook_moved.items() if not v]) or "-"

        # En passant (only if a pawn can actually capture it)
        en_passant_str = "-"
        if getattr(board, "move_history", None):
            last_move = board.move_history[-1]
            if last_move["piece"].piece_type == "p":
                start_row, start_col = last_move["start"]
                end_row, end_col = last_move["end"]
                if abs(start_row - end_row) == 2:
                    ep_row = (start_row + end_row) // 2
                    ep_col = start_col
                    for dc in [-1, 1]:
                        adj_col = ep_col + dc
                        if 0 <= adj_col < 8:
                            adj_piece = board.board[ep_row][adj_col]
                            if (
                                adj_piece
                                and adj_piece.color != last_move["piece"].color
                                and adj_piece.piece_type == "p"
                            ):
                                en_passant_str = f"{ep_row}{ep_col}"
                                break

        return f"{board_str}_{turn}_{castling_str}_{en_passant_str}"

    # --- Lightweight move/undo for AI search ---
    def make_move_light(
        self, board: Board, start: Tuple[int, int], end: Tuple[int, int]
    ) -> dict:
        """
        Performs a lightweight move for AI search, including castling, promotion, and en passant.
        Returns info needed to undo the move.

        Args:
            board (Board): Board to operate on.
            start (Tuple[int,int]): Starting position (row, col).
            end (Tuple[int,int]): Ending position (row, col).

        Returns:
            dict: Information needed to undo the move.
        """
        piece = board.board[start[0]][start[1]]
        captured = board.board[end[0]][end[1]]
        move_info = {
            "piece": piece,
            "start": start,
            "end": end,
            "captured": captured,
            "king_pos": None,
            "castling": None,
            "en_passant": False,
            "promotion": None,
        }

        # --- Handle castling ---
        if isinstance(piece, King) and abs(start[1] - end[1]) == 2:
            move_info["castling"] = "kingside" if end[1] > start[1] else "queenside"
            rook_start_col = 7 if end[1] > start[1] else 0
            rook_end_col = start[1] + 1 if end[1] > start[1] else start[1] - 1
            rook = board.board[start[0]][rook_start_col]
            board.board[start[0]][rook_end_col] = rook
            board.board[start[0]][rook_start_col] = None
            rook.col = rook_end_col

        # --- Handle en passant ---
        elif isinstance(piece, Pawn) and captured is None and start[1] != end[1]:
            move_info["en_passant"] = True
            captured_row = start[0] if piece.color == "w" else start[0]
            captured_piece = board.board[start[0]][end[1]]  # pawn being captured
            move_info["captured"] = captured_piece
            board.board[start[0]][end[1]] = None

        # --- Move piece ---
        board.board[end[0]][end[1]] = piece
        board.board[start[0]][start[1]] = None
        piece.row, piece.col = end

        # --- Handle promotion ---
        if isinstance(piece, Pawn) and (end[0] == 0 or end[0] == 7):
            move_info["promotion"] = piece
            board.board[end[0]][end[1]] = Queen(
                end[0], end[1], piece.color
            )  # or a Queen
            piece = board.board[end[0]][end[1]]

        # --- Update king position ---
        if isinstance(piece, King):
            move_info["king_pos"] = (
                board.white_king if piece.color == "w" else board.black_king
            )
            if piece.color == "w":
                board.white_king = end
            else:
                board.black_king = end

        return move_info

    def undo_move_light(self, board: Board, move_info: dict):
        """
        Undoes a move made by `make_move_light`, including castling, promotion, and en passant.

        Args:
            board (Board): Board to operate on.
            move_info (dict): Move info returned by `make_move_light`.
        """
        piece = move_info["piece"]
        start, end = move_info["start"], move_info["end"]
        captured = move_info["captured"]

        # --- Undo promotion ---
        if move_info["promotion"]:
            board.board[end[0]][end[1]] = move_info["promotion"]
            piece = move_info["promotion"]

        # --- Undo castling ---
        if move_info["castling"]:
            rook_end_col = (
                start[1] + 1 if move_info["castling"] == "kingside" else start[1] - 1
            )
            rook_start_col = 7 if move_info["castling"] == "kingside" else 0
            rook = board.board[start[0]][rook_end_col]
            board.board[start[0]][rook_end_col] = None
            board.board[start[0]][rook_start_col] = rook
            rook.col = rook_start_col

        # --- Undo en passant ---
        if move_info["en_passant"]:
            captured_row = start[0] - 1 if piece.color == "w" else start[0] + 1
            board.board[captured_row][end[1]] = captured
            board.board[end[0]][end[1]] = None
            board.board[start[0]][start[1]] = piece
            piece.row, piece.col = start
            return

        # --- Normal undo ---
        board.board[start[0]][start[1]] = piece
        board.board[end[0]][end[1]] = captured
        piece.row, piece.col = start

        # --- Restore king position ---
        if isinstance(piece, King):
            if piece.color == "w":
                board.white_king = move_info["king_pos"]
            else:
                board.black_king = move_info["king_pos"]

    # --- Evaluation functions ---
    def is_endgame(self, board: Board) -> bool:
        """
        Determines whether the current position should be considered an endgame.

        Args:
            board (Board): Current board.

        Returns:
            bool: True if endgame, False otherwise.
        """
        queens = {"w": 0, "b": 0}
        non_pawn_material = {"w": 0, "b": 0}

        for row in board.board:
            for piece in row:
                if not piece:
                    continue

                if piece.piece_type == "q":
                    queens[piece.color] += 1

                elif piece.piece_type not in ("p", "k"):
                    non_pawn_material[piece.color] += self.piece_values[
                        piece.piece_type
                    ]

        if queens["w"] == 0 and queens["b"] == 0:
            return True

        if (
            queens["w"] == 1 and queens["b"] == 0 and non_pawn_material["w"] <= 800
        ) or (queens["b"] == 1 and queens["w"] == 0 and non_pawn_material["b"] <= 800):
            return True

        total_non_pawn = (
            non_pawn_material["w"]
            + non_pawn_material["b"]
            + queens["w"] * 900
            + queens["b"] * 900
        )

        return total_non_pawn <= 1400

    # --- Evaluate board ---
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
        endgame = self.is_endgame(board)

        # Piece-square tables
        pst = {
            "p": self.pawn_table,
            "n": self.knight_table,
            "b": self.bishop_table,
            "r": self.rook_table,
            "q": self.queen_table,
            "k": self.king_endgame_table if endgame else self.king_midgame_table,
        }

        score = 0
        pawn_columns = {"w": [0] * 8, "b": [0] * 8}
        bishop_count = {"w": 0, "b": 0}

        # --- Single pass over the board ---
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if not piece:
                    continue

                base_value = self.piece_values[piece.piece_type]
                pst_bonus = (
                    pst[piece.piece_type][row][col]
                    if piece.color == "w"
                    else pst[piece.piece_type][7 - row][col]
                )

                if piece.color == self.color:
                    score += base_value + pst_bonus
                else:
                    score -= base_value + pst_bonus

                # --- Pawn tracking for structure and passed pawns ---
                if piece.piece_type == "p":
                    pawn_columns[piece.color][col] += 1

                    # Passed pawn check (early exit once blocked)
                    direction = -1 if piece.color == "w" else 1
                    passed = True
                    for adj_col in [col - 1, col, col + 1]:
                        if 0 <= adj_col < 8:
                            r = row + direction
                            while 0 <= r < 8:
                                enemy = board.board[r][adj_col]
                                if (
                                    enemy
                                    and enemy.piece_type == "p"
                                    and enemy.color != piece.color
                                ):
                                    passed = False
                                    break  # blocked
                                r += direction
                        if not passed:
                            break
                    if passed:
                        rank = row if piece.color == "b" else 7 - row
                        bonus = 10 * (7 - rank)
                        if endgame:
                            bonus *= 2
                        score += bonus if piece.color == self.color else -bonus

                    # Isolated/doubled pawns will be calculated later

                elif piece.piece_type == "b":
                    bishop_count[piece.color] += 1

                elif piece.piece_type == "r":
                    # --- Inline rook file bonuses ---
                    has_white_pawn = pawn_columns["w"][col] > 0
                    has_black_pawn = pawn_columns["b"][col] > 0
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
                    score += bonus if piece.color == self.color else -bonus

        # --- Pawn structure penalties ---
        for color in ["w", "b"]:
            penalty = 0
            for col in range(8):
                if pawn_columns[color][col] > 1:
                    penalty += 20 * (pawn_columns[color][col] - 1)  # doubled
                if pawn_columns[color][col] > 0:
                    if (col == 0 or pawn_columns[color][col - 1] == 0) and (
                        col == 7 or pawn_columns[color][col + 1] == 0
                    ):
                        penalty += 15  # isolated
            score += -penalty if color == self.color else penalty

        # --- Bishop pair bonus ---
        for color in ["w", "b"]:
            if bishop_count[color] >= 2:
                score += 40 if color == self.color else -40

        return score

    def quiescence(
        self, board: Board, alpha: float, beta: float, color: str, depth: int = 0
    ) -> int:
        """
        Performs quiescence search to reduce horizon effect.

        Args:
            board (Board): Current board.
            alpha (float): Alpha value for pruning.
            beta (float): Beta value for pruning.
            color (str): Color to move.
            depth (int): Current depth in quiescence search.

        Returns:
            int: Evaluated score.
        """
        stand_pat = self.evaluate_board(board)
        if color != self.color:
            stand_pat = -stand_pat

        if stand_pat >= beta:
            return beta

        if alpha < stand_pat:
            alpha = stand_pat

        # Generate captures + checks
        moves = self.get_all_moves(board, color)

        if not moves:
            # No legal moves -> mate or stalemate
            if board.is_check(color):
                # side to move is checkmated -> huge negative (from perspective of side to move)
                return -self.MATE_SCORE + depth
            else:
                # stalemate -> draw
                return 0

        capture_or_check_moves = []

        for move in moves:
            target_piece = board.board[move[1][0]][move[1][1]]

            if target_piece is not None:
                capture_or_check_moves.append(move)

            else:
                # If the move results in a check, include it
                move_info = self.make_move_light(board, move[0], move[1])
                is_check = board.is_check("b" if color == "w" else "w")
                self.undo_move_light(board, move_info)
                if is_check:
                    capture_or_check_moves.append(move)

        # Search them
        for move in capture_or_check_moves:
            move_info = self.make_move_light(board, move[0], move[1])
            score = -self.quiescence(
                board, -beta, -alpha, "b" if color == "w" else "w", depth + 1
            )
            self.undo_move_light(board, move_info)

            if score >= beta:
                return beta

            alpha = max(alpha, score)

        return alpha

    def negamax(
        self,
        board: Board,
        depth: int,
        alpha: float,
        beta: float,
        color: str,
    ) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Negamax search with alpha-beta pruning, repetition handling, and transposition table.

        This function evaluates chess positions recursively using the negamax framework,
        which is equivalent to minimax but exploits symmetry to simplify logic.
        Scores are always returned from the perspective of the player to move.

        Args:
            board (Board): The current board state.
            depth (int): Remaining depth to search.
            alpha (float): Alpha bound for alpha-beta pruning (lower bound).
            beta (float): Beta bound for alpha-beta pruning (upper bound).
            color (str): Side to move ("w" or "b").

        Returns:
            Tuple[int, Optional[Tuple[start, end]]]:
                - The best evaluation score achievable from this position.
                - The corresponding best move (as ((row_from, col_from), (row_to, col_to))),
                or None if no move is available.

        Key Features:
            - **Repetition handling:**
                - Threefold repetition → treated as a draw (returns -STALEMATE_PENALTY).
                - Twofold repetition → discouraged with a soft penalty (-400 by default).
                - This prevents the engine from intentionally forcing perpetual checks
                unless there is no better option.

            - **Transposition table (TT):**
                - Uses a hash of the board position for caching evaluations.
                - If the position is already evaluated, returns the stored score/move
                adjusted for any repetition penalty.

            - **Terminal conditions:**
                - Depth == 0 → fall back to quiescence search for tactical stability.
                - No legal moves:
                    - If in check → checkmate (score = -MATE_SCORE + depth).
                    - Else → stalemate (score = -STALEMATE_PENALTY).

            - **Alpha-beta pruning:**
                - Cuts off branches when `alpha >= beta` to improve efficiency.

            - **Mate scoring:**
                - Checkmate is scored as `-MATE_SCORE + depth` (the sooner the mate,
                the higher the score for the mating side).
                - This ensures the engine prefers faster mates and delays being mated.

            - **Repetition penalty application:**
                - Applied consistently at all levels (leaf and recursive nodes).
                - Soft discouragement avoids draw loops unless forced.

        """
        # --- Generate position key ---
        pos_key = self.get_position_key(board, color)
        self.position_counts[pos_key] = self.position_counts.get(pos_key, 0) + 1

        repeat_count = self.position_counts[pos_key]

        # --- Handle repetition explicitly ---
        if repeat_count >= 3:
            # Threefold repetition = draw → treat as stalemate
            self.position_counts[pos_key] -= 1
            return -self.STALEMATE_PENALTY, None

        elif repeat_count == 2:
            # Apply soft penalty to discourage repetition loops
            repetition_penalty = 400

        else:
            repetition_penalty = 0

        # --- Transposition table ---
        board_key = hash(
            str([[p.piece_type if p else "-" for p in r] for r in board.board])
        )
        if board_key in self.transposition_table:
            self.position_counts[pos_key] -= 1
            stored_eval, stored_move = self.transposition_table[board_key]
            return stored_eval - repetition_penalty, stored_move

        # --- Depth 0: quiescence search ---
        if depth == 0:
            score = self.quiescence(board, alpha, beta, color) - repetition_penalty
            self.transposition_table[board_key] = (score, None)
            self.position_counts[pos_key] -= 1
            return score, None

        # --- Generate moves ---
        moves = self.get_all_moves(board, color)
        if not moves:
            if board.is_check(color):
                score = -self.MATE_SCORE + depth
            else:
                score = -self.STALEMATE_PENALTY
            self.transposition_table[board_key] = (score, None)
            self.position_counts[pos_key] -= 1
            return score, None

        best_move = None
        max_eval = float("-inf")

        for move in moves:
            move_info = self.make_move_light(board, move[0], move[1])
            eval_score, _ = self.negamax(
                board,
                depth - 1,
                -beta,
                -alpha,
                "b" if color == "w" else "w",
            )
            eval_score = -eval_score
            self.undo_move_light(board, move_info)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if alpha >= beta:
                break

        # Store in TT with penalty included
        max_eval -= repetition_penalty
        self.transposition_table[board_key] = (max_eval, best_move)

        # Decrement repetition count after recursion
        self.position_counts[pos_key] -= 1

        return max_eval, best_move

    def get_all_moves(
        self, board: Board, color: str
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Generates all legal moves for a given color.

        Args:
            board (Board): Current board.
            color (str): Color to move.

        Returns:
            List[Tuple[start, end]]: List of legal moves.
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.board[row][col]
                if piece and piece.color == color:
                    for dest in piece.valid_moves(board):
                        moves.append(((row, col), dest))

        # Sort moves: promotions > captures > others
        def score_move(move):
            start, end = move
            target = board.board[end[0]][end[1]]
            score = 0
            if target:
                score += (
                    10 * self.piece_values[target.piece_type]
                    - self.piece_values[board.board[start[0]][start[1]].piece_type]
                )
            # Bonus for pawn promotion (if applicable)
            piece = board.board[start[0]][start[1]]
            if piece.piece_type == "p" and (end[0] == 0 or end[0] == 7):
                score += 900
            return score

        moves.sort(key=score_move, reverse=True)
        return moves

    def get_best_move(
        self, board: Board, max_depth: int = 5
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Finds the best move using iterative deepening.

        Args:
            board (Board): Current board.
            max_depth (int): Maximum search depth.

        Returns:
            Optional[Tuple[start, end]]: Best move found.
        """
        best_move = None
        for depth in range(2, max_depth + 1):
            score, move = self.negamax(
                board, depth, float("-inf"), float("inf"), self.color
            )
            if move:
                best_move = move

            if score >= self.MATE_SCORE - 10:
                break

        return best_move
