import pickle
from _thread import *
from cgi import print_environ_usage

from UNONetworkv2 import *



server = "192.168.1.51"
port = 5560

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((server, port))
except socket.error as e:
    print(e)

s.listen(5)
print("Waiting for a connection, Server Started")
players = []   #list of players list
connections =[] #the ip addresses of clients connected

# username will be recieved after which sql will be asked if username in playerlist/lobby
#send to clients to open uno2 this will be a function

def broadcast(data):
    for c in connections:
        try:
            c.sendall(pickle.dumps(data))
        except:
            connections.remove(c)


def check_game_start():
    """Check if all players are ready and game should start"""
    if len(players) < 2:
        return False

    # Check if all players are ready
    for p in players:
        if not p.get("ready", False):
            return False

    return True


def threaded_client(conn, player):
   print(f"[Player {player}] Thread Started")

   try:
        welcome = {
           "type": "welcome",
           "player_id": player,
           "message" : 'connected to server'
       }
        conn.send(pickle.dumps(welcome))
        print(f"[Player {player}] Welcome Sent")
   except Exception as e:
        print(f"[Player {player}] Error sending Welcome")
        conn.close()

   try:
        data = conn.recv(2048)
        message = pickle.loads(data)
        print(f"[Player {player}] Received Message: {message}")

        if message.get("type") == "join":
           username = message.get("username")
           players[player]['username'] = username
           print(f"[Player {player}] Username set: {username}")
           ack = {
               "type": "ack",
               "message": "Username set"
            }
           conn.send(pickle.dumps(ack))
           broadcast({
               "type": "player_list",
               "players": players
           })
        else:
            raise ValueError("expected join message")
   except Exception as e:
       print(f'[Player {player}] Error receiving username: {e}')
       conn.close()
       return

   print(f"[Player {player}] Entering message loop")
   while True:
       try:
           data = conn.recv(2048)
           if not data:
               print("[Player {player}] Empty data, Connection closed")
               break
           message = pickle.loads(data)
           msg_type = message.get("type")
           print(f"[Player {player}] Received: {msg_type}")

           if msg_type == "get_players":
               response = {
                   "type": "player_list",
                   "players": players
               }
               conn.send(pickle.dumps(response))
               print(f"[Player {player}] Sent player list")
           elif msg_type == "toggle_ready":
                players[player]["ready"] = not players[player]["ready"]

                #check if game should start based on if all r ready
                if check_game_start():
                    #broadcasts game starts
                    broadcast({
                        "type": "game_start",
                        "message": "All players ready, starting the game"
                    })
                    #send acknowledgement to requester
                    conn.send(pickle.dumps({
                        "type": "game_start",
                        "message": "All players ready, starting the game"

                    }))
                else:
                    broadcast({
                        "type": "player_list",
                        "players": players
                    })
                    conn.send(pickle.dumps({
                        "type": "ack",
                        "message": "Ready toggled"
                    }))

           else:
                print(f"[Player {player}] Unknown message type: {msg_type}")

       except ConnectionResetError:
           print(f"[Player {player}] Connection reset")
           break

       except Exception as e:
           print(f'[Player {player}] Error: {e}')
           import traceback
           traceback.print_exc()
           break

   #clean up
   print(f"[Player {player}] Cleaning up...")
   if conn in connections:
       connections.remove(conn)

   if player < len(players):
       players[player]["username"] = "Left"
       players[player]["ready"] = False
       broadcast({
           "type": "player_list",
           "players": players
       })

   conn.close()
   print(f"[Player {player}] Thread ended")



currentPlayer = 0
while True:
    conn, addr = s.accept()  #conn is the client , addr is the ip address
    print("Connected to:", addr)
    connections.append(conn)
    player = len(players)
    players.append({"username": None, "ready": False})


    start_new_thread(threaded_client,(conn, player))
