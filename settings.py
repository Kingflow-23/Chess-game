import pygame

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 900, 900
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
CLEAR_BLUE = (135, 206, 235)
CLEAR_GREEN = (144, 238, 144)

# Load and scale pieces
PIECES = {
    "wp": pygame.image.load("pieces/white_pawn.png"),
    "bp": pygame.image.load("pieces/black_pawn.png"),
    "wr": pygame.image.load("pieces/white_rook.png"),
    "br": pygame.image.load("pieces/black_rook.png"),
    "wn": pygame.image.load("pieces/white_knight.png"),
    "bn": pygame.image.load("pieces/black_knight.png"),
    "wb": pygame.image.load("pieces/white_bishop.png"),
    "bb": pygame.image.load("pieces/black_bishop.png"),
    "wq": pygame.image.load("pieces/white_queen.png"),
    "bq": pygame.image.load("pieces/black_queen.png"),
    "wk": pygame.image.load("pieces/white_king.png"),
    "bk": pygame.image.load("pieces/black_king.png"),
}

TITLE_BG = pygame.image.load("background/title.jpg")

for key in PIECES:
    PIECES[key] = pygame.transform.scale(PIECES[key], (SQUARE_SIZE, SQUARE_SIZE))
