from typing import List, Optional, Tuple, Dict, Any

from settings import *

from src.pieces import *


class Board:
    """
    Represents a chessboard and manages game logic, including piece placement, movement,
    special rules, and game state checks.
    """

    def __init__(self) -> None:
        """
        Initializes the chessboard with pieces in their starting positions.
        Tracks the positions of kings and castling rights.
        """
        self.board = self.create_board()
        self.white_king = (7, 4)  # Track king positions for check/checkmate
        self.black_king = (0, 4)
        self.king_moved = {"w": False, "b": False}
        self.rook_moved = {
            "w_kingside": False,
            "w_queenside": False,
            "b_kingside": False,
            "b_queenside": False,
        }

    def clone(self) -> "Board":
        """
        Creates and returns a deep copy of the board state.
        This clone method duplicates the board matrix using each piece's clone method,
        along with king and rook moved flags.

        Returns:
            Board: A new Board instance with the same state.
        """
        # Create a new Board instance without calling __init__
        new_board = Board.__new__(Board)
        # Manually copy the board matrix using each piece's clone method
        new_board.board = [
            [piece.clone() if piece is not None else None for piece in row]
            for row in self.board
        ]
        new_board.white_king = self.white_king
        new_board.black_king = self.black_king
        new_board.king_moved = self.king_moved.copy()
        new_board.rook_moved = self.rook_moved.copy()
        return new_board

    def create_board(self) -> List[List[Optional[Piece]]]:
        """
        Initializes the board with chess pieces in their standard starting positions.

        Returns:
            List[List[Optional[Piece]]]: A 2D list representing the chessboard with pieces
                                         placed in their starting positions.
        """
        board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        starting_positions = [
            ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
        ]

        piece_classes = {
            "p": Pawn,
            "r": Rook,
            "n": Knight,
            "b": Bishop,
            "q": Queen,
            "k": King,
        }

        for row in range(ROWS):
            for col in range(COLS):
                piece_code = starting_positions[row][col]
                if piece_code:
                    color = piece_code[0]
                    piece_type = piece_code[1]
                    board[row][col] = piece_classes[piece_type](row, col, color)

        return board

    def draw(self, screen: pygame.Surface, flipped: bool = False) -> None:
        """
        Draws the chessboard along with all the pieces onto the provided screen.
        Also highlights the king in red if it is in check.

        Args:
            screen (pygame.Surface): The display surface on which to draw the board.
        """
        # Determine if white or black king is in check
        white_in_check = self.is_check("w")
        black_in_check = self.is_check("b")

        # Draw the board
        for row in range(ROWS):
            for col in range(COLS):

                x, y = self.to_screen_coords(row, col, flipped)

                # Default square color
                color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN

                # Highlight king in red if in check
                if (white_in_check and (row, col) == self.white_king) or (
                    black_in_check and (row, col) == self.black_king
                ):
                    color = (255, 0, 0)  # Red color for check

                pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

        # Draw the pieces on top of the squares
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece:
                    piece.draw(self, screen, flipped)

    def to_screen_coords(
        self, row: int, col: int, flipped: bool = False
    ) -> Tuple[int, int]:
        """
        Convert board coordinates (row, col) -> top-left screen pixel (x, y).
        If flipped is True it returns coords for black's perspective (board rotated 180°).
        """
        if not flipped:
            return col * SQUARE_SIZE, row * SQUARE_SIZE
        # flipped: mirror both axes
        return (COLS - 1 - col) * SQUARE_SIZE, (ROWS - 1 - row) * SQUARE_SIZE

    def from_screen_coords(self, x: int, y: int, flipped: bool) -> Tuple[int, int]:
        """Convert screen pixel coordinates back to board (row, col)."""
        col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
        if flipped:
            row = ROWS - 1 - row
            col = COLS - 1 - col
        return row, col

    def highlight_valid_moves(
        self,
        screen: pygame.Surface,
        selected_piece: Piece,
        last_move: Tuple[Any, Tuple[int, int], Tuple[int, int]],
        flipped: bool = False,
    ) -> None:
        """
        Highlights valid moves for the selected piece.

        Args:
            screen (pygame.Surface): The game display surface.
            selected_piece (Piece): The currently selected piece.
            last_move (tuple): The last move made (piece, start_pos, end_pos).

        Returns:
            None
        """
        if not selected_piece:
            return  # No piece selected, exit early

        valid_moves = selected_piece.valid_moves(self, last_move)
        current_pos = (selected_piece.row, selected_piece.col)

        for move in valid_moves:
            color = (0, 255, 0)  # Default: Green (valid move)

            # Check if the move captures an enemy piece
            if (
                self.board[move[0]][move[1]]
                and self.board[move[0]][move[1]].color != selected_piece.color
            ):
                color = (255, 0, 0)  # Red (capture move)

            # Check for En Passant
            if isinstance(selected_piece, Pawn) and self.is_en_passant(
                selected_piece, current_pos, move, last_move
            ):
                color = (255, 0, 0)  # Red for en passant capture

            # Check for Castling
            if isinstance(selected_piece, King):
                if self.is_castle(selected_piece, current_pos, move):
                    color = (0, 0, 255)  # Blue for castling move

            # Convert to screen coords
            x, y = self.to_screen_coords(move[0], move[1], flipped)
            pygame.draw.circle(
                screen,
                color,
                (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2),
                10,
            )

    def highlight_last_move(
        self,
        screen: pygame.Surface,
        last_move: Tuple[Tuple[int, int], Tuple[int, int]],
        was_there_enemy: bool,
        flipped: bool = False,
    ) -> None:
        """
        Highlights the last move made on the board.

        Args:
            screen (pygame.Surface): The game display surface.
            last_move (tuple): The last move made (start_pos, end_pos).
            was_there_enemy (bool): True if an enemy piece was captured.

        Returns:
            None
        """
        if not last_move:
            return  # No last move to highlight

        start_pos, end_pos = last_move
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # Define colors
        yellow = (255, 255, 0)  # Normal move highlight
        red = (255, 0, 0)  # Capture highlight

        # Convert to screen coords
        start_x, start_y = self.to_screen_coords(start_row, start_col, flipped)
        end_x, end_y = self.to_screen_coords(end_row, end_col, flipped)

        # Highlight the start square (Yellow Border)
        pygame.draw.rect(
            screen, yellow, pygame.Rect(start_x, start_y, SQUARE_SIZE, SQUARE_SIZE), 5
        )

        # Highlight the destination square
        pygame.draw.rect(
            screen,
            red if was_there_enemy else yellow,
            pygame.Rect(end_x, end_y, SQUARE_SIZE, SQUARE_SIZE),
            5,
        )

    def is_en_passant(
        self,
        piece: Piece,
        start: Tuple[int, int],
        end: Tuple[int, int],
        last_move: Tuple[Any, Tuple[int, int], Tuple[int, int]],
    ) -> bool:
        """
        Checks if an en passant capture is possible.

        Args:
            piece (Piece): The pawn attempting en passant.
            start (tuple): The (row, col) position of the moving pawn.
            end (tuple): The target (row, col) position.
            last_move (tuple): The last move made (moved piece, start position, end position).

        Returns:
            bool: True if en passant is legal, False otherwise.
        """

        if isinstance(piece, Pawn) and last_move:
            last_move_piece, last_move_start, last_move_end = last_move

            # Ensure the last move was a pawn moving two squares forward
            if (
                isinstance(last_move_piece, Pawn)
                and abs(last_move_start[0] - last_move_end[0]) == 2
            ):

                # Check if the last moved pawn is adjacent
                if abs(last_move_end[1] - start[1]) == 1:
                    if last_move_end[0] == start[0]:
                        # Check if en passant is valid for white
                        if (
                            piece.color == "w"
                            and last_move_piece.color == "b"
                            and start[0] == 3
                            and end[0] == 2
                            and end[1] == last_move_end[1]
                        ):
                            return True
                        # Check if en passant is valid for black
                        if (
                            piece.color == "b"
                            and last_move_piece.color == "w"
                            and start[0] == 4
                            and end[0] == 5
                            and end[1] == last_move_end[1]
                        ):
                            return True

        return False

    def move_piece(
        self,
        piece: Piece,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        last_move: Optional[Tuple[Any, Tuple[int, int], Tuple[int, int]]] = None,
        game: Optional[Any] = None,
    ) -> None:
        """
        Moves a chess piece from start_pos to end_pos, handling special moves such as castling,
        en passant, and pawn promotion.

        Args:
            piece (Piece): The chess piece being moved.
            start_pos (tuple): The (row, col) position where the piece starts.
            end_pos (tuple): The (row, col) position where the piece moves.
            last_move (tuple): The last move made (piece, start, end), used for en passant.
            game (Game): The current game instance.

        Returns:
            None
        """
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        if piece:
            if isinstance(piece, King):  # Track king's position for check detection
                if piece.color == "w":
                    self.white_king = (end_row, end_col)
                else:
                    self.black_king = (end_row, end_col)

                self.king_moved[piece.color] = True

                # Handle castling move
                castling_type = self.is_castle(piece, start_pos, end_pos)
                if castling_type:
                    rook_start_col = 7 if castling_type == "kingside" else 0
                    rook_end_col = 5 if castling_type == "kingside" else 3

                    # Move the rook
                    rook = self.board[start_row][rook_start_col]
                    if isinstance(rook, Rook) and rook.color == piece.color:
                        self.board[start_row][rook_start_col] = None
                        self.board[start_row][rook_end_col] = rook
                        rook.col = rook_end_col
                    ""
                    # Update piece's state
                    self.king_moved[piece.color] = True
                    self.rook_moved[f"{piece.color}_{castling_type}"] = True

            if isinstance(piece, Rook):
                self.rook_moved[
                    f"{piece.color}_{'kingside' if piece.col >= 4 else 'queenside'}"
                ] = True

            # En Passant Handling
            if isinstance(piece, Pawn) and last_move:
                _, _, last_move_end = last_move

                if self.is_en_passant(piece, start_pos, end_pos, last_move):
                    self.board[last_move_end[0]][
                        last_move_end[1]
                    ] = None  # Remove the captured pawn

            # **🔹 Pawn Promotion Handling**
            if isinstance(piece, Pawn) and (end_row == 0 or end_row == 7):
                if game is not None:
                    self.draw(game.screen)
                    promoted_piece = game.ask_promotion_choice(
                        piece, (end_row, end_col)
                    )  # Get promoted piece
                else:
                    # Default to Queen if no game instance is provided
                    promoted_piece = Queen(end_row, end_col, piece.color)

                self.board[end_row][
                    end_col
                ] = promoted_piece  # Replace pawn with new piece
                promoted_piece.row, promoted_piece.col = end_row, end_col

            else:
                self.board[end_row][end_col] = piece

            # Clear old position
            self.board[start_row][start_col] = None
            piece.row, piece.col = end_row, end_col

    def can_castle(self, color: str) -> Dict[str, bool]:
        """
        Checks whether castling is legal for the given color.

        Args:
            color (str): The player's color ('w' or 'b').

        Returns:
            Dict[str, bool]: A dictionary indicating castling rights.
                             For example: {"kingside": True, "queenside": False}.
        """
        row = 7 if color == "w" else 0
        king_col = 4

        castling_rights = {"kingside": False, "queenside": False}

        # Ensure the king is in the correct position and has not moved
        king = self.board[row][king_col]
        if king is None or not isinstance(king, King) or self.king_moved[color]:
            return castling_rights  # King has moved or is not in the correct position

        # Kingside Castling (King moves two squares to the right)
        rook_col = 7
        if not self.rook_moved.get(f"{color}_kingside", True):
            if (
                self.board[row][rook_col] is not None
                and isinstance(self.board[row][rook_col], Rook)
                and all(
                    self.board[row][col] is None for col in [5, 6]
                )  # f, g must be empty
                and not any(
                    self.is_check(color, (row, col)) for col in [4, 5, 6]
                )  # King can't pass through check
            ):
                castling_rights["kingside"] = True

        # Queenside Castling (King moves two squares to the left)
        rook_col = 0
        if not self.rook_moved.get(f"{color}_queenside", True):
            if (
                self.board[row][rook_col] is not None
                and isinstance(self.board[row][rook_col], Rook)
                and all(
                    self.board[row][col] is None for col in [1, 2, 3]
                )  # b, c, d must be empty
                and not any(
                    self.is_check(color, (row, col)) for col in [4, 3, 2]
                )  # King can't pass through check
            ):
                castling_rights["queenside"] = True

        return castling_rights

    def is_castle(
        self, piece: Piece, start: Tuple[int, int], end: Tuple[int, int]
    ) -> Optional[str]:
        """
        Determines if the given move is a castling move.

        Args:
            piece (Piece): The piece being moved (should be a king).
            start (tuple): The starting position (row, col).
            end (tuple): The ending position (row, col).

        Returns:
            Optional[str]: 'kingside' if the move is kingside castling, 'queenside' if queenside castling,
                           or None if the move is not a castling move.
        """
        if not isinstance(piece, King):  # Ensure it's a king
            return None

        start_row, start_col = start
        end_row, end_col = end

        # King must move two squares horizontally
        if start_row == end_row and abs(start_col - end_col) == 2:
            if end_col > start_col:  # Moving right -> Kingside castling
                return "kingside"
            else:  # Moving left -> Queenside castling
                return "queenside"

        return None  # Not a castling move

    def is_check(
        self, color: str, checked_pos: Optional[Tuple[int, int]] = None
    ) -> bool:
        """
        Determines if the king of the specified color is in check.

        Args:
            color (str): The player's color ('w' or 'b').
            checked_pos (Optional[Tuple[int, int]]): The position to check;
                                                     if None, uses the current king position.

        Returns:
            bool: True if the king is in check, False otherwise.
        """
        if checked_pos:
            king_row, king_col = checked_pos
        else:
            king_pos = self.white_king if color == "w" else self.black_king
            king_row, king_col = king_pos

        opponent_color = "b" if color == "w" else "w"

        # Define possible directions of attack
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),  # Vertical & horizontal (Rook, Queen)
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),  # Diagonal (Bishop, Queen)
        ]

        # 1️⃣ Check for Rook & Queen (straight-line attacks)
        for drow, dcol in directions[:4]:  # First four are straight lines
            r, c = king_row + drow, king_col + dcol
            while 0 <= r < ROWS and 0 <= c < COLS:
                piece = self.board[r][c]
                if piece:
                    if piece.color == opponent_color and isinstance(
                        piece, (Rook, Queen)
                    ):
                        return True  # King is in check
                    break  # Stop searching if a piece blocks
                r += drow
                c += dcol

        # 2️⃣ Check for Bishop & Queen (diagonal attacks)
        for drow, dcol in directions[4:]:  # Last four are diagonals
            r, c = king_row + drow, king_col + dcol
            while 0 <= r < ROWS and 0 <= c < COLS:
                piece = self.board[r][c]
                if piece:
                    if piece.color == opponent_color and isinstance(
                        piece, (Bishop, Queen)
                    ):
                        return True
                    break
                r += drow
                c += dcol

        # 3️⃣ Check for Knights
        knight_moves = [
            (-2, -1),
            (-2, 1),
            (2, -1),
            (2, 1),
            (-1, -2),
            (-1, 2),
            (1, -2),
            (1, 2),
        ]
        for dr, dc in knight_moves:
            r, c = king_row + dr, king_col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                piece = self.board[r][c]
                if (
                    piece
                    and piece.color == opponent_color
                    and isinstance(piece, Knight)
                ):
                    return True  # King is in check

        # 4️⃣ Check for Pawn Attacks
        pawn_attack_rows = (
            [-1, 1] if color == "w" else [1, -1]
        )  # White pawns attack upwards, black downwards
        for dr in pawn_attack_rows:
            for dc in [-1, 1]:  # Pawns attack diagonally
                r, c = king_row + dr, king_col + dc
                if 0 <= r < ROWS and 0 <= c < COLS:
                    piece = self.board[r][c]
                    if (
                        piece
                        and piece.color == opponent_color
                        and isinstance(piece, Pawn)
                    ):
                        return True  # King is in check

        # 5️⃣ Check for Opponent King (Adjacent Squares)
        king_moves = directions + [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for dr, dc in king_moves:
            r, c = king_row + dr, king_col + dc
            if 0 <= r < ROWS and 0 <= c < COLS:
                piece = self.board[r][c]
                if piece and piece.color == opponent_color and isinstance(piece, King):
                    return True  # King is in check

        return False  # No check detected

    def is_check_after_move(self, king: King, new_pos: Tuple[int, int]) -> bool:
        """
        Simulates moving the King to a new position and checks if it would be in check.

        Args:
            king (King): The King piece to test.
            new_pos (tuple): The (row, col) position to check.

        Returns:
            bool: True if the King would be in check at new_pos, False otherwise.
        """
        original_position = self.white_king if king.color == "w" else self.black_king
        captured_piece = self.board[new_pos[0]][new_pos[1]]

        # Update the king's position before simulating the move
        if king.color == "w":
            self.white_king = new_pos
        else:
            self.black_king = new_pos

        # Simulate moving the king
        self.board[original_position[0]][original_position[1]] = None
        self.board[new_pos[0]][new_pos[1]] = king
        king.row, king.col = new_pos

        # Check if the king is in check at the new position
        in_check = self.is_check(king.color)

        # Revert move
        self.board[original_position[0]][original_position[1]] = king
        self.board[new_pos[0]][new_pos[1]] = captured_piece
        king.row, king.col = original_position

        # Restore the king's position after checking
        if king.color == "w":
            self.white_king = original_position
        else:
            self.black_king = original_position

        return in_check

    def is_checkmate(self, color: str) -> bool:
        """
        Determines if the given player is in checkmate (no legal moves to escape check).

        Args:
            color (str): The color of the player ('w' for white, 'b' for black).

        Returns:
            bool: True if the player is in checkmate, False otherwise.
        """
        if not self.is_check(color):
            return False  # Can't be checkmate if not in check

        # Loop over all pieces of the given color
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    if piece.valid_moves(
                        self
                    ):  # If the piece has ANY valid moves, no checkmate
                        return False

        return True  # No moves escape check, so it's checkmate

    def is_stalemate(self, color: str) -> bool:
        """
        Determines if the given player is in stalemate (no legal moves, but not in check).

        Args:
            color (str): The color of the player ('w' for white, 'b' for black).

        Returns:
            bool: True if the game is in stalemate, False otherwise.
        """
        if self.is_check(color):
            return False  # Can't be stalemate if in check

        # Loop over all pieces of the given color
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    if piece.valid_moves(
                        self
                    ):  # If the piece has ANY valid moves, no stalemate
                        return False

        return True  # No moves available, so it's stalemate
