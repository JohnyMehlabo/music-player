import vlc
import socket
import json
from threading import Thread

Ended = 6
song_id = -1

p : vlc.MediaPlayer = None

with open("song_list.json", "r") as f:
    song_list = json.loads(f.read())

def playSong(id):
    global p
    if p:
        p.stop()
    p = vlc.MediaPlayer("songs/" + song_list[id]["filename"])
    p.play()

def handleEnd():
    try:
        global song_id, p
        while True:
            if p:
                current_state = p.get_state()
            else:
                current_state = - 1

            if current_state == Ended:
                song_id += 1
                playSong(song_id)
    except KeyboardInterrupt:
        return

def handleConnection(conn : socket.socket, addr):
    global p
    
    while True:
        global song_id
        data = conn.recv(4096).decode()
        values = data.split(" ")
        command = values[0]
        args = values[1:]

        

        if command == "get_current_status":
            print("Command: get_current_status")
            current_song = song_list[song_id]
            if p:
                is_playing = p.is_playing()
            else:
                is_playing = 0
            conn.send(f"{current_song}-{is_playing}".encode())
        if command == "play":
            print("Command: play")
            song_id = int(args[0])
            playSong(song_id)
        if command == "pause":
            if p:
                p.pause()
        if command == "stop":
            print("Command: play")
            if p:
                p.stop()
        if command == "get_songs":
            print("Command: get_songs")
            conn.send(json.dumps(song_list).encode("utf-8"))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 4444))

s.listen(1)
s.settimeout(0.5)

h_t = Thread(target=handleEnd)
h_t.start()

try:
    while True:
        try:
            conn, addr = s.accept()
            print("Got Connection!")
            t = Thread(target=handleConnection, args=(conn, addr))
            t.start()
        except socket.timeout:
            pass
except KeyboardInterrupt:
    s.close()
