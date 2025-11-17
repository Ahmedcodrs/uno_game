from uno1ver23octVer2 import *
from uno2ver23octVer3 import *
from UNONetworkv2 import Network
import pickle

def main():

    username = username_screen()
    if not username:
        print("No username entered,exiting")
        return  #to exit properly

    print("connecting to server...")
    n = Network()       # Creating one network instance per client joined
    if not n.p:
        print("Failed to connect to server")
        return
    print("joining as ", username )
    responce = n.join(username)
    if responce and responce.get("type") == 'ack':
        print('Successfully joined')
        startlobby(username, n)

    else:
        print("Failed to join as ", username )

if __name__ == "__main__":
    main()