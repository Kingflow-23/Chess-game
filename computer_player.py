import random

class ComputerPlayer:
    

    def __init__(self, color):
        """
        Initialize the computer player.
        
        Parameters:
            color: The player's color ("w" or "b").
        """

        self.color = color
        self.opponent_color = "w" if color == "b" else "b"