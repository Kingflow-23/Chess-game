import sys
import pygame

from pieces import *
from settings import *
from board import Board


class Game:
    def __init__(self):
        """
        Initializes the game, sets up the display, and creates the board.
        Also sets the initial game state, including which player's turn it is.
        """
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess Game")
        self.board = Board()
        self.selected_piece = None
        self.turn = "w"  # White starts
        self.running = True
        self.setup_phase()  # Call setup_phase to select game mode

    def setup_phase(self):
        """
        Displays the initial menu to choose the game mode.
        Options include Player vs Player, Player vs Computer, and Help.
        The game proceeds based on the user's selection.
        """
        background = pygame.image.load("background/title.jpg")
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        font = pygame.font.Font(None, 48)
        title_font = pygame.font.Font(None, 72)

        title_text = title_font.render("Chess Game", True, (255, 255, 255))
        author_text = font.render("Created by KingFlow-23", True, (200, 200, 200))
        pvp_text = font.render("1. Player vs Player", True, (255, 255, 255))
        pvc_text = font.render("2. Player vs Computer", True, (255, 255, 255))
        help_text = font.render("3. Help", True, (255, 255, 255))

        # Define button areas (rectangles)
        pvp_rect = pygame.Rect(
            WIDTH // 2 - 150, HEIGHT // 2.7, pvp_text.get_width(), pvp_text.get_height()
        )
        pvc_rect = pygame.Rect(
            WIDTH // 2 - 150, HEIGHT // 2.3, pvc_text.get_width(), pvc_text.get_height()
        )
        help_rect = pygame.Rect(
            WIDTH // 2 - 150, HEIGHT // 2, help_text.get_width(), help_text.get_height()
        )

        running = True
        while running:
            self.screen.blit(background, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 6 - 50))
            self.screen.blit(author_text, (WIDTH // 2 - 190, HEIGHT // 4 - 50))
            self.screen.blit(pvp_text, (WIDTH // 2 - 150, HEIGHT // 2.7))
            self.screen.blit(pvc_text, (WIDTH // 2 - 150, HEIGHT // 2.3))
            self.screen.blit(help_text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_mode = "pvp"
                        running = False
                    if event.key == pygame.K_2:
                        self.game_mode = "pvc"
                        running = False
                    if event.key == pygame.K_3:
                        self.game_mode = "help"
                        running = False

                # Mouse controls (check if the mouse clicks on a menu item)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        mouse_pos = pygame.mouse.get_pos()
                        if pvp_rect.collidepoint(mouse_pos):
                            self.game_mode = "pvp"
                            running = False
                        elif pvc_rect.collidepoint(mouse_pos):
                            self.game_mode = "pvc"
                            running = False
                        elif help_rect.collidepoint(mouse_pos):
                            self.game_mode = "help"
                            running = False

                # Highlight menu options on mouse hover
                if event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    if pvp_rect.collidepoint(mouse_pos):
                        pvp_text = font.render(
                            "1. Player vs Player", True, (255, 255, 0)
                        )  # Yellow for hover
                    else:
                        pvp_text = font.render(
                            "1. Player vs Player", True, (255, 255, 255)
                        )  # White by default

                    if pvc_rect.collidepoint(mouse_pos):
                        pvc_text = font.render(
                            "2. Player vs Computer", True, (255, 255, 0)
                        )
                    else:
                        pvc_text = font.render(
                            "2. Player vs Computer", True, (255, 255, 255)
                        )

                    if help_rect.collidepoint(mouse_pos):
                        help_text = font.render("3. Help", True, (255, 255, 0))
                    else:
                        help_text = font.render("3. Help", True, (255, 255, 255))

    def display_help(self):
        """
        Displays a help screen with instructions for the user on how to play the game.
        The screen provides key controls and rules, and waits for user input to return to the main menu.
        """
        self.screen.fill((0, 0, 0))  # Fill the screen with black to create a background
        title_font = pygame.font.Font(None, 48)
        font = pygame.font.Font(None, 36)  # Set font for the instructions

        # Instructions and game controls
        title_text = title_font.render("Chess Game Help", True, (255, 255, 255))
        instructions_text = [
            "",
            "Welcome to my Chess Game!",
            "Use your mouse to select and move pieces.",
            "Press 'S' to toggle showing valid moves.",
            "Press 'Z' to surrender.",
            "Press 'B' to undo a move.",
            "Press 'Y' to redo an undone move.",
            "Press 'Backspace' to quit.",
            "Press 'Enter' to restart the game.",
            "",
            "Press 'Enter' when you're done with the help screen",
            "",
            "Have fun playing!",
        ]

        # Display title
        self.screen.blit(
            title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4)
        )

        # Display instructions
        y_offset = HEIGHT // 4 + 50  # Start below the title
        for line in instructions_text:
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 40  # Increase y_offset for the next line of text

        # Update the display
        pygame.display.flip()

        # Wait for the user to press any key to return to the main menu
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    waiting = False  # Exit help screen when a key is pressed
                    if event.key == pygame.K_BACKSPACE:
                        pygame.quit()
                        sys.exit()  # Exit the game if Backspace is pressed
                    elif event.key == pygame.K_RETURN:
                        self.setup_phase()  # Return to the main menu if Enter is pressed

    def undo_move(self):
        """
        Undoes the most recent move made during the game.
        Restores the board to the state before the last move and reverts any captured pieces.
        Also switches the turn back to the other player.
        """
        if self.move_history:
            last_move = self.move_history.pop()

            # Undo the move
            piece = last_move["piece"]
            start_row, start_col = last_move["start"]
            end_row, end_col = last_move["end"]
            captured_piece = last_move["captured"]
            was_en_passant = last_move.get(
                "en_passant", False
            )  # Check if en passant happened
            was_castling = last_move.get("castling", None)  # Check if castling happened
            was_promotion = last_move.get("promotion", False)
            king_moved = last_move.get("king_moved", None)
            rook_moved = last_move.get("rook_moved", None)

            if was_castling == "kingside":
                self.board.board[start_row][start_col] = piece  # Restore the king
                self.board.board[end_row][6] = None  # Clear the castled king's position

                if self.board.board[start_row][5]:  # Ensure there's a rook to move
                    self.board.board[start_row][7] = self.board.board[start_row][
                        5
                    ]  # Move the rook back
                    self.board.board[start_row][5] = None  # Clear its previous position
                    self.board.board[start_row][
                        7
                    ].col = 7  # Restore rook's original column

            elif was_castling == "queenside":
                self.board.board[start_row][start_col] = piece  # Restore the king
                self.board.board[end_row][2] = None  # Clear the castled king's position

                if self.board.board[start_row][3]:  # Ensure there's a rook to move
                    self.board.board[start_row][0] = self.board.board[start_row][
                        3
                    ]  # Move the rook back
                    self.board.board[start_row][3] = None  # Clear its previous position
                    self.board.board[start_row][
                        0
                    ].col = 0  # Restore rook's original column

            else:
                # Place the piece back to its start position
                self.board.board[start_row][start_col] = piece
                self.board.board[end_row][end_col] = None  # Clear the end position

                if was_en_passant and captured_piece:
                    # If en passant, restore the captured pawn at its original square
                    captured_row = end_row + 1 if piece.color == "w" else end_row - 1
                    self.board.board[captured_row][
                        end_col
                    ] = captured_piece  # Restore the pawn

                else:
                    # Normal capture: restore the captured piece in its original position
                    if captured_piece:
                        self.board.board[end_row][end_col] = captured_piece

            if was_promotion:
                # Restore the pawn instead of the promoted piece
                self.board.board[start_row][start_col] = Pawn(
                    start_row, start_col, piece.color
                )

            # Update the piece's row and col
            piece.row = start_row
            piece.col = start_col

            # Update the king and rook moved flags
            if isinstance(piece, King) and king_moved:
                self.board.king_moved[piece.color] = king_moved[piece.color]
            if isinstance(piece, Rook) and rook_moved:
                self.board.rook_moved[
                    f"{piece.color}_{'kingside' if piece.col >= 4 else 'queenside'}"
                ] = rook_moved[
                    f"{piece.color}_{'kingside' if piece.col >= 4 else 'queenside'}"
                ]

            # Switch the turn back
            self.turn = "b" if self.turn == "w" else "w"

            # Add this move to the future moves stack
            self.future_moves.append(last_move)

    def advance_move(self):
        """ "
        Redoes a previously undone move by applying it to the board.
        Handles the restoration of captured pieces, en passant, and castling if necessary.
        Switches the turn back to the correct player after advancing the move.
        """
        if self.future_moves:
            next_move = self.future_moves.pop()

            # Apply the move (advance it)
            piece = next_move["piece"]
            start_row, start_col = next_move["start"]
            end_row, end_col = next_move["end"]
            captured_piece = next_move["captured"]
            was_en_passant = next_move.get("en_passant", False)
            was_castling = next_move.get("castling", None)
            was_promotion = next_move.get("promotion", False)
            king_moved = next_move.get("king_moved", None)
            rook_moved = next_move.get("rook_moved", None)

            # Move the piece to its new position
            self.board.board[end_row][end_col] = piece
            self.board.board[start_row][start_col] = None  # Clear the old position

            if was_en_passant:
                # Remove the captured pawn (which was not on end_row, but one row behind)
                captured_row = end_row + 1 if piece.color == "w" else end_row - 1
                self.board.board[captured_row][
                    end_col
                ] = None  # Remove en passant captured pawn

            # Handle castling
            elif was_castling:
                if was_castling == "kingside":
                    self.board.board[end_row][6] = piece  # Move the king
                    self.board.board[start_row][
                        start_col
                    ] = None  # Clear old king position

                    self.board.board[end_row][5] = self.board.board[end_row][
                        7
                    ]  # Move the rook
                    self.board.board[end_row][7] = None  # Clear old rook position
                    self.board.board[end_row][5].col = 5

                elif was_castling == "queenside":
                    self.board.board[end_row][2] = piece  # Move the king
                    self.board.board[start_row][
                        start_col
                    ] = None  # Clear old king position

                    self.board.board[end_row][3] = self.board.board[end_row][
                        0
                    ]  # Move the rook
                    self.board.board[end_row][0] = None  # Clear old rook position
                    self.board.board[end_row][3].col = 3

            # Handle promotion
            if was_promotion:
                self.board.board[end_row][end_col] = Queen(
                    end_row, end_col, piece.color
                )  # Promote to Queen
            if captured_piece:
                # If a piece was captured, restore it to the correct position
                self.board.board[start_row][start_col] = captured_piece

            # Update the piece's row and col
            piece.row = end_row
            piece.col = end_col

            # Update the king and rook moved flags
            if isinstance(piece, King):
                self.board.king_moved[piece.color] = king_moved[piece.color]
            if isinstance(piece, Rook):
                self.board.rook_moved[
                    f"{piece.color}_{'kingside' if piece.col >= 4 else 'queenside'}"
                ] = rook_moved[
                    f"{piece.color}_{'kingside' if piece.col >= 4 else 'queenside'}"
                ]

            # Switch the turn
            self.turn = "b" if self.turn == "w" else "w"

            # Add this move back to the move history
            self.move_history.append(next_move)

    def ask_promotion_choice(self, color):
        """
        Opens a promotion menu next to the game window, showing promotion choices without covering the board.
        Highlights a piece only when hovered.
        """
        choices = ["q", "r", "b", "n"]  # Possible promotions
        piece_classes = {"q": Queen, "r": Rook, "b": Bishop, "n": Knight}

        # Get piece images
        piece_images = {choice: PIECES[f"{color}{choice}"] for choice in choices}

        menu_y = HEIGHT // 2 - (SQUARE_SIZE // 2)  # Centered vertically
        menu_x = (WIDTH // 2) - (2 * SQUARE_SIZE)  # Centered horizontally

        # Create button rects
        button_rects = []
        for i, choice in enumerate(choices):
            rect = pygame.Rect(
                menu_x + i * SQUARE_SIZE, menu_y, SQUARE_SIZE, SQUARE_SIZE
            )
            button_rects.append((rect, choice))

        while True:

            mouse_pos = pygame.mouse.get_pos()
            hovered_choice = None

            for rect, choice in button_rects:
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(
                        self.screen, CLEAR_BLUE, rect, border_radius=10
                    )  # Highlight only when hovered
                    hovered_choice = choice

                else:
                    pygame.draw.rect(
                        self.screen, BLACK, rect, border_radius=10
                    )  # Default color

                self.screen.blit(piece_images[choice], (rect.x, rect.y))  # Draw pieces

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, choice in button_rects:
                        if rect.collidepoint(event.pos):
                            return piece_classes[choice](0, 0, color)

    def run(self, mode):
        """
        Main game loop.

        This method is the core loop of the chess game. It handles the main game flow,
        user input (keyboard and mouse events), and displays the game state (board, pieces, etc.).
        It updates the board, handles player moves, and checks for game end conditions like checkmate or stalemate.

        Args:
            mode (str): The mode of the game, either "help", "pvp", or "pvc". Determines the initial state of the game.
        """

        if mode == "help":
            self.display_help()

        self.move_history = []  # List to store move history
        self.future_moves = []  # List to store future moves (undone moves)

        show_valid_moves = False  # Flag to show valid moves or not
        dragging_piece = False  # Track if a piece is being dragged

        offset_x, offset_y = 0, 0  # Track the offset between mouse and piece position

        last_move_piece = None  # Track the last piece that was moved
        last_move_start = (-1, -1)  # Track the start position of the last move
        last_move_end = (-1, -1)  # Track the end position of the last move

        was_there_enemy = (
            False  # Flag to check if there was an enemy piece at the end position
        )

        while self.running:
            self.board.draw(self.screen)

            if self.selected_piece:
                current_selected_piece = self.selected_piece

                if show_valid_moves:
                    self.board.highlight_valid_moves(
                        self.screen,
                        self.selected_piece,
                        (last_move_piece, last_move_start, last_move_end),
                    )

                # Draw the selected piece at the mouse position if it's being dragged
                if dragging_piece:
                    temp_row, temp_col = (
                        self.selected_piece.row,
                        self.selected_piece.col,
                    )
                    self.board.board[temp_row][temp_col] = None  # Hide piece from board

                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    self.screen.blit(
                        self.selected_piece.image,
                        (mouse_x - offset_x, mouse_y - offset_y),
                    )

            self.board.highlight_last_move(
                self.screen, (last_move_start, last_move_end), was_there_enemy
            )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                    piece = self.board.board[row][col]

                    if piece and piece.color == self.turn:
                        self.selected_piece = piece
                        dragging_piece = True  # Start dragging
                        offset_x = x - col * SQUARE_SIZE
                        offset_y = y - row * SQUARE_SIZE

                elif event.type == pygame.MOUSEMOTION:
                    if dragging_piece and self.selected_piece:
                        # Keep updating piece position with mouse
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        self.screen.blit(
                            self.selected_piece.image,
                            (mouse_x - offset_x, mouse_y - offset_y),
                        )

                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging_piece:
                        x, y = event.pos
                        col, row = x // SQUARE_SIZE, y // SQUARE_SIZE

                        # Try to move the piece if it's a valid move
                        if self.selected_piece and (
                            row,
                            col,
                        ) in self.selected_piece.valid_moves(
                            self.board,
                            (last_move_piece, last_move_start, last_move_end),
                        ):

                            # If a valid move is made, clear the redo stack (future moves)
                            self.future_moves.clear()  # 🚀 This prevents advancing after a new move

                            was_there_enemy = False

                            # Store current move before updating last move
                            current_move_start = (
                                self.selected_piece.row,
                                self.selected_piece.col,
                            )
                            current_move_end = (row, col)

                            # Get the **previous** move from history (if available)
                            if len(self.move_history) > 0:
                                previous_move = self.move_history[
                                    -1
                                ]  # Last move in history
                                prev_piece = previous_move["piece"]
                                prev_start = previous_move["start"]
                                prev_end = previous_move["end"]
                            else:
                                prev_piece, prev_start, prev_end = None, (0, 0), (0, 0)

                            # Store the captured piece (if any)
                            if self.board.board[row][col]:
                                captured_piece = self.board.board[row][col]
                            elif self.board.is_en_passant(
                                current_selected_piece,
                                (
                                    current_selected_piece.row,
                                    current_selected_piece.col,
                                ),
                                (row, col),
                                (prev_piece, prev_start, prev_end),
                            ):
                                captured_piece = self.board.board[
                                    (
                                        row - 1
                                        if self.selected_piece.color == "b"
                                        else row + 1
                                    )
                                ][col]
                            else:
                                captured_piece = None

                            if captured_piece:
                                was_there_enemy = True

                            # ✅ Detect castling
                            castling_move = False
                            if isinstance(self.selected_piece, King):
                                castling_move = self.board.is_castle(
                                    self.selected_piece,
                                    current_move_start,
                                    current_move_end,
                                )

                            # Record the move in the history (store the moved piece and destination state)
                            self.move_history.append(
                                {
                                    "piece": self.selected_piece,
                                    "start": current_move_start,
                                    "end": current_move_end,
                                    "captured": captured_piece,
                                    "en_passant": self.board.is_en_passant(
                                        self.selected_piece,
                                        (
                                            current_selected_piece.row,
                                            current_selected_piece.col,
                                        ),
                                        (row, col),
                                        (prev_piece, prev_start, prev_end),
                                    ),
                                    "castling": castling_move,
                                    "king_moved": self.board.king_moved,
                                    "rook_moved": self.board.rook_moved,
                                    "promotion": False,
                                }
                            )

                            # Perform the move
                            self.board.move_piece(
                                self.selected_piece,
                                (self.selected_piece.row, self.selected_piece.col),
                                (row, col),
                                (prev_piece, prev_start, prev_end),
                                self,
                            )

                            # Update piece's row and col to reflect its new position
                            last_move_piece = self.selected_piece
                            last_move_start = current_move_start
                            last_move_end = current_move_end

                            self.selected_piece.row = row
                            self.selected_piece.col = col

                            self.board.board[row][col] = self.selected_piece
                            self.turn = "b" if self.turn == "w" else "w"

                            if self.board.is_checkmate(self.turn):
                                self.board.draw(self.screen)
                                self.running = False
                                self.endgame("Checkmate", self.turn)
                            elif (
                                self.board.is_stalemate(WHITE) and self.turn == "w"
                            ) or (self.board.is_stalemate(BLACK) and self.turn == "b"):
                                self.board.draw(self.screen)
                                self.running = False
                                self.endgame("Draw", self.turn)

                        elif self.selected_piece and (
                            row,
                            col,
                        ) not in self.selected_piece.valid_moves(
                            self.board,
                            (last_move_piece, last_move_start, last_move_end),
                        ):
                            # If the move is not valid, put the piece back in its original position
                            self.board.board[temp_row][temp_col] = self.selected_piece

                        # Stop dragging and restore the board
                        dragging_piece = False
                        self.selected_piece = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        self.__init__()
                        self.run(self.game_mode)
                    elif event.key == pygame.K_z:
                        message = (
                            f'{"White" if self.turn == "w" else "Black"} Surrender ! '
                        )
                        self.running = False
                        self.endgame(message, self.turn)
                    elif event.key == pygame.K_s:
                        show_valid_moves = not show_valid_moves
                    elif event.key == pygame.K_b:
                        self.undo_move()
                    elif event.key == pygame.K_y:
                        self.advance_move()

            pygame.display.flip()

    def endgame(self, message, color):
        """
        Display endgame message.

        This method displays the final message on the screen after the game ends. It shows either a draw or a win message
        depending on the outcome of the game. Additionally, it provides instructions to the player on how to exit the game
        or restart it.

        Args:
            message (str): The message to display at the end of the game. Can be "Draw" or "Checkmate" or "Surrender".
            color (str): The color of the player who has lost the game. ("w" for white, "b" for black).
        """
        font = pygame.font.Font(None, 48)

        if message == "Draw":
            game_state = font.render("It's a draw!", True, (0, 0, 0))
        else:
            game_state = font.render(
                f"{message} : {'White wins' if self.turn == 'b' else 'Black wins'}",
                True,
                (0, 0, 0),
            )
        self.screen.blit(
            game_state, (WIDTH // 2 - game_state.get_width() // 2, HEIGHT // 2 - 150)
        )

        text = font.render(
            "Press Backspace to exit or Enter to replay.", True, (0, 0, 0)
        )
        self.screen.blit(text, (WIDTH // 2 - 350, HEIGHT // 2 + 100))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_RETURN:
                        self.__init__()
                        self.run(self.game_mode)
