import json
import socket

HOST = "127.0.0.1"
PORT = 54290

client_info = {"action": "save", "path": "./millionaire.txt", "info": "You are millionare yay"}
# client_info = {"action": "load", "path": "financial_info.txt"}
client_info_json = json.dumps(client_info)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(client_info_json, encoding="utf-8"))

    # receive msg, 1024 is the maximum amount to receive at once
    data = s.recv(1024)
    # when bytes arrive, need to save them in a buffer because calling .recv() again reads the next stream of bytes
    data = data.decode("utf-8")
    data = json.loads(data)

print(f"Received {data}")
