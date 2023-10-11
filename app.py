from quart import Quart
import wave
import socketio
import hypercorn
import asyncio
import aiofiles

# If we end up needing quart, this is how you integerate the two:
# https://python-socketio.readthedocs.io/en/latest/api.html#socketio.ASGIApp

app = Quart(__name__)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

transcript_file = open('./data/clean_transcripts/CAR0001.txt')
transcript = list(filter(lambda str: str != "", transcript_file.read().splitlines()))
transcript_file.close()

summary = "TEST SUMMARY"

@sio.on('audio-chunk')
async def handle_audio(sid, data):
  # `data` is a binary sequence encoding an entire audio file, not just a chunk
  # of one.
  async with sio.session(sid) as session:
    if 'audio_file' not in session:
      # We're writing the raw PCM.
      audio_file = wave.open('./streamed.wav', 'wb')
      audio_file.setnchannels(1)
      audio_file.setsampwidth(2)
      audio_file.setframerate(16000)
      # audio_file = await aiofiles.open('./streamed.wav', 'wb')
      # I have no idea what the right settings are and I'm starting to think
      # part of the problem is how wav wants the channels interleaved.
      session['audio_file'] = audio_file
    # await session['audio_file'].write(data)
    session['audio_file'].writeframes(data)

@sio.on('audio-end')
async def handle_audio_end(sid, data):
  async with sio.session(sid) as session:
    if 'audio_file' in session:
      session['audio_file'].close()
      # await session['audio_file'].close()
      del session['audio_file']
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
