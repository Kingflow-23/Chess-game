# Chess Game - Python & Pygame

This is a simple chess game implemented using Python and Pygame. It includes various features such as drag-and-drop piece movement, check/checkmate detection, en passant, castling, and an undo/redo functionality.

## Features:
- **PvP Mode**: Play against a friend on the same computer.
- **Drag-and-Drop**: Move pieces by dragging them.
- **Undo/Redo**: Undo moves with the `B` key, redo with the `Y` key.
- **En Passant**: Support for the special pawn capture.
- **Valid Move Highlighting**: Highlight possible moves when a piece is selected if enabled by pressing the `S` key.
- **Check/Checkmate Detection**: Automatically detects checkmate and stalemate.

## Requirements:

- Python 3.x. I used 3.10.11
- Pygame library

You can install Pygame by running the following command:

```bash
pip install pygame
```

## Folder Structure:
Chess/

├── background/             # Background for the ui

│   └──      (title, etc ...)

├── pieces/             # Images for chess pieces

│   └──      (king, queen, bishop, etc.)

├── board.py           # Handles the chessboard

├── computer_player.py # Handles the computer player

├── main.py      # Main game logic and UI

├── pieces.py          # Contains piece classes like Pawn, Knight, etc.

├── game.py          # Handles game workflow and rules

├── settings.py     # Contains game settings

└── README.md          # This file

## How to Play:

1. **Start the Game**: Execute `main.py` to start playing.

    - First, You'll have to choose the opponent. You can choose between a friend or the computer.
    - If you choose a friend, you can play against each other on the same computer.
    - If you choose the computer, you'll play against the computer. The computer is using a minimax algorithm to search for the best move.
   - When you run the game, the chessboard will appear on the screen with all the pieces in their initial positions.

2. **Move Pieces**:
   - To move a piece, **click** on it, and **drag** it to a valid square on the board.
   - The possible moves for each piece will be highlighted in **green**.

3. **Undo a Move**:
   - Press the **B** key to undo your last move.
   - This will revert the board to the previous state, allowing you to correct mistakes or reconsider your strategy.

4. **Redo a Move**:
   - Press the **Y** key to redo the last move you undid.
   - This allows you to restore a move that was previously undone.

5. **Castling**:
   - Castling is supported for both players, but only if the king and rook have not moved before.
   - Castling is a special move that lets the king move two squares towards a rook, and the rook then moves to the other side of the king.

6. **En Passant**:
   - **En passant** is a special pawn capture that can occur when a pawn moves two squares forward from its starting position, and lands beside an opponent's pawn. 
   - In this case, the opponent's pawn may capture the first pawn as if it had moved only one square forward. 
   - To perform en passant, click the opponent's pawn and drag your pawn diagonally over the space where the opponent’s pawn just moved, capturing it.

7. **Promote a Pawn**:
   - When a pawn reaches the opposite end of the board, it can be promoted to a **Queen**, **Rook**, **Bishop**, or **Knight**.
   - A prompt will appear, and you can choose which piece to promote to.

8. **Endgame**:
   - **Checkmate**: The game ends if a player's king is in **check** and cannot escape capture.
   - **Stalemate**: If the current player has no legal move and their king is not in check, it’s a stalemate, and the game ends in a draw.
   - **Resignation**: If you want to give up during the game, press **Z** to surrender. The opponent will win, and a message will be displayed announcing the victory.

9. **Game Restart**:
   - If you want to restart the game, press the **Enter** key.
   - The board will reset to its initial state, and the game will continue from the beginning.

## Controls:

- **Mouse**:
   - **Left-click**: Select a piece to move.
   - **Drag**: Move the selected piece to a valid destination.
   
- **Keyboard**:
   - **B Key**: Undo the last move.
   - **Y Key**: Redo the last undone move.
   - **Z Key**: Surrender the game. The opponent wins.
   - **Enter Key**: Restart the game.
   - **Escape Key**: Quit the game.

## Example of Playing a Game:

1. Start the game by running `python main.py`. Choose the game mode and your piece color.
2. White always goes first. Select a white piece by clicking on it, then drag it to a valid square. For example, move the white pawn from **e2 to e4**.
3. Black's turn – select a black piece and move it. If you accidentally make a bad move, press **B** to undo it. If you change your mind again, press **Y** to redo the move.
5. Continue playing until one player wins by **checkmate**, the game ends in a **stalemate**, or one player **resigns**.

## Example of Moves:

- **Pawn**: Move one square forward, two squares on the first move, or diagonally to capture an enemy piece.
- **Rook**: Move vertically or horizontally any number of squares.
- **Knight**: Move in an "L" shape: two squares in one direction and then one square perpendicular, or vice versa.
- **Bishop**: Move diagonally any number of squares.
- **Queen**: Combine the movements of the rook and bishop (vertically, horizontally, or diagonally).
- **King**: Move one square in any direction. Castling is a special move to protect the king.

## Example of Castling:

- White's king is on **e1**, and the white rook is on **h1** (or **a1**).
- White can castle by moving the king two squares towards the rook (e.g., from **e1 to g1**), and the rook will jump to the square the king skipped (e.g., from **h1 to f1**).
- **Conditions**: The king and the rook must not have moved previously, and there should be no pieces between them.

## Troubleshooting:

- **Game not starting?** Make sure you have installed the `pygame` library.
- **Piece movement issue?** Ensure you are dragging the pieces to valid squares. If you misplaced a piece, press **B** to undo the move.

Have fun playing chess!