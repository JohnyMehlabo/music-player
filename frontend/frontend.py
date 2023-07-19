from flask import Flask, render_template, request
import socket
import json

app = Flask(__name__)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect(("127.0.0.1", 4444))

@app.route("/songs")
def songs():
    s.send("get_songs".encode())
    data = json.loads(s.recv(1024).decode())
    context = {
        songs : data
    }
    return render_template("song_list.html", songs=data)

@app.route("/")
def index():
    return "<p>Hello World</p>"

@app.route("/play")
def play_song():
    if request.args.get("id"):
        s.send(f"play {request.args.get('id')}".encode())
    return "a"
