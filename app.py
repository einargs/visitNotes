from quart import Quart
import wave
import socketio
import hypercorn
import asyncio
import aiofiles
import dotenv
import summarize
import speech_recognizer as speech
from socket_server import sio

# We load the environment file
dotenv.load_dotenv()

# If we end up needing quart, this is how you integerate the two:
# https://python-socketio.readthedocs.io/en/latest/api.html#socketio.ASGIApp

# app = Quart(__name__)

# We load the transcript file in for testing. We use it for the
# `send-transcript` event the website uses for testing UI.
transcript_file = open('./data/clean_transcripts/CAR0001.txt')
transcript = list(filter(lambda str: str != "", transcript_file.read().splitlines()))
transcript_file.close()

def cleanup_recording_session(session):
  if 'speech_recognizer' in session:
    speech.end_recognition(session['speech_recognizer'])
    del session['speech_recognizer']
  if 'speech_stream' in session:
    del session['speech_stream']

@sio.on('connect')
async def handle_connect(sid, arg):
  print(f"Connected to {sid}")
  async with sio.session(sid) as session:
    session['transcript'] = []

@sio.on('disconnect')
async def handle_disconnect(sid):
  """
  Here we clean up resources and file handlers if we disconnect early.
  """
  async with sio.session(sid) as session:
    cleanup_recording_session(session)

def open_wav():
  """Opens a wav file with the right settings to record the audio chunks.

  You write to the returned file with `audio_file.writeframes(data)`.

  This is for testing to make sure the audio is formatted right."""
  audio_file = wave.open('./streamed.wav', 'wb')
  audio_file.setnchannels(1)
  audio_file.setsampwidth(2)
  audio_file.setframerate(16000)
  return audio_file

@sio.on('audio-chunk')
async def handle_audio(sid, data):
  """
  Gets a binary chunk of raw PCM data with 1 channel, 2 byte wide samples, and
  16000 samples per second.
  """
  async with sio.session(sid) as session:
    if 'speech_stream' not in session:
      # We check to see if the audio recognizer and stream is already set up.
      # If it isn't, we start it.
      stream, recognizer = speech.start_audio_recognizer(sid)
      session['speech_stream'] = stream
      session['speech_recognizer'] = recognizer
    session['speech_stream'].write(data)

@sio.on('audio-end')
async def handle_audio_end(sid, data):
  async with sio.session(sid) as session:
    cleanup_recording_session(session)

@sio.on('reset-transcript')
async def handle_reset(sid):
  """This is basically just a test event to help the frontend test UI."""
  async with sio.session(sid) as session:
    session['lines_sent'] = 1
    lines = session['lines_sent']*5
    await asyncio.gather(
      sio.emit('transcript-update', to=sid, data=transcript[0:lines]),
      sio.emit('new-summary', to=sid, data=f"TEST SUMMARY: {lines} lines")
    )

@sio.on('send-transcript')
async def handle_transcript(sid):
  """This is basically just a test event to help the frontend test UI."""
  global transcript
  async with sio.session(sid) as session:
    if 'lines_sent' not in session:
      session['lines_sent'] = 0
    session['lines_sent'] += 1
    lines = session['lines_sent']*5
    await asyncio.gather(
      sio.emit('transcript-update', to=sid, data=transcript[0:lines]),
      sio.emit('new-summary', to=sid, data=f"TEST SUMMARY: {lines} lines")
    )

asgi = socketio.ASGIApp(
  sio,
  static_files = {
    '/':

  }
  # other_asgi_app=app
)
