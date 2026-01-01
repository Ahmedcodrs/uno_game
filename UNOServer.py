
import pickle
import socket
from _thread import *

# Import your refactored game logic
from Gamelogic import UNOGame

# Server configuration
server = "192.168.1.51"
port = 5560

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    s.bind((server, port))
except socket.error as e:
    print(f"[ERROR] Could not bind to {server}:{port}")
    print(e)
    exit()

s.listen(5)
print(f"[SERVER] Waiting for connections on {server}:{port}")

# ==================== GLOBAL GAME STATE ====================
players = []  # Lobby players: [{"username": "Alice", "ready": False}, ...]
connections = []  # Socket connections
game = None  # The actual UNO game (None until game starts)
game_active = False  # Flag to know if game is running


# ==================== BROADCAST FUNCTION ====================
def broadcast(data):
    """Send data to all connected clients"""
    disconnected = []
    for i, conn in enumerate(connections):
        try:
            conn.sendall(pickle.dumps(data))
        except:
            print(f"[BROADCAST] Failed to send to client {i}")
            disconnected.append(conn)

    # Remove disconnected clients
    for conn in disconnected:
        if conn in connections:
            connections.remove(conn)


# ==================== GAME MANAGEMENT ====================
def check_game_start():
    """
    Check if all players are ready and we should start the game
    Requirements:
    - At least 2 players
    - All players marked as ready
    """
    if len(players) < 2:
        return False

    for p in players:
        if not p.get("ready", False):
            return False

    return True


def start_game():
    """
    Initialize the UNO game with current players
    Called when all players are ready
    """
    global game, game_active

    print("\n" + "=" * 50)
    print("[GAME] Starting UNO Game!")
    print("=" * 50)

    # Extract player names
    player_names = [p["username"] for p in players]
    print(f"[GAME] Players: {', '.join(player_names)}")

    # Create game instance
    game = UNOGame(player_names)
    game_active = True

    print(f"[GAME] Initial top card: {game.discard_pile[-1]}")
    print(f"[GAME] Starting player: {game.get_current_player().name}")

    # Send initial game state to all players
    for player_id in range(len(players)):
        send_game_state_to_player(player_id)

    print("[GAME] Game state sent to all players\n")


def send_game_state_to_player(player_id):
    """
    Send current game state to a specific player
    Each player gets:
    - Full game info
    - Their own hand
    - Other players' card counts (not their actual cards)
    """
    if player_id >= len(connections):
        return

    conn = connections[player_id]

    try:
        # Get game state with this player's hand
        state = game.get_game_state(for_player_id=player_id)

        message = {
            "type": "game_state",
            "state": state,
            "your_player_id": player_id
        }

        conn.send(pickle.dumps(message))
        print(f"[GAME STATE] Sent to Player {player_id} ({players[player_id]['username']})")

    except Exception as e:
        print(f"[ERROR] Failed to send game state to player {player_id}: {e}")


def broadcast_game_state():
    """Send updated game state to ALL players"""
    print("[GAME STATE] Broadcasting to all players...")
    for player_id in range(len(players)):
        send_game_state_to_player(player_id)


