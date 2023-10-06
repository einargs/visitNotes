from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask("notes")

socketio = SocketIO(app, cors_allowed_origins='*')

file = open('./data/clean_transcripts/CAR0001.txt')

transcript = list(filter(lambda str: str != "", file.read().splitlines()))

summary = "TEST SUMMARY"

lines_sent = 0

file.close()

@socketio.on('audio')
def handle_audio():
  global lines_sent
  lines_sent += 1
  emit('transcript-update', {
    'transcript':transcript[0:lines_sent],
    'summary': summary }, json=True)

if __name__ == '__main__':
  socketio.run(app)
