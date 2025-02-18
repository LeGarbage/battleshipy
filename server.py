# Server-side implementation of the Battleship game
# This file handles the server's network connection and game logic

import socket  # Python's built-in networking module
from battleship_game import BattleshipGame

def main():
    # Create a new TCP socket for network communication
    # TCP ensures reliable, ordered data delivery between the client and server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Get the port number from user input
    # Ports are like specific channels that network traffic can flow through
    port = int(input("Enter port number: "))
    
    # Bind the server to listen on all available network interfaces ('')
    # This allows connections from any IP address that can reach this computer
    server.bind(('', port))
    
    # Start listening for incoming connections
    # The parameter 1 means we only allow one connection in the waiting queue
    server.listen(1)
    print(f"Server started on port {port}")
    
    # Initialize the game board and ships
    game = BattleshipGame()
    print("\nWaiting for opponent...")
    
    # accept() blocks (waits) until a client connects
    # It returns a new socket specifically for this connection and the client's address
    conn, addr = server.accept()
    print(f"Opponent has connected from {addr}!")
    
    # Send a ready signal to the client to synchronize game start
    conn.send("ready".encode())
    
    # Randomly place ships on the server's board
    game.place_ships_randomly()
    
    # Server plays second (client goes first)
    my_turn = False
    print("\nGame started! All ships have been placed.")
    
    try:
        while True:
            # Show current game state (both boards)
            game.display_game_state()
            
            if not my_turn:
                # OPPONENT'S TURN
                print("\nWaiting for opponent's move...")
                # Receive the opponent's move (blocking call)
                data = conn.recv(1024).decode()
                if not data:  # Connection closed by client
                    break
                
                result = ""
                while  result == "repeat" or result == "invalid" or result == "":
                    # Process the opponent's move and send back the result
                    result = game.handle_opponent_move(data)
                    conn.send(result.encode())
                    
                    if result == "gameover":
                        game.display_game_state()
                        break
                my_turn = True
            else:
                # SERVER'S TURN
                # Keep asking for input until a valid move is entered
                while True:
                    move = input("\nYour move (e.g. A5): ")
                    if game.validate_move(move):
                        break
                    print("Invalid move format!")
                
                # Send our move to the client
                conn.send(move.encode())
                
                # Get the result of our move
                result = conn.recv(1024).decode()
                
                # Handle different response cases
                if result == "repeat":
                    print("\nYou already shot there!")
                    continue
                elif result == "invalid":
                    print("\nInvalid move! Try again")
                    continue
                
                # Update game state based on move result
                game.handle_move_result(move, result)
                if result == "gameover":
                    game.display_game_state()
                    break
                    
                my_turn = False
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up network resources when the game ends
        conn.close()
        server.close()

# Only run the server if this file is run directly (not imported)
if __name__ == "__main__":
    main()
