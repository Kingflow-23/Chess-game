# Chess Game - Python & Pygame

This is a simple chess game implemented using Python and Pygame. It features drag-and-drop piece movement, check/checkmate detection, en passant, castling, and an undo/redo functionality. Play against a friend (PvP) or challenge the computer (PvC), which uses a Minimax algorithm with Alpha-Beta pruning for its moves.

## Features:

- **PvP Mode:** Play against a friend on the same computer.
- **PvC Mode:** Play against an AI that uses the Minimax algorithm with Alpha-Beta pruning and transposition table caching.
- **Drag-and-Drop Movement:** Select and move pieces by dragging them.
- **Undo/Redo:** Undo your moves with the `B` key and redo undone moves with the `Y` key.
- **En Passant:** Special pawn capture is supported.
- **Castling:** Both kingside and queenside castling are implemented (with proper conditions).
- **Valid Move Highlighting:** When enabled (by pressing the `S` key), possible moves for a selected piece are highlighted.
- **Check/Checkmate/Stalemate Detection:** The game automatically detects check, checkmate, and stalemate.
- **Pawn Promotion:** When a pawn reaches the opposite end, a prompt allows promotion to a Queen, Rook, Bishop, or Knight (with auto-promotion for AI moves).

## Requirements:

- Python 3.x. I used 3.10.11

I recommend you to use a virtual environment.

```bash 
python -m venv .
source venv/bin/activate # On Linux/Mac
venv\Scripts\activate # On Windows
``` 

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Folder Structure:

```
📦 Chess-Game
├── 📂 background/               # Contains background-related assets
│
├── 📂 pieces/                   # Contains individual chess piece assets or logic
│
├── 📂 src/                      # Main source code directory
│   ├── board.py                 # Handles board representation and game logic
│   ├── computer_player.py       # AI logic using Minimax and Alpha-Beta pruning
│   ├── game.py                  # Game management (turns, win conditions, etc.)
│   ├── pieces.py                # Defines chess piece behaviors and movements
│   └── settings.py              # Configuration settings for the game
│
├── main.py                      # Entry point to start the game
├── .gitignore                   # Specifies files to ignore in version control
├── README.md                    # Project documentation
└── requirements.txt             # Lists dependencies for installation
```

## How to Play:

1. **Start the Game**: Execute `main.py` to start playing.

   ```bash 
   python main.py
   ```

    - First, You'll have to choose the opponent. You can choose between a friend or the computer.
    - If you choose a friend, you can play against each other on the same computer.
    - If you choose the computer, you'll play against the computer. You will be able to choose before the color you'll play as. The computer is using a minimax algorithm to search for the best move.
   - When you run the game, the chessboard will appear on the screen with all the pieces in their initial positions.

2. **Move Pieces**:
   - To move a piece, **click** on it, and **drag** it to a valid square on the board.
   - The possible moves for each piece will be highlighted in **green**, **red** for capture moves.

3. **Undo a Move**:
   - Press the **B** key to undo your last move. It's a simple way to try different moves without losing your progress but be careful when using it vs computer cause it might cause bugs. My advice i can give to you is to wait for your turn and then to click 2 times on "B".
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