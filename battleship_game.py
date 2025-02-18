# Battleship Game Core Logic
# This file contains the main game mechanics and board management

from typing import Set, Dict, Tuple  # Type hints for better code understanding
import random

# ASCII Art for visual feedback - makes the game more engaging
# Each message is centered within 53 characters for consistent display
HIT_ART = """
                    ╔╗ ╔═╗╔═╗╔╦╗┬
                    ╠╩╗║ ║║ ║║║║│
                    ╚═╝╚═╝╚═╝╩ ╩o"""

MISS_ART = """
                     ╔╦╗┬┌─┐┌─┐┬
                     ║║║│└─┐└─┐│
                     ╩ ╩┴└─┘└─┘o"""

WIN_ART = """
                ╦  ╦╦╔═╗╔╦╗╔═╗╦═╗╦ ╦┬
                ╚╗╔╝║║   ║ ║ ║╠╦╝╚╦╝│
                 ╚╝ ╩╚═╝ ╩ ╚═╝╩╚═ ╩ o"""

LOSE_ART = """
             ╔═╗╔═╗╔╦╗╔═╗  ╔═╗╦  ╦╔═╗╦═╗┬
             ║ ╦╠═╣║║║║╣   ║ ║╚╗╔╝║╣ ╠╦╝│
             ╚═╝╩ ╩╩ ╩╚═╝  ╚═╝ ╚╝ ╚═╝╩╚═o"""

SUNK_ART = """
                  ╔═╗╦ ╦╦ ╦╔╗╔╦╔═┬
                  ╚═╗║ ║║ ║║║║╠╩╗│
                  ╚═╝╚═╝╚═╝╝╚╝╩ ╩o"""

def print_boards(my_board, shots: set, hits: set):
    """
    Display both game boards side by side
    my_board: The player's own board showing ship positions
    shots: Set of coordinates where the player has fired
    hits: Set of coordinates where the player has hit enemy ships
    """
    # First, create both boards' rows as lists
    enemy_rows = []
    my_rows = []
    
    # Generate enemy board rows
    enemy_rows.append("   A B C D E F G H I J    ")
    enemy_rows.append("  +-------------------+   ")
    for i in range(10):
        row = [" "] * 10
        for j in range(10):
            if (j, i) in shots:
                row[j] = "X" if (j, i) in hits else "O"
        enemy_rows.append(f"{i} |{' '.join(row)}|   ")
    enemy_rows.append("  +-------------------+   ")
    enemy_rows.append("  [    ENEMY BOARD    ]   ")

    # Generate my board rows
    my_rows.append("   A B C D E F G H I J")
    my_rows.append("  +-------------------+")
    for i in range(10):
        row = list(my_board[i])
        # Convert hits and misses to X and O on your board
        for j in range(10):
            if row[j] == 'H':
                row[j] = 'X'
            elif row[j] == 'M':
                row[j] = 'O'
        my_rows.append(f"{i} |{' '.join(row)}|")
    my_rows.append("  +-------------------+")
    my_rows.append("  [     YOUR BOARD    ]")

    # Print boards side by side
    print("\n")
    for i in range(len(enemy_rows)):
        print(f"{enemy_rows[i]}    {my_rows[i]}")
    print("\n")

