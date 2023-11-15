import os
import pathlib
from quart import Quart
import wave
import socketio
import hypercorn
import asyncio
import aiofiles
import dotenv
import summarize
import speech_recognizer as speech
from socket_server import sio, send_error

# We load the environment file
# We provide an environment variable we use on the VM to point us to a new file.
if (dotenv_path := os.environ.get("ENV_FILE")):
  dotenv.load_dotenv(dotenv_path)
else:
  dotenv.load_dotenv()

# If we end up needing quart, this is how you integerate the two:
# https://python-socketio.readthedocs.io/en/latest/api.html#socketio.ASGIApp

# app = Quart(__name__)

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
  print(f"Disconnected from {sid}")
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
  try:
    async with sio.session(sid) as session:
      if 'speech_stream' not in session:
        # We check to see if the audio recognizer and stream is already set up.
        # If it isn't, we start it.
        stream, recognizer = speech.start_audio_recognizer(sid)
        session['speech_stream'] = stream
        session['speech_recognizer'] = recognizer
      session['speech_stream'].write(data)
  except Exception as err:
    print(f"audio handling error: {err}")
    await send_error(err, True, to=sid)

@sio.on('audio-end')
async def handle_audio_end(sid):
  print(f"audio-end event from {sid}")
  async with sio.session(sid) as session:
    try:
      await speech.send_notes(sid, session['transcript'])
    except Exception as err:
      print(f"note creation error: {err}")
      await send_error(err, show=True, to=sid)
    finally:
      cleanup_recording_session(session)

async def get_transcript_text(transcript_name):
  transcript_dir = os.environ.get("TRANSCRIPT_DIR", "./data/selected_transcripts")
  if transcript_name not in ['CAR', 'GEN', 'MSK', 'RES']:
    raise Exception("unknown transcript id")
  path = pathlib.Path(transcript_dir) / (transcript_name + "0001.txt")
  async with aiofiles.open(path, mode='r') as f:
    transcript = []
    async for line in f:
      if line.strip() == '':
        continue
      speaker = line[:3]
      if speaker == "D: ":
        msg = line[3:].strip()
        transcript.append({
          'speaker': "Guest-1",
          'text': msg
        })
      elif speaker == "P: ":
        msg = line[3:].strip()
        transcript.append({
          'speaker': "Guest-2",
          'text': msg
        })
      else:
        transcript[-1]['text'] += " " + line
    return transcript

@sio.on('use-transcript')
async def handle_use_transcript(sid, transcript_name):
  transcript = await get_transcript_text(transcript_name)
  await sio.emit('transcript-update', to=sid, data=transcript)
  await speech.send_notes(sid, transcript)

# Quick hack to let us serve the static files if an environment variable with
# them is set. Used for letting us serve the static files from a docker
# container.
if (static_path := os.environ.get("STATIC_FILES")):
  static_path = pathlib.Path(static_path)
  static_files = {
    '/': str(static_path) + "/"
  }
else:
  static_files = {}
asgi = socketio.ASGIApp(
  sio,
  static_files=static_files
  # other_asgi_app=app
)

if __name__ == "__main__":
  async def main():
    transcripts = await get_transcript_text("GEN")
    print(transcripts)
  asyncio.run(main())
