import socket
import json

HOST = "127.0.0.1"
PORT = 54290

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"server is on {HOST} listening on {PORT}")
    while True:
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode("utf-8")
                data = json.loads(data)

                if data["action"] == "save":
                    with open(data["path"], 'w') as info_file:
                        info_file.write(json.dumps(data["info"]))
                    success_msg = {"status": "Success"}
                    success_msg_json = json.dumps(success_msg)
                    conn.sendall(bytes(success_msg_json, encoding="utf-8"))

                if data["action"] == "load":
                    send_back = {}
                    with open(data["path"], 'r') as load_file:
                        file_data = load_file.read()
                        send_back["info"] = json.loads(file_data)
                    send_back_json = json.dumps(send_back)
                    conn.sendall(bytes(send_back_json, encoding="utf-8"))