class BattleshipGame:
    def __init__(self):
        """
        Initialize a new game with:
        - 10x10 game board
        - Standard set of ships and their sizes
        - Empty board and tracking sets for shots and hits
        """
        self.board_size = 10
        # Dictionary of ship types and their lengths
        self.ships = {
            'Carrier': 5,      # Largest ship
            'Battleship': 4,
            'Cruiser': 3,
            'Submarine': 3,
            'Destroyer': 2     # Smallest ship
        }
        # Create empty game board (10x10 grid)
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        # Track opponent's shots for hit detection
        self.opponent_shots = set()
        # Dictionary to track ship positions {ship_name: {(x,y) coordinates}}
        self.ship_positions: Dict[str, Set[Tuple[int, int]]] = {
            'Carrier': set(),
            'Battleship': set(),
            'Cruiser': set(),
            'Submarine': set(),
            'Destroyer': set()
        }
        # Track which ships have been sunk
        self.sunk_ships = set()
        # Track player's shots and hits on enemy board
        self.shots = set()
        self.hits = set()

    def place_ships_randomly(self):
        """
        Randomly place all ships on the board:
        - Ensures ships don't overlap
        - Places ships both horizontally and vertically
        - Retries up to 100 times if placement fails
        """
        for ship, size in self.ships.items():
            attempts = 0
            while attempts < 100:
                horizontal = random.choice([True, False])
                if horizontal:
                    x = random.randint(0, self.board_size - size)
                    y = random.randint(0, self.board_size - 1)
                    positions = [(x + i, y) for i in range(size)]
                else:
                    x = random.randint(0, self.board_size - 1)
                    y = random.randint(0, self.board_size - size)
                    positions = [(x, y + i) for i in range(size)]
                
                if not any(pos in [p for ship_pos in self.ship_positions.values() for p in ship_pos] 
                          for pos in positions):
                    for pos in positions:
                        self.board[pos[1]][pos[0]] = 'S'
                        self.ship_positions[ship].add(pos)
                    break
                attempts += 1

    def check_ship_sunk(self, hit_pos: Tuple[int, int]) -> str:
        """
        Check if hitting this position has sunk a ship
        Returns a message if a ship was sunk, empty string otherwise
        """
        for ship, positions in self.ship_positions.items():
            if hit_pos in positions and ship not in self.sunk_ships:
                if all((x, y) in self.opponent_shots for x, y in positions):
                    self.sunk_ships.add(ship)
                    return f"Sunk {ship}!"
        return ""

    def process_shot(self, move: str) -> str:
        """
        Process a shot at the given coordinates:
        - Validates the move format
        - Checks for hits or misses
        - Updates the game state
        - Returns the result of the shot
        """
        try:
            col = ord(move[0].upper()) - ord('A')
            row = int(move[1:])
            
            if not (0 <= col < self.board_size and 0 <= row < self.board_size):
                return "invalid"
            
            if (col, row) in self.opponent_shots:
                return "repeat"
            
            self.opponent_shots.add((col, row))
            
            # Check if hit
            for positions in self.ship_positions.values():
                if (col, row) in positions:
                    self.board[row][col] = 'H'
                    sunk_message = self.check_ship_sunk((col, row))
                    
                    if len(self.sunk_ships) == len(self.ships):
                        return "gameover"
                    
                    if sunk_message:
                        return f"hit\nsunk"
                    return f"hit"
            
            self.board[row][col] = 'M'
            return f"miss"

        except (IndexError, ValueError):
            return "Invalid move format! Use letter + number (e.g. A5)"

    def handle_move_result(self, move: str, result: str) -> None:
        """
        Update game state based on the result of player's move:
        - Tracks shots and hits
        - Displays appropriate ASCII art for feedback
        - Shows victory message if game is won
        """
        if not result or result in ["invalid", "repeat"]:
            return
            
        col = ord(move[0].upper()) - ord('A')
        row = int(move[1:])
        self.shots.add((col, row))
        
        if "hit" in result:
            self.hits.add((col, row))
            print(f"{HIT_ART}")
            if "sunk" in result:
                print(f"{SUNK_ART}")
        elif "miss" in result:
            print(f"{MISS_ART}")
        elif result == "gameover":
            print(f"{WIN_ART}")
    
    def handle_opponent_move(self, move: str) -> str:
        """
        Process and respond to opponent's move:
        - Updates the board with hit/miss
        - Shows appropriate visual feedback
        - Returns the result to be sent to opponent
        """
        result = self.process_shot(move)
        print(f"\nOpponent's move: {move}")
        
        if "hit" in result:
            print(f"{HIT_ART}")
            if "sunk" in result:
                print(f"{SUNK_ART}")
        elif "miss" in result:
            print(f"{MISS_ART}")
        elif result == "gameover":
            print(f"{LOSE_ART}")
        
        return result

    def display_game_state(self) -> None:
        """
        Show the current state of both game boards:
        - Your board: Shows your ships and opponent's hits/misses
        - Enemy board: Shows your hits and misses
        """
        print_boards(self.board, self.shots, self.hits)

    def validate_move(self, move: str) -> bool:
        """
        Check if a move is in valid format:
        - Must start with a letter (column A-J)
        - Followed by numbers (row 0-9)
        Example: 'A5' or 'H3'
        """
        return len(move) >= 2 and move[0].isalpha() and move[1:].isdigit()