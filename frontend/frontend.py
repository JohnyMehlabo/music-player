from flask import Flask, render_template, request, redirect
import socket
import json

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect(("127.0.0.1", 4444))

def getCurrentStatus():
    s.send("get_current_status".encode())
    data = s.recv(1024).decode().split("¬")
    return (json.loads(data[0]), int(data[1]), int(data[2]))

def getQueue():
    s.send("get_queue".encode())
    data = json.loads(s.recv(1024).decode())
    return data

@app.route("/playlists")
def get_playlists():
    s.send("get_playlists".encode())
    data = json.loads(s.recv(1024).decode())
    return render_template("playlists.html", playlists=data)

@app.route("/play_playlist")
def play_playlist():
    s.send(f"play_playlist {request.args.get('id')}".encode())
    return redirect("/")

@app.route("/songs")
def songs():
    currentSong, _, _ = getCurrentStatus()
    s.send("get_songs".encode())
    data = json.loads(s.recv(4096).decode("utf-8"))
    return render_template("song_list.html", songs=data, currentSong=currentSong)

@app.route("/pause")
def pause():
    s.send("pause".encode())
    return redirect("/")

@app.route("/")
def index():
    currentSong, isPlaying, currentMode = getCurrentStatus()
    queue = []
    if currentMode == 1:
        s.send("get_songs".encode())
        songs = json.loads(s.recv(4096).decode("utf-8"))
        raw_queue = getQueue()
        queue = []
        for i in range(0, len(raw_queue)):
            queue.append(songs[raw_queue[i]])
    print(queue)
    return render_template("index.html", currentSong=currentSong, isPlaying=isPlaying, currentMode=currentMode, queue=queue)

@app.route("/change_queue_index")
def change_queue_index():
    s.send(f"change_queue_index {request.args.get('index')}".encode())
    return redirect("/")

@app.route("/play")
def play_song():
    if request.args.get("id"):
        s.send(f"play {request.args.get('id')}".encode())
    if request.args.get("redirect_uri"):
        redirect_uri = request.args.get("redirect_uri")
    else:
        redirect_uri = "/"
    return redirect(redirect_uri)
