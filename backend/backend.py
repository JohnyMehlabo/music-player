import vlc
import socket
import json

p : vlc.MediaPlayer = None

with open("song_list.json", "r") as f:
    song_list = json.loads(f.read())



def handleConnection(conn : socket.socket, addr):
    global p
    while True:
        data = conn.recv(1024).decode()
        values = data.split(" ")
        command = values[0]
        args = values[1:]

        if command == "play":
            print("Command: play")
            if p:
                p.stop()
            p = vlc.MediaPlayer("songs\\" + song_list[int(args[0])]["filename"])
            p.play()
        if command == "stop":
            print("Command: play")
            if p:
                p.stop()
        if command == "get_songs":
            print("Command: get_songs")
            conn.send(json.dumps(song_list).encode())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 4444))

s.listen(1)
s.settimeout(0.5)

try:
    while True:
        try:
            conn, addr = s.accept()
            print("Got Connection!")
            handleConnection(conn, addr)
        except socket.timeout:
            pass
except KeyboardInterrupt:
    s.close()
