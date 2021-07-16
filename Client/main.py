import socket
import threading
import json
import discordpresence

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "" #Host IP example 192.168.0.22
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

presence = discordpresence.DiscordIpcClient.for_platform('544620244014989312')

def listen_for_message(cc):
    while True:
        data = cc.recv(1024).decode('utf-8').replace("'", '"')
        if not data:
            break
        try:
            data_json = json.loads(data)
            presence.set_activity(data_json)
            print(data_json)
        except:
            pass

def send(msg):
    client.send(msg.encode(FORMAT))

thread = threading.Thread(target=listen_for_message,args=(client,))
thread.start()


input()
send(DISCONNECT_MESSAGE)