# ==================== CLIENT HANDLER ====================
def threaded_client(conn, player_id):
    """
    Handle a single client connection

    Args:
        conn: Socket connection
        player_id: Player's position (0, 1, 2, 3)
    """
    print(f"\n[Player {player_id}] Thread Started")

    # === STEP 1: Send Welcome Message ===
    try:
        welcome = {
            "type": "welcome",
            "player_id": player_id,
            "message": "Connected to UNO server"
        }
        conn.send(pickle.dumps(welcome))
        print(f"[Player {player_id}] Welcome sent")
    except Exception as e:
        print(f"[Player {player_id}] Error sending welcome: {e}")
        conn.close()
        return

    # === STEP 2: Receive Username (Join Message) ===
    try:
        data = conn.recv(2048)
        message = pickle.loads(data)
        print(f"[Player {player_id}] Received: {message}")

        if message.get("type") == "join":
            username = message.get("username")
            players[player_id]["username"] = username
            print(f"[Player {player_id}] Username set: {username}")

            # Send acknowledgment
            ack = {"type": "ack", "message": "Username set"}
            conn.send(pickle.dumps(ack))

            # Broadcast updated player list to everyone
            broadcast({
                "type": "player_list",
                "players": players
            })
        else:
            raise ValueError("Expected 'join' message")

    except Exception as e:
        print(f"[Player {player_id}] Error receiving username: {e}")
        conn.close()
        return

    # === STEP 3: Main Message Loop ===
    print(f"[Player {player_id}] Entering message loop...")

    while True:
        try:
            data = conn.recv(2048)

            if not data:
                print(f"[Player {player_id}] Connection closed (no data)")
                break

            message = pickle.loads(data)
            msg_type = message.get("type")
            print(f"\n[Player {player_id}] Received: {msg_type}")

            # ========== LOBBY MESSAGES ==========

            if msg_type == "toggle_ready":
                # Player toggling ready status in lobby
                players[player_id]["ready"] = not players[player_id]["ready"]
                print(f"[Player {player_id}] Ready: {players[player_id]['ready']}")

                # Check if game should start
                if check_game_start():
                    print("[LOBBY] All players ready! Starting game...")

                    # Tell everyone game is starting
                    broadcast({
                        "type": "game_start",
                        "message": "All players ready, starting game!"
                    })

                    # Initialize the game
                    start_game()
                else:
                    # Just update player list
                    broadcast({
                        "type": "player_list",
                        "players": players
                    })

            # ========== GAME MESSAGES ==========

            elif msg_type == "play_card":
                """
                Player wants to play a card
                Message format:
                {
                    "type": "play_card",
                    "card_index": 3,
                    "chosen_color": "Red"  # Only if Wild card
                }
                """
                if not game_active:
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": "Game not active"
                    }))
                    continue

                card_index = message.get("card_index")
                chosen_color = message.get("chosen_color", None)

                print(f"[GAME] Player {player_id} playing card {card_index}")

                # Execute the move in game logic
                result = game.play_card(player_id, card_index, chosen_color)

                print(f"[GAME] Result: {result}")

                if result["success"]:
                    # Move was valid - broadcast new state to everyone
                    broadcast_game_state()

                    # Check if game ended
                    if result.get("game_over"):
                        print(f"\n{'=' * 50}")
                        print(f"[GAME] GAME OVER! Winner: {result['winner']}")
                        print(f"{'=' * 50}\n")

                        broadcast({
                            "type": "game_over",
                            "winner": result["winner"],
                            "message": f"{result['winner']} wins!"
                        })
                else:
                    # Invalid move - send error only to this player
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": result.get("error", "Invalid move")
                    }))

            elif msg_type == "draw_card":
                """
                Player wants to draw a card
                Message format: {"type": "draw_card"}
                """
                if not game_active:
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": "Game not active"
                    }))
                    continue

                print(f"[GAME] Player {player_id} drawing card")

                # Execute draw action
                result = game.draw_card_action(player_id)

                print(f"[GAME] Draw result: {result}")

                if result["success"]:
                    # Broadcast updated state
                    broadcast_game_state()

                    # Check if game ended (rare, but possible if they drew and auto-played)
                    if result.get("game_over"):
                        broadcast({
                            "type": "game_over",
                            "winner": result["winner"]
                        })
                else:
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": result.get("error", "Cannot draw")
                    }))
            elif msg_type == "call_uno":
                """
                Player calls UNO
                Message format: {"type": "call_uno"}
                """
                if not game_active:
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": "Game not active"
                    }))
                    continue

                print(f"[GAME] Player {player_id} calling UNO")

                # Execute UNO call
                result = game.call_uno(player_id)

                print(f"[GAME] UNO call result: {result}")

                if result["success"]:
                    # Broadcast updated state
                    broadcast_game_state()
                else:
                    # Send error to this player
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": result.get("message", "Cannot call UNO")
                    }))

            elif msg_type == "get_game_state":
                """
                Player requesting current game state (e.g., after reconnect)
                """
                if game_active:
                    send_game_state_to_player(player_id)
                else:
                    conn.send(pickle.dumps({
                        "type": "error",
                        "message": "Game not started yet"
                    }))

            else:
                print(f"[Player {player_id}] Unknown message type: {msg_type}")

        except ConnectionResetError:
            print(f"[Player {player_id}] Connection reset by client")
            break

        except Exception as e:
            print(f"[Player {player_id}] Error: {e}")
            import traceback
            traceback.print_exc()
            break

    # ===== CLEANUP WHEN CLIENT DISCONNECTS =====
    print(f"\n[Player {player_id}] Cleaning up...")

    if conn in connections:
        connections.remove(conn)

    if player_id < len(players):
        players[player_id]["username"] = "Disconnected"
        players[player_id]["ready"] = False

        # Notify others
        broadcast({
            "type": "player_list",
            "players": players
        })

    conn.close()
    print(f"[Player {player_id}] Thread ended\n")


# ==================== MAIN SERVER LOOP ====================
print("[SERVER] Ready to accept connections!\n")

current_player_count = 0

while True:
    # Accept new connection
    conn, addr = s.accept()
    print(f"\n[CONNECTION] New client from {addr}")

    # Add to connections list
    connections.append(conn)

    # Create player slot
    player_id = len(players)
    players.append({"username": None, "ready": False})

    print(f"[CONNECTION] Assigned as Player {player_id}")
    print(f"[SERVER] Total players: {len(players)}")

    # Start thread for this client
    start_new_thread(threaded_client, (conn, player_id))
