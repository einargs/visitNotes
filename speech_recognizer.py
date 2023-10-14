from summarize import create_transcript_notes
from langchain.docstore.document import Document
import os
import asyncio
import azure.cognitiveservices.speech as speech
import azure.cognitiveservices.speech.audio as saudio
import threading
from socket_server import sio

async def send_notes(sid, transcript):
  """Create notes from the transcript and send them to the website."""
  print("STARTING SEND NOTES")
  notes = await create_transcript_notes(transcript)
  print("GOT NOTES")
  await sio.emit('new-summary', to=sid, data=notes)

async def send_recognized_event(sid, msg):
  """
  Informs the client that text has been recognized and sends notes.
  """
  try:
    async with sio.session(sid) as session:
      session['transcript'].append(msg)
      transcript = session['transcript']
      await asyncio.gather(
        send_notes(sid, transcript),
        sio.emit('transcript-update', to=sid, data=transcript)
      )
  except Exception as err:
    print(f"Error: {err}")

def start_audio_recognizer(sid):
  print("start audio recognizer thread: {}".format(threading.get_ident()))
  speech_key = os.environ.get('SPEECH_KEY')
  speech_region = os.environ.get('SPEECH_REGION')
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
  # We start the speech recognizer here.
  recognizer.start_continuous_recognition_async()
  # I'm not sure why we need to do this when it's already having a session
  # stopped or canceled event, but the docs say to do so.
  def stop_cb():
    nonlocal recognizer
    end_recognition(recognizer)

  # Recognizing is basically each word in a sentence as it's figuring out what
  # someone is saying.
  def recognizing_text(event):
    print("recognizing: {}".format(event.result.text))
  # Recognized is when it's settled down exactly what someone is saying and can
  # format it all. This is what we'll be adding to the transcript logs.
  # We get the 
  loop = asyncio.get_running_loop()
  def recognized_text(event):
    print("recognized_text thread: {}".format(threading.get_ident()))
    print("recognized: {}".format(event.result.text))
    # This callback runs in a different thread, so we call a method to tell the
    # event loop the server is running on to schedule send_recognized_event
    # to happen soon.
    coro = send_recognized_event(sid, event.result.text)
    asyncio.run_coroutine_threadsafe(coro, loop)

  # We don't need the partial recognition events right now.
  # We could send them to the website and have them show up live as people are
  # talking, which could be cool.
  # recognizer.recognizing.connect(recognizing_text)
  recognizer.recognized.connect(recognized_text)
  recognizer.session_stopped.connect(stop_cb)
  recognizer.canceled.connect(stop_cb)
  return push_stream, recognizer

def end_recognition(recognizer):
  recognizer.stop_continuous_recognition()
