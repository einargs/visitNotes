from flask import Flask
from flask_socketio import SocketIO, send, emit

app = Flask("notes")

socketio = SocketIO(app, cors_allowed_origins='*')

transcript_file = open('./data/clean_transcripts/CAR0001.txt')
transcript = list(filter(lambda str: str != "", transcript_file.read().splitlines()))
transcript_file.close()

summary = "TEST SUMMARY"

lines_sent = 0

audio_file = None

@socketio.on('audio-chunk')
def handle_audio(data):
  global audio_file
  if audio_file is None:
    audio_file = open('./streamed.wav', 'wb')
  audio_file.write(data)

@socketio.on('audio-end')
def handle_audio_end(data):
  global audio_file
  if audio_file is not None:
    audio_file.close()
    audio_file = None
  with open('./at-end.wav', 'wb') as file:
    file.write(data)

@socketio.on('reset-transcript')
def handle_reset():
  global lines_sent
  lines_sent = 1
  emit('transcript-update', {
    'transcript':transcript[0:lines_sent*5],
    'summary': summary }, json=True)
  

@socketio.on('send-transcript')
def handle_transcript():
  global lines_sent
  lines_sent += 1
  emit('transcript-update', {
    'transcript':transcript[0:lines_sent*5],
    'summary': summary }, json=True)

if __name__ == '__main__':
  socketio.run(app)
