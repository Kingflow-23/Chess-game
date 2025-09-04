from settings import *
from typing import List, Tuple, Optional


class Piece:
    """
    Base class for all chess pieces.

    Attributes:
        row (int): The row position of the piece on the board.
        col (int): The column position of the piece on the board.
        color (str): The color of the piece ('w' for white, 'b' for black).
        piece_type (str): The type of the piece ('p', 'r', 'n', 'b', 'q', 'k').
        image (pygame.Surface): The image representing the piece.

    Methods:
        valid_moves(board, last_move=None):
            Abstract method to be overridden by subclasses to define valid moves.

        draw(screen):
            Draws the piece on the board.
    """

    def __init__(self, row: int, col: int, color: str, piece_type: str) -> None:
        """
        Initializes a chess piece with its position, color, and type.

        Args:
            row (int): The row position of the piece.
            col (int): The column position of the piece.
            color (str): The piece's color ('w' for white, 'b' for black).
            piece_type (str): The type of the piece ('p', 'r', 'n', 'b', 'q', 'k').
        """
        self.row = row
        self.col = col
        self.color = color
        self.piece_type = piece_type

        # Load the corresponding piece image
        self.image = PIECES[f"{color}{piece_type}"]

    def valid_moves(
        self,
        board,
        last_move: Optional[Tuple["Piece", Tuple[int, int], Tuple[int, int]]] = None,
    ) -> List[Tuple[int, int]]:
        """
        Returns a list of valid moves for the piece.

        Args:
            board (Board): The board instance.
            last_move (Optional[Tuple[Piece, Tuple[int, int], Tuple[int, int]]]):
                The last move played, used for specific move rules (e.g., en passant).

        Returns:
            List[Tuple[int, int]]: A list of valid destination positions for the piece.
        """
        pass

    def safe_moves(self, board, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Filter out moves that would put the King in check.

        Args:
            board (Board()): The board instance to check for king safety.
            moves (list):  The list of moves to filter.

        Returns:
            safe_moves: The list of moves that do not put the King in check.
        """

        safe_moves = []
        original_position = (self.row, self.col)

        for move in moves:
            end_row, end_col = move
            captured_piece = board.board[end_row][end_col]

            # Simulate move
            board.board[self.row][self.col] = None
            board.board[end_row][end_col] = self
            self.row, self.col = end_row, end_col

            # Check king safety
            if not board.is_check(self.color):
                safe_moves.append(move)

            # Revert move
            board.board[original_position[0]][original_position[1]] = self
            board.board[end_row][end_col] = captured_piece
            self.row, self.col = original_position

        return safe_moves

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws the piece on the board at its current position.

        Args:
            screen (pygame.Surface): The game screen to draw the piece on.
        """
        piece_key = self.color + self.piece_type  # e.g., "wp" for white pawn

        piece_image = PIECES[piece_key]

        # Center the piece in the square
        offset_x = (SQUARE_SIZE - piece_image.get_width()) // 2
        offset_y = (SQUARE_SIZE - piece_image.get_height()) // 2

        screen.blit(
            piece_image,
            (self.col * SQUARE_SIZE + offset_x, self.row * SQUARE_SIZE + offset_y),
        )

    def clone(self):
        """
        Creates a copy of the piece with the same attributes.

        Returns:
            Piece: A new instance of the same piece.
        """
        return type(self)(self.row, self.col, self.color)


class Pawn(Piece):
    """
    Represents a Pawn piece.

    Attributes:
        direction (int): Movement direction (-1 for white, +1 for black).
        start_row (int): The starting row of the pawn (6 for white, 1 for black).

    Methods:
        valid_moves(board, last_move=None):
            Returns a list of valid moves for the pawn, including en passant.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "p")
        self.direction = -1 if color == "w" else 1
        self.start_row = 6 if color == "w" else 1

    def valid_moves(self, board, last_move=None):
        """
        Computes the valid moves for the pawn.

        Args:
            board (Board()): Instance of the Board class.
            last_move (tuple[Piece, tuple[int, int], tuple[int, int]] | None):
                The last move played, used for en passant.

        Returns:
            list[tuple[int, int]]: A list of valid moves for the pawn.
        """
        moves = []
        forward_row = self.row + self.direction

        # Normal one-step forward move
        if 0 <= forward_row < 8 and board.board[forward_row][self.col] is None:
            moves.append((forward_row, self.col))

        # Two-step move from starting position
        if self.row == self.start_row and board.board[forward_row][self.col] is None:
            double_step_row = self.row + 2 * self.direction
            if (
                0 <= double_step_row < 8
                and board.board[double_step_row][self.col] is None
            ):
                moves.append((double_step_row, self.col))

        # Capture diagonally
        for side_col in [self.col - 1, self.col + 1]:
            if (
                0 <= side_col < 8 and 0 <= forward_row < 8
            ):  # Ensure forward_row is within bounds
                if (
                    board.board[forward_row][side_col]
                    and board.board[forward_row][side_col].color != self.color
                ):
                    moves.append((forward_row, side_col))

            # **En Passant Handling**
            if last_move:
                last_piece, last_start, last_end = last_move

                if (
                    isinstance(last_piece, Pawn)
                    and abs(last_start[0] - last_end[0]) == 2
                ):
                    last_move_row, last_move_col = last_end

                    # En Passant condition: the last pawn must be adjacent and in the row behind
                    if last_move_row == self.row and abs(last_move_col - self.col) == 1:
                        if (
                            board.board[self.row + self.direction][last_move_col]
                            is None
                        ):
                            moves.append((self.row + self.direction, last_move_col))

        return self.safe_moves(board, moves)


class Rook(Piece):
    """
    Represents a Rook piece.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "r")

    def valid_moves(self, board, last_move=None):
        """
        Computes the valid moves for the rook.

        Returns:
            list[tuple[int, int]]: A list of valid moves for the rook.
        """
        moves = []
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Up, Down, Right, Left

        for d_row, d_col in directions:
            r, c = self.row, self.col
            while 0 <= r + d_row < 8 and 0 <= c + d_col < 8:
                r += d_row
                c += d_col
                if board.board[r][c] is None:
                    moves.append((r, c))
                elif board.board[r][c].color != self.color:
                    moves.append((r, c))
                    break  # Stop moving in this direction if an enemy is captured
                else:
                    break  # Stop moving if a friendly piece is blocking

        return self.safe_moves(board, moves)


