import vlc
import socket
import json
from threading import Thread

Ended = 6
song_id = 0
current_mode = 0

playlist_name = ""
song_queue = []
queue_index = []

p : vlc.MediaPlayer = None

with open("song_list.json", "r") as f:
    song_list = json.loads(f.read())
    f.close()

with open("playlists.json", "r") as f:
    playlists = json.loads(f.read())
    f.close()

def playSong(id):
    global p
    if p:
        p.stop()
    p = vlc.MediaPlayer("songs/" + song_list[id]["filename"])
    p.play()

def handleEnd():
    global queue_index, song_queue
    try:
        global song_id, p
        while True:
            if p:
                current_state = p.get_state()
            else:
                current_state = - 1

            if current_state == Ended:
                if current_mode == 0:
                    song_id += 1
                    if song_id >= len(song_list):
                        song_id = 0
                    playSong(song_id)
                if current_mode == 1:
                    queue_index += 1
                    if queue_index >= len(song_queue):
                        queue_index = 0
                    playSong(song_queue[queue_index])

    except KeyboardInterrupt:
        return

def load_playlist(id):
    global playlists
    return playlists[id]

def handleConnection(conn : socket.socket, addr):
    global p, current_mode, playlist_name, song_queue, queue_index, playlists
    
    while True:
        global song_id
        data = conn.recv(4096).decode()
        values = data.split(" ")
        command = values[0]
        args = values[1:]

        if command == "get_current_status":
            print("Command: get_current_status")
            if current_mode == 0:
                current_song = song_list[song_id]
            elif current_mode == 1:
                current_song = song_list[song_queue[queue_index]]

            if p:
                is_playing = p.is_playing()
            else:
                is_playing = 0
            conn.send(f"{json.dumps(current_song)}¬{is_playing}¬{current_mode}".encode())
        
        if command == "change_queue_index":
            if current_mode == 1 and int(args[0]) < len(song_queue):
                queue_index = int(args[0])
                playSong(song_queue[queue_index])

        if command == "get_queue":
            conn.send(json.dumps(song_queue).encode())

        if command == "get_playlists":
            conn.send(json.dumps(playlists).encode())

        if command == "play":
            current_mode = 0
            print("Command: play")
            song_id = int(args[0])
            playSong(song_id)

        if command == "play_playlist":
            current_mode = 1
            queue_index = 0
            playlist = load_playlist(int(args[0]))
            song_queue = playlist["songs"]
            playlist_name = playlist["name"]
            playSong(song_queue[queue_index])

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
