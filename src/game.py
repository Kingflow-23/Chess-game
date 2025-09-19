import sys
import random
import pygame
from typing import Tuple, Optional, Any

from settings import *

from src.pieces import *
from src.board import Board
from src.computer_player import ComputerPlayer


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
        self.flipped = False
        self.running = True
        self.computer_player = None

        self.position_history = []
        self.position_counts = {}
        self.halfmove_clock = 0

        self.setup_phase()  # Call setup_phase to select game mode

    def setup_phase(self):
        """
        Displays the initial menu to choose the game mode.
        Options include Player vs Player, Player vs Computer, Computer Vs Computer and Help.
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
        cvc_text = font.render("3. Computer vs Computer", True, (255, 255, 255))
        help_text = font.render("4. Help", True, (255, 255, 255))

        # Define button areas (rectangles)
        pvp_rect = pygame.Rect(
            WIDTH // 2 - 180, HEIGHT // 2.7, pvp_text.get_width(), pvp_text.get_height()
        )
        pvc_rect = pygame.Rect(
            WIDTH // 2 - 180, HEIGHT // 2.3, pvc_text.get_width(), pvc_text.get_height()
        )
        cvc_rect = pygame.Rect(
            WIDTH // 2 - 180, HEIGHT // 2, cvc_text.get_width(), cvc_text.get_height()
        )
        help_rect = pygame.Rect(
            WIDTH // 2 - 180,
            HEIGHT // 1.78,
            help_text.get_width(),
            help_text.get_height(),
        )

        running = True
        while running:
            self.screen.blit(background, (0, 0))
            self.screen.blit(title_text, (WIDTH // 2 - 150, HEIGHT // 6 - 50))
            self.screen.blit(author_text, (WIDTH // 2 - 190, HEIGHT // 4 - 50))
            self.screen.blit(pvp_text, (WIDTH // 2 - 180, HEIGHT // 2.7))
            self.screen.blit(pvc_text, (WIDTH // 2 - 180, HEIGHT // 2.3))
            self.screen.blit(cvc_text, (WIDTH // 2 - 180, HEIGHT // 2))
            self.screen.blit(help_text, (WIDTH // 2 - 180, HEIGHT // 1.78))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

                    elif event.key == pygame.K_BACKSPACE:
                        # Go back to the main menu
                        self.setup_phase()
                        # Restart the run loop with the newly chosen game mode
                        self.run(self.game_mode)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.game_mode = "pvp"
                        running = False
                    if event.key == pygame.K_2:
                        self.game_mode = "pvc"
                        running = False
                    if event.key == pygame.K_3:
                        self.game_mode = "cvc"
                        running = False
                    if event.key == pygame.K_4:
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
                        elif cvc_rect.collidepoint(mouse_pos):
                            self.game_mode = "cvc"
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

                    if cvc_rect.collidepoint(mouse_pos):
                        cvc_text = font.render(
                            "3. Computer vs Computer", True, (255, 255, 0)
                        )
                    else:
                        cvc_text = font.render(
                            "3. Computer vs Computer", True, (255, 255, 255)
                        )

                    if help_rect.collidepoint(mouse_pos):
                        help_text = font.render("4. Help", True, (255, 255, 0))
                    else:
                        help_text = font.render("4. Help", True, (255, 255, 255))

    def choose_color_menu(self, screen) -> Tuple[str, str]:
        """
        Displays an in-game menu for the player to choose their color or choose a random option.

        Args:
            screen (pygame.Surface): The game display surface.

        Returns:
            Tuple[str, str]: A tuple containing (player_color, computer_color)
                            where each is either "w" or "b".
        """
        background = pygame.transform.scale(TITLE_BG, (WIDTH, HEIGHT))

        font = pygame.font.Font(None, 60)
        white_button = pygame.Rect(100, 125, 290, 100)
        black_button = pygame.Rect(500, 125, 290, 100)
        random_button = pygame.Rect(300, 350, 275, 100)

        running = True
        player_color = None

        while running:
            screen.blit(background, (0, 0))

            mouse_pos = pygame.mouse.get_pos()

            # --- White button ---
            if white_button.collidepoint(mouse_pos):
                white_text = font.render(
                    "Play as White", True, (255, 255, 0)
                )  # Yellow hover
            else:
                white_text = font.render(
                    "Play as White", True, (0, 0, 0)
                )  # Black default

            # --- Black button ---
            if black_button.collidepoint(mouse_pos):
                black_text = font.render("Play as Black", True, (255, 255, 0))
            else:
                black_text = font.render("Play as Black", True, (0, 0, 0))

            # --- Random button ---
            if random_button.collidepoint(mouse_pos):
                random_text = font.render("Random", True, (255, 255, 0))
            else:
                random_text = font.render("Random", True, (0, 0, 0))

            # Draw buttons
            pygame.draw.rect(screen, (200, 200, 200), white_button)
            pygame.draw.rect(screen, (200, 200, 200), black_button)
            pygame.draw.rect(screen, (200, 200, 200), random_button)

            screen.blit(white_text, (white_button.x + 10, white_button.y + 30))
            screen.blit(black_text, (black_button.x + 10, black_button.y + 30))
            screen.blit(random_text, (random_button.x + 50, random_button.y + 30))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

                    elif event.key == pygame.K_BACKSPACE:
                        # Go back to the main menu
                        self.setup_phase()
                        # Restart the run loop with the newly chosen game mode
                        self.run(self.game_mode)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if white_button.collidepoint(pos):
                        player_color = "w"
                        running = False
                    elif black_button.collidepoint(pos):
                        player_color = "b"
                        running = False
                    elif random_button.collidepoint(pos):
                        player_color = random.choice(["w", "b"])
                        running = False

        # Computer gets the opposite color.
        computer_color = "w" if player_color == "b" else "b"
        return player_color, computer_color

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
            "Press 'C' to undo a move.",
            "Press 'V' to redo an undone move.",
            "Press 'Backspace' to go to the menu.",
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
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()  # Exit the game if Escape is pressed

                    elif event.key == pygame.K_BACKSPACE:
                        # Go back to the main menu
                        self.setup_phase()
                        # Restart the run loop with the newly chosen game mode
                        self.run(self.game_mode)

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

                    self.board.king_moved[piece.color] = False
                    self.board.rook_moved[f"{piece.color}_kingside"] = False

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

                    self.board.king_moved[piece.color] = False
                    self.board.rook_moved[f"{piece.color}_queenside"] = False

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
                if piece.color == "w":
                    self.board.white_king = (start_row, start_col)
                else:
                    self.board.black_king = (start_row, start_col)

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
                self.board.board[end_row][end_col] = self.ask_promotion_choice(
                    piece, (end_row, end_col)
                )

            # Update the piece's row and col
            piece.row = end_row
            piece.col = end_col

            # Update the king and rook moved flags
            if isinstance(piece, King):
                self.board.king_moved[piece.color] = king_moved[piece.color]
                if piece.color == "w":
                    self.board.white_king = (end_row, end_col)
                else:
                    self.board.black_king = (end_row, end_col)

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

    def ask_promotion_choice(self, pawn: Pawn, end_move: Tuple[int, int]) -> Piece:
        """
        Opens a promotion menu next to the game window, showing promotion choices without covering the board.
        Highlights a piece only when hovered.
        """
        choices = ["q", "r", "b", "n"]  # Possible promotions
        piece_classes = {"q": Queen, "r": Rook, "b": Bishop, "n": Knight}

        # Get piece images
        piece_images = {choice: PIECES[f"{pawn.color}{choice}"] for choice in choices}

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
                            return piece_classes[choice](
                                end_move[0], end_move[1], pawn.color
                            )

    def initialize_game_state(self) -> None:
        """
        Initializes game state variables to their default values.

        This includes clearing move and future move histories, resetting UI flags,
        and setting initial last move values.
        """
        self.move_history: list = []
        self.future_moves: list = []
        self.show_valid_moves: bool = True
        self.dragging_piece: bool = False
        self.offset_x: int = 0
        self.offset_y: int = 0
        self.last_move_piece = None
        self.last_move_start: Tuple[int, int] = (-1, -1)
        self.last_move_end: Tuple[int, int] = (-1, -1)
        self.was_there_enemy: bool = False
        self.ai_moved: bool = False

    def draw_board_and_pieces(self) -> None:
        """
        Renders the board and all pieces onto the screen.

        First, it draws the board, then highlights valid moves if a piece is selected.
        If a piece is being dragged, it draws the piece at the current mouse position.
        Finally, it highlights the last move made.
        """
        self.board.draw(self.screen, self.flipped)

        if self.selected_piece:
            if self.show_valid_moves:
                self.board.highlight_valid_moves(
                    self.screen,
                    self.selected_piece,
                    (self.last_move_piece, self.last_move_start, self.last_move_end),
                    flipped=self.flipped,
                )

            if self.dragging_piece:
                temp_row, temp_col = self.selected_piece.row, self.selected_piece.col

                # Convert to flipped screen coords
                screen_x, screen_y = self.board.to_screen_coords(
                    temp_row, temp_col, self.flipped
                )

                # ✅ Use flipped row/col for correct square color
                square_color = self.board.get_square_color(
                    temp_row, temp_col, self.flipped
                )

                pygame.draw.rect(
                    self.screen,
                    square_color,
                    (screen_x, screen_y, SQUARE_SIZE, SQUARE_SIZE),
                )

                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.screen.blit(
                    self.selected_piece.image,
                    (mouse_x - self.offset_x, mouse_y - self.offset_y),
                )

        self.board.highlight_last_move(
            self.screen,
            (self.last_move_start, self.last_move_end),
            self.was_there_enemy,
            flipped=self.flipped,
        )

    def handle_events(self) -> None:
        """
        Processes all user input events (mouse, keyboard, and quit events).

        Delegates mouse down, motion, up, and keypress events to their respective handlers.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event)

    def handle_mouse_down(self, event: pygame.event.Event) -> None:
        """
        Handles mouse button press events.

        Determines the board square where the click occurred and, if a piece of the current
        turn's color is present, starts dragging that piece.

        Args:
            event (pygame.event.Event): The mouse button down event.
        """
        # If it's AI's turn, ignore clicks
        if (
            self.game_mode == "pvc"
            and self.computer_player
            and self.turn == self.computer_player.color
        ):
            return
        if self.game_mode == "cvc":  # In CVC no human input at all
            return

        x, y = event.pos
        row, col = self.board.from_screen_coords(x, y, self.flipped)

        piece = self.board.board[row][col]

        if piece and piece.color == self.turn:
            self.selected_piece = piece
            self.dragging_piece = True

            # ✅ Use to_screen_coords so offsets are correct when flipped
            square_x, square_y = self.board.to_screen_coords(row, col, self.flipped)
            self.offset_x = x - square_x
            self.offset_y = y - square_y

    def handle_mouse_motion(self) -> None:
        """Handles mouse movement while dragging a piece."""
        if self.dragging_piece and self.selected_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.screen.blit(
                self.selected_piece.image,
                (mouse_x - self.offset_x, mouse_y - self.offset_y),
            )

    def handle_mouse_up(self, event: pygame.event.Event) -> None:
        """
        Handles mouse button release events (dropping a piece).

        If the drop location is a valid move for the selected piece, the move is performed;
        otherwise, the piece is returned to its original square.

        Args:
            event (pygame.event.Event): The mouse button up event.
        """
        if not self.dragging_piece:
            return

        x, y = event.pos
        row, col = self.board.from_screen_coords(x, y, self.flipped)

        if self.selected_piece and (row, col) in self.selected_piece.valid_moves(
            self.board, (self.last_move_piece, self.last_move_start, self.last_move_end)
        ):
            self.perform_move(row, col)

        else:
            temp_row, temp_col = self.selected_piece.row, self.selected_piece.col
            self.board.board[temp_row][temp_col] = self.selected_piece

        self.dragging_piece = False
        self.selected_piece = None

    def get_last_move(self) -> Tuple[Optional[Any], Tuple[int, int], Tuple[int, int]]:
        """
        Retrieves details of the most recent move from the move history.

        Returns:
            A tuple containing:
                - The piece that made the last move (or None if no moves have been made),
                - The starting position (row, col) of the last move,
                - The ending position (row, col) of the last move.
        """
        if len(self.move_history) > 0:
            last_move = self.move_history[-1]
            return last_move["piece"], last_move["start"], last_move["end"]
        return None, (0, 0), (0, 0)

    def get_captured_piece(
        self,
        piece: Any,
        row: int,
        col: int,
        prev_piece: Any,
        prev_start: Tuple[int, int],
        prev_end: Tuple[int, int],
    ) -> Optional[Any]:
        """
        Determines if a capture occurred during a move.

        This method checks:
          1. Normal capture: If the destination square (row, col) is occupied.
          2. En passant: If the move qualifies as an en passant capture.

        Args:
            piece: The piece being moved.
            row (int): The destination row.
            col (int): The destination column.
            prev_piece: The piece involved in the previous move.
            prev_start (Tuple[int, int]): The starting position of the previous move.
            prev_end (Tuple[int, int]): The ending position of the previous move.

        Returns:
            The captured piece if one was captured; otherwise, None.
        """
        if self.board.board[row][col]:
            return self.board.board[row][col]
        if self.board.is_en_passant(
            piece,
            (piece.row, piece.col),
            (row, col),
            (prev_piece, prev_start, prev_end),
        ):
            return self.board.board[row - 1 if piece.color == "b" else row + 1][col]
        return None

    def get_position_key(self) -> str:
        """
        Generate a key that uniquely identifies the current position for repetition checks.
        Includes: piece placement, turn, castling rights, and en passant (if valid).
        """
        # Piece placement
        board_str = ""
        for row in self.board.board:
            for piece in row:
                if piece:
                    board_str += piece.color + piece.piece_type
                else:
                    board_str += "--"

        # Whose turn
        turn_str = self.turn

        # Castling rights
        castling_str = "".join([k for k, v in self.board.rook_moved.items() if not v])
        if not castling_str:
            castling_str = "-"

        # En passant
        en_passant_str = "-"
        if self.move_history:
            last_move = self.move_history[-1]
            if last_move["piece"].piece_type == "p":
                start_row, start_col = last_move["start"]
                end_row, end_col = last_move["end"]

                # Double pawn move
                if abs(start_row - end_row) == 2:
                    # Check if an enemy pawn can actually capture
                    ep_row = (start_row + end_row) // 2
                    ep_col = start_col
                    for dc in [-1, 1]:
                        adj_col = ep_col + dc
                        if 0 <= adj_col < 8:
                            adj_piece = self.board.board[ep_row][adj_col]
                            if (
                                adj_piece
                                and adj_piece.color != last_move["piece"].color
                                and adj_piece.piece_type == "p"
                            ):
                                en_passant_str = f"{ep_row}{ep_col}"
                                break

        return f"{board_str}_{turn_str}_{castling_str}_{en_passant_str}"

    def check_game_status(self) -> None:
        """
        Checks for game-ending conditions (checkmate or stalemate).

        If either condition is met, the board is redrawn, the game loop is terminated,
        and the endgame message is displayed.
        """
        if self.board.is_checkmate(self.turn):
            self.board.draw(self.screen, self.flipped)
            self.running = False
            self.endgame("Checkmate", self.turn)

        elif self.board.is_stalemate(self.turn):
            self.board.draw(self.screen, self.flipped)
            self.running = False
            self.endgame("Draw", self.turn)

        elif self.check_threefold_repetition():
            self.board.draw(self.screen, self.flipped)
            self.running = False
            self.endgame("Draw by repetition", self.turn)

        # (optional) add 50-move rule:
        elif self.fifty_move_rule():
            self.board.draw(self.screen, self.flipped)
            self.running = False
            self.endgame("Draw by 50-move rule", self.turn)

    def handle_key_press(self, event: pygame.event.Event) -> None:
        """
        Processes keypress events and executes corresponding game actions.

        Supported keys:
          - Escape: Exit the game.
          - Backspace: Go back to the game menu.
          - Return: Restart the game.
          - Z: Surrender.
          - S: Toggle showing valid moves.
          - C: Undo the last move.
          - V: Redo the previously undone move.

        Args:
            event (pygame.event.Event): The keypress event.
        """
        if event.key == pygame.K_ESCAPE:
            # Quit the whole game
            pygame.quit()
            sys.exit()

        elif event.key == pygame.K_BACKSPACE:
            # Go back to the main menu
            self.setup_phase()
            # Restart the run loop with the newly chosen game mode
            self.run(self.game_mode)

        elif event.key == pygame.K_RETURN:
            self.__init__()
            self.run(self.game_mode)
        elif event.key == pygame.K_z:
            message = f'{"White" if self.turn == "w" else "Black"} Surrender!'
            self.running = False
            self.endgame(message, self.turn)
        elif event.key == pygame.K_s:
            self.show_valid_moves = not self.show_valid_moves
        elif event.key == pygame.K_c:
            self.undo_move()
        elif event.key == pygame.K_v:
            self.advance_move()

    def perform_move(self, row: int, col: int) -> None:
        """
        Executes a move for the selected piece and updates the game state.

        This includes storing the move in history (with details for undo/redo), moving the piece,
        handling special moves (castling, en passant, promotion), and switching turns.

        Args:
            row (int): The destination row.
            col (int): The destination column.
        """
        self.future_moves.clear()

        start_pos = (self.selected_piece.row, self.selected_piece.col)
        self.was_there_enemy = self.board.board[row][col] is not None
        prev_piece, prev_start, prev_end = self.get_last_move()

        captured_piece = self.get_captured_piece(
            self.selected_piece, row, col, prev_piece, prev_start, prev_end
        )

        castling_move = isinstance(self.selected_piece, King) and self.board.is_castle(
            self.selected_piece,
            (self.selected_piece.row, self.selected_piece.col),
            (row, col),
        )

        promotion_move = isinstance(self.selected_piece, Pawn) and (
            (self.selected_piece.color == "w" and row == 0)
            or (self.selected_piece.color == "b" and row == 7)
        )

        king_moved = self.board.king_moved.copy()
        rook_moved = self.board.rook_moved.copy()

        self.move_history.append(
            {
                "piece": self.selected_piece,
                "start": start_pos,
                "end": (row, col),
                "captured": captured_piece,
                "en_passant": self.board.is_en_passant(
                    self.selected_piece,
                    (self.selected_piece.row, self.selected_piece.col),
                    (row, col),
                    (prev_piece, prev_start, prev_end),
                ),
                "castling": castling_move,
                "king_moved": king_moved,
                "rook_moved": rook_moved,
                "promotion": promotion_move,
            }
        )

        self.board.move_piece(
            self.selected_piece,
            start_pos,
            (row, col),
            (prev_piece, prev_start, prev_end),
            self,
        )

        self.last_move_piece = self.selected_piece
        self.last_move_start = start_pos
        self.last_move_end = (row, col)

        self.selected_piece.row = row
        self.selected_piece.col = col
        self.turn = "b" if self.turn == "w" else "w"

        pos_key = self.get_position_key()
        self.position_history.append(pos_key)
        self.position_counts[pos_key] = self.position_counts.get(pos_key, 0) + 1

        if isinstance(self.selected_piece, Pawn) or self.was_there_enemy:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.board.draw(self.screen, self.flipped)
        self.board.highlight_last_move(
            self.screen,
            (self.last_move_start, self.last_move_end),
            self.was_there_enemy,
            flipped=self.flipped,
        )

        self.check_game_status()

    def computer_move(self) -> None:
        """
        Executes the computer's move using the Minimax algorithm.

        Retrieves the best move for the AI, updates the board and move history, and
        switches the turn back to the human player.
        """
        prev_piece, prev_start, prev_end = self.get_last_move()

        if self.computer_player and self.turn == self.computer_player.color:
            if self.game_mode == "pvc" and self.ai_moved:
                return  # Prevent AI from moving multiple times in a row in PvC mode

            move = self.computer_player.get_best_move(self.board)
            if move:
                start_pos, end_pos = move
                row, col = end_pos
                piece = self.board.board[start_pos[0]][start_pos[1]]

                # Store the AI's last move for highlighting
                self.last_move_start = start_pos
                self.last_move_end = end_pos
                self.was_there_enemy = (
                    self.board.board[end_pos[0]][end_pos[1]] is not None
                )  # Check if capture happened

                captured_piece = self.get_captured_piece(
                    piece, row, col, prev_piece, prev_start, prev_end
                )

                castling_move = isinstance(piece, King) and self.board.is_castle(
                    piece,
                    (piece.row, piece.col),
                    (row, col),
                )

                promotion_move = isinstance(piece, Pawn) and (
                    (piece.color == "w" and row == 0)
                    or (piece.color == "b" and row == 7)
                )

                king_moved = self.board.king_moved.copy()
                rook_moved = self.board.rook_moved.copy()

                self.move_history.append(
                    {
                        "piece": piece,
                        "start": start_pos,
                        "end": (row, col),
                        "captured": captured_piece,
                        "en_passant": self.board.is_en_passant(
                            piece,
                            (piece.row, piece.col),
                            (row, col),
                            (prev_piece, prev_start, prev_end),
                        ),
                        "castling": castling_move,
                        "king_moved": king_moved,
                        "rook_moved": rook_moved,
                        "promotion": promotion_move,
                    }
                )

                self.board.move_piece(
                    piece, start_pos, end_pos, (prev_piece, prev_start, prev_end)
                )

                # Switch the turn after the move
                self.turn = "b" if self.turn == "w" else "w"

                # In CVC Mode: Allow AI to continue playing without restriction
                if self.game_mode == "cvc":
                    self.computer_player = (
                        self.computer_white if self.turn == "w" else self.computer_black
                    )
                else:
                    # In PvC Mode: Prevent AI from moving twice in a row
                    self.ai_moved = True

                # Save new position for repetition check
                pos_key = self.get_position_key()
                self.position_history.append(pos_key)
                self.position_counts[pos_key] = self.position_counts.get(pos_key, 0) + 1

                if isinstance(self.selected_piece, Pawn) or self.was_there_enemy:
                    self.halfmove_clock = 0
                else:
                    self.halfmove_clock += 1

                self.check_game_status()

    def run(self, mode: str) -> None:
        """
        Runs the main game loop.

        This function manages:
        - The game setup and initial mode selection.
        - The continuous rendering of the board.
        - Handling user inputs and AI moves.
        - Running AI vs AI when in 'cvc' mode.

        Args:
            mode (str): The game mode ('help', 'pvp', 'pvc', or 'cvc').
        """

        self.game_mode = mode

        if self.game_mode == "pvc":
            player_color, computer_color = self.choose_color_menu(self.screen)
            self.player_color = player_color
            self.computer_player = ComputerPlayer(computer_color)

            # Flip board if player is black
            self.flipped = True if player_color == "b" else False

        elif mode == "cvc":
            self.computer_white = ComputerPlayer("w")
            self.computer_black = ComputerPlayer("b")
            self.computer_player = self.computer_white  # Start with white

        self.initialize_game_state()

        while self.running:

            if self.game_mode == "help":
                self.display_help()

            self.draw_board_and_pieces()

            if self.game_mode == "pvc":
                if self.computer_player and self.turn == self.computer_player.color:
                    if not self.ai_moved:
                        self.computer_move()
                else:
                    self.ai_moved = False

            elif self.game_mode == "cvc":
                # Both AI players take turns automatically
                pygame.time.delay(500)  # Small delay for visualization
                self.computer_move()

            self.handle_events()
            pygame.display.flip()

    def check_threefold_repetition(self) -> bool:
        """
        Checks if the current position (with castling and en passant rights)
        has appeared at least 3 times.
        """
        current_key = self.get_position_key()
        return self.position_counts.get(current_key, 0) >= 3

    def fifty_move_rule(self) -> bool:
        """
        Returns True if 50-move rule applies (no pawn move or capture in last 50 moves).
        """
        return self.halfmove_clock >= 100  # 100 half-moves = 50 moves

    def endgame(self, message: str, color: str) -> None:
        """
        Displays the endgame screen with a message and instructions for exit or replay.

        Args:
            message (str): The outcome message ("Draw", "Checkmate", or "Surrender").
            color (str): The color of the player who lost ("w" for white, "b" for black).
        """
        font = pygame.font.Font(None, 48)

        if message == "Draw":
            game_state = font.render("It's a draw!", True, (0, 0, 0))

        elif message == "Draw by repetition":
            game_state = font.render("It's a draw by repetition!", True, (0, 0, 0))

        elif message == "Draw by 50-move rule":
            game_state = font.render("It's a draw by 50-move rule!", True, (0, 0, 0))

        else:
            game_state = font.render(
                f"{message} : {'White wins' if color == 'b' else 'Black wins'}",
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
