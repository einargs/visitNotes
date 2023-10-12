from quart import Quart
import wave
import socketio
import hypercorn
import asyncio
import aiofiles
import os
import azure.cognitiveservices.speech as speech
import azure.cognitiveservices.speech.audio as saudio

# If we end up needing quart, this is how you integerate the two:
# https://python-socketio.readthedocs.io/en/latest/api.html#socketio.ASGIApp

speech_key = os.environ.get('SPEECH_KEY')
speech_region = os.environ.get('SPEECH_REGION')

app = Quart(__name__)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

transcript_file = open('./data/clean_transcripts/CAR0001.txt')
transcript = list(filter(lambda str: str != "", transcript_file.read().splitlines()))
transcript_file.close()

summary = "TEST SUMMARY"

def start_audio_recognizer():
  global speech_key
  global speech_region
  speech_config = speech.SpeechConfig(speech_key, speech_region)
  speech_config.speech_recognition_language="en-US"
  # Set up the format for the audio stream
  audio_format = saudio.AudioStreamFormat(
    bits_per_sample=16, channels=1, samples_per_second=16000)
  # We use a push audio stream that maintains an internal buffer we can write
  # to from elsewhere. I don't know if we need a lock for it.
  push_stream = saudio.PushAudioInputStream(audio_format)
  audio_config = speech.audio.AudioConfig(stream=push_stream)
  recognizer = speech.SpeechRecognizer(
    speech_config=speech_config, audio_config=audio_config)
  recognizer.start_continuous_recognition()
  def stop_cb():
    nonlocal recognizer
    end_recognition(recognizer)
  def recognizing_text(event):
    print("recognizing: {}".format(event.result.text))
  def recognized_text(event):
    print("recognized: {}".format(event.result.text))
  recognizer.recognizing.connect(recognizing_text)
  recognizer.recognized.connect(recognized_text)
  recognizer.session_stopped.connect(stop_cb)
  recognizer.canceled.connect(stop_cb)
  return push_stream, recognizer

def end_recognition(recognizer):
  recognizer.stop_continuous_recognition()

def cleanup_recording_session(session):
  if 'speech_recognizer' in session:
    end_recognition(session['speech_recognizer'])
    del session['speech_recognizer']
  if 'audio_file' in session:
    session['audio_file'].close()
    del session['audio_file']
    # await session['audio_file'].close()
  if 'speech_stream' in session:
    del session['speech_stream']

@sio.on('disconnect')
async def handle_disconnect(sid):
  async with sio.session(sid) as session:
    cleanup_recording_session(session)

@sio.on('audio-chunk')
async def handle_audio(sid, data):
  # `data` is a binary sequence encoding an entire audio file, not just a chunk
  # of one.
  async with sio.session(sid) as session:
    if 'audio_file' not in session:
      # Our first message
      # We're writing the raw PCM.
      audio_file = wave.open('./streamed.wav', 'wb')
      audio_file.setnchannels(1)
      audio_file.setsampwidth(2)
      audio_file.setframerate(16000)
      #audio_file = await aiofiles.open('./streamed.wav', 'wb')
      # I have no idea what the right settings are and I'm starting to think
      # part of the problem is how wav wants the channels interleaved.
      session['audio_file'] = audio_file
      stream, recognizer = start_audio_recognizer()
      session['speech_stream'] = stream
      session['speech_recognizer'] = recognizer
    #await session['audio_file'].write(data)
    session['audio_file'].writeframes(data)
    session['speech_stream'].write(data)

@sio.on('audio-end')
async def handle_audio_end(sid, data):
  async with sio.session(sid) as session:
    cleanup_recording_session(session)
  async with aiofiles.open('./at-end.wav', 'wb') as file:
    await file.write(data)

@sio.on('reset-transcript')
async def handle_reset(sid):
  async with sio.session(sid) as session:
    session['lines_sent'] = 1
    await sio.emit('transcript-update', data={
      'transcript':transcript[0:session['lines_sent']*5],
      'summary': summary }, to=sid)

@sio.on('send-transcript')
async def handle_transcript(sid):
  async with sio.session(sid) as session:
    if 'lines_sent' not in session:
      session['lines_sent'] = 0
    session['lines_sent'] += 1
    await sio.emit('transcript-update', data={
      'transcript':transcript[0:session['lines_sent']*5],
      'summary': summary }, to=sid)

asgi = socketio.ASGIApp(sio, other_asgi_app=app)
