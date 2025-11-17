import socket
import pickle
import threading
import time


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.1.51"
        self.port = 5560
        self.addr = (self.server, self.port)
        self.player_id = None

        # Shared state (updated by listener)
        self.players = []
        self.game_started = False
        self.running = True

        # Don't start listener yet - do it after join
        self.listener_thread = None

        # Connect and get welcome
        self.p = self.connect()

    def connect(self):
        """Connect to server and receive welcome message"""
        try:
            print("Connecting to", self.addr)
            self.client.connect(self.addr)
            print("Connected! Waiting for welcome...")

            welcome_data = self.client.recv(2048)
            welcome = pickle.loads(welcome_data)
            print(f"Welcome message: {welcome}")

            if welcome.get("type") == "welcome":
                self.player_id = welcome.get("player_id")
                print(f"Connected! Player ID: {self.player_id}")
                return welcome
            else:
                print(f"Unexpected message: {welcome}")
                return None

        except Exception as e:
            print(f"Connection error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def join(self, username):
        """Send join message with username"""
        print(f"Sending join message for {username}")

        # Send join message
        message = {"type": "join", "username": username}
        try:
            self.client.send(pickle.dumps(message))

            # Wait for ack response
            response_data = self.client.recv(2048)
            response = pickle.loads(response_data)
            print(f"Join response: {response}")

            # NOW start the listener thread after join is complete
            if response.get("type") == "ack":
                self.start_listener()

            return response

        except Exception as e:
            print(f"Error joining: {e}")
            return None

    def start_listener(self):
        """Start the background listener thread"""
        if self.listener_thread is None:
            self.listener_thread = threading.Thread(target=self.listen_for_updates, daemon=True)
            self.listener_thread.start()
            print("Listener thread started")

    def listen_for_updates(self):
        """Background thread that constantly listens for server broadcasts"""
        while self.running:
            try:
                data = self.client.recv(2048)
                if not data:
                    print("[LISTENER] No data, stopping")
                    break

                message = pickle.loads(data)
                msg_type = message.get("type")
                print(f"[LISTENER] Received: {msg_type}")

                # Update shared state based on message type
                if msg_type == "player_list":
                    self.players = message.get("players", [])
                    print(f"[LISTENER] Updated players: {len(self.players)} players")

                elif msg_type == "game_start":
                    self.game_started = True
                    print("[LISTENER] Game starting flag set!")

                elif msg_type == "game_state":
                    self.game_state = message

            except Exception as e:
                print(f"[LISTENER] Error: {e}")
                break

        print("[LISTENER] Thread ended")

    def send_action(self, action_type, **data):
        """Send an action without waiting for response"""
        message = {"type": action_type}
        message.update(data)
        try:
            self.client.send(pickle.dumps(message))
            print(f"Sent action: {action_type}")
        except Exception as e:
            print(f"Error sending action: {e}")

    def stop(self):
        """Stop the listener thread"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