class Knight(Piece):
    """
    Represents a Knight piece with its unique movement pattern.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "n")

    def valid_moves(self, board, last_move=None):
        """
        Computes the valid moves for the knight.

        Returns:
            list[tuple[int, int]]: A list of valid moves for the knight.
        """
        moves = []
        knight_moves = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]

        for d_row, d_col in knight_moves:
            r, c = self.row + d_row, self.col + d_col
            if 0 <= r < 8 and 0 <= c < 8:
                if board.board[r][c] is None or board.board[r][c].color != self.color:
                    moves.append((r, c))

        return self.safe_moves(board, moves)


class Bishop(Piece):
    """
    Represents a Bishop piece that moves diagonally.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "b")

    def valid_moves(self, board, last_move=None):
        """
        Computes the valid moves for the bishop.

        Returns:
            list[tuple[int, int]]: A list of valid moves for the bishop.
        """
        moves = []
        directions = [(1, 1), (-1, -1), (1, -1), (-1, 1)]  # Diagonal directions

        for d_row, d_col in directions:
            r, c = self.row, self.col
            while 0 <= r + d_row < 8 and 0 <= c + d_col < 8:
                r += d_row
                c += d_col
                if board.board[r][c] is None:
                    moves.append((r, c))
                elif board.board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break

        return self.safe_moves(board, moves)


class Queen(Piece):
    """
    Represents a Queen piece, combining Rook and Bishop movements.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "q")

    def valid_moves(self, board, last_move=None):
        moves = []

        # Use the Queen's position to simulate Rook and Bishop moves
        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),  # Rook-like moves (vertical & horizontal)
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),  # Bishop-like moves (diagonal)
        ]

        for drow, dcol in directions:
            r, c = self.row + drow, self.col + dcol
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board.board[r][c]
                if piece:
                    if piece.color != self.color:  # Capture opponent's piece
                        moves.append((r, c))
                    break  # Stop if there's a piece blocking
                moves.append((r, c))
                r += drow
                c += dcol

        return self.safe_moves(board, moves)


class King(Piece):
    """
    Represents a King piece that moves one step in any direction.
    """

    def __init__(self, row, col, color):
        super().__init__(row, col, color, "k")

    def valid_moves(self, board, last_move=None):
        moves = []
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, -1),
            (1, -1),
            (-1, 1),
        ]

        for d_row, d_col in directions:
            r, c = self.row + d_row, self.col + d_col
            if 0 <= r < 8 and 0 <= c < 8:
                if board.board[r][c] is None or board.board[r][c].color != self.color:
                    if not board.is_check_after_move(self, (r, c)):
                        moves.append((r, c))

        # ✅ Check for castling rights
        castling = board.can_castle(
            self.color
        )  # Get dict {"kingside": True/False, "queenside": True/False}
        row = 7 if self.color == "w" else 0

        if castling["kingside"]:
            moves.append((row, 6))

        if castling["queenside"]:
            moves.append((row, 2))

        return moves
