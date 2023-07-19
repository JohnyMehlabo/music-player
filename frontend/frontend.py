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
    return (json.loads(data[0].replace("'", "\"")), int(data[1]))


@app.route("/songs")
def songs():
    currentSong, _ = getCurrentStatus()
    s.send("get_songs".encode())
    data = json.loads(s.recv(4096).decode("utf-8"))
    return render_template("song_list.html", songs=data, currentSong=currentSong)

@app.route("/pause")
def pause():
    s.send("pause".encode())
    return redirect("/")

@app.route("/")
def index():
    currentSong, isPlaying = getCurrentStatus()
    return render_template("index.html", currentSong=currentSong, isPlaying=isPlaying)

@app.route("/play")
def play_song():
    if request.args.get("id"):
        s.send(f"play {request.args.get('id')}".encode())
    if request.args.get("redirect_uri"):
        redirect_uri = request.args.get("redirect_uri")
    else:
        redirect_uri = "/"
    return redirect(redirect_uri)
