# Client-side implementation of the Battleship game
# This file handles connecting to the server and the client's game interaction

import socket  # Import Python's networking module
from battleship_game import BattleshipGame

def main():
    # Create a TCP socket for client-server communication
    # TCP (Transmission Control Protocol) ensures reliable data transfer
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Get connection details from the user
    # The IP address identifies the server computer on the network
    server_ip = input("Enter server IP address: ")

    # The port number must match the server's port for successful connection
    port = int(input("Enter server port: "))
    
    try:
        # Attempt to establish a connection to the server
        # If the server isn't running, this will raise an exception
        client.connect((server_ip, port))
        print("Connected to server!")
        
        # Wait for the server's ready signal before starting
        # This ensures both players are ready to begin
        client.recv(1024).decode()
        
        # Initialize the game board and randomly place ships
        game = BattleshipGame()
        game.place_ships_randomly()
        print("\nGame Started! All ships have been placed:")
        
        # Client always moves first in this implementation
        my_turn = True
        
        # Main game loop
        while True:
            # Display both players' boards (showing appropriate information)
            game.display_game_state()
            
            if my_turn:
                # CLIENT'S TURN
                # Keep asking for input until the player enters a valid move
                while True:
                    move = input("\nYour move (e.g. A5): ")
                    if game.validate_move(move):
                        break
                    print("Invalid move format!")
                
                # Send the move to the server and wait for response
                client.send(move.encode())
                response = client.recv(1024).decode()
                
                # Handle different response types from the server
                if response == "repeat":
                    print("\nYou already shot there!")
                    continue
                elif response == "invalid":
                    print("\nInvalid move! Try again")
                    continue
                
                # Update the game state based on the server's response
                game.handle_move_result(move, response)
                if response == "gameover":
                    game.display_game_state()
                    break
                
                my_turn = False
            else:
                # OPPONENT'S TURN
                print("\nWaiting for opponent's move...")
                
                result = ""
                is_valid = False
                while not is_valid:
                    # Receive the opponent's move (blocking call)
                    data = client.recv(1024).decode()
                    if not data:  # Connection closed by client
                        break
                    
                    # Process the opponent's move and send back the result
                    result = game.handle_opponent_move(data)
                    client.send(result.encode())
                    # Check if the result was invalid
                    if result == "repeat" or result == "invalid":
                        # If it was invalid, ask the client again
                        continue
                    else:
                        # The result was valid and we don't have to ask again
                        is_valid = True
                else:
                    # If the loop was exited naturally (not broken), continue the game
                    if result == "gameover":
                        game.display_game_state()
                        break
                    my_turn = True
                # If the else block was not triggered, then the connection was closed and the game loop should end
                if not my_turn:
                    break
                
    except ConnectionRefusedError:
        # This exception occurs when we can't connect to the server
        print("Could not connect to server. Make sure server is running and address is correct.")
    except Exception as e:
        # Handle any other unexpected errors
        print(f"Error: {e}")
    finally:
        # Always close the network connection when we're done
        client.close()

# Only run the client if this file is run directly
if __name__ == "__main__":
    main()