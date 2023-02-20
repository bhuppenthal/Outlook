import socket
import json

HOST = "127.0.0.1"
PORT = 54290

# creates a socket object and since using "with" don't have to call s.close()
# AF_INET is the internet address for IPv4, SOCK_STREAM is the socket type for TCP protocol
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"server is on {HOST} and listening on {PORT}")
    while True:
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024) #reads what ever the client sends, if data is an empty object that signals the ct closed the connection
                if not data: #empty obj sent from ct means connection is closed so we exit loop
                    break

                data = data.decode("utf-8")
                data = json.loads(data)
                print(f"recieved the msg: {format(data)}")
                print(type(data))
                if data["action"] == "save":
                    print("save file")
                    with open(data["path"], 'w') as info_file:
                        info_file.write(str(data["info"]) + "\n")
                    success_msg = {"status":"Success"}
                    success_msg_json = json.dumps(success_msg)
                    conn.sendall(bytes(success_msg_json, encoding="utf-8"))
                if data["action"] == "load":
                    print("load file")
                    send_back = {}
                    with open(data["path"], 'r') as load_file:
                        #print(load_file.read())
                        #send_back_text = load_file.read()
                        send_back["info"] = load_file.read()
                    print(send_back)
                    send_back_json = json.dumps(send_back)
                    conn.sendall(bytes(send_back_json, encoding="utf-8"))
