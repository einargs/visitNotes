import { useState, useEffect } from 'react'
import { io } from 'socket.io-client';
// import RecordRTC from 'recordrtc'

const URL = "localhost:5000";

export const socket = io(URL);

export function useAudio() {
  const [isRecording, setIsRecording] = useState(false)
  useEffect(() => {
    if (isRecording) {
      const chunks = []
      let recorder = null
      navigator.mediaDevices.getUserMedia({
        audio: true,
      }).then(stream => {
        console.log(stream.getAudioTracks())
        // TODO: look at multiple channels and merging them if needed?
        // Also, if necessary, I could probably do this in an AudioWorklet,
        // but I don't need to.
        recorder = new MediaRecorder(stream, {
          //audioBitsPerSecond: 
          mimeType: "audio/ogg; codec=opus"
          // mimeType: "audio/wave"
        })
        console.log(recorder.mimeType, recorder)

        recorder.ondataavailable = (e) => {
          chunks.push(e.data)
          // we send the raw info over
          // we could send `recorder.audioBitsPerSecond`? Not sure if needed.
          socket.emit('audio-chunk', e.data)
        }

        recorder.onstop = () => {
          // We turn the entire thing into a single blob file. We might be able
          // to also turn it into e.g. a different codec? I might need a second
          // media recorder for that. e.g. "audio/ogg; codec=opus"
          const entireRecord = new Blob(chunks, { type: "audio/ogg; codec=opus" })
          socket.emit('audio-end', entireRecord)
        }
        recorder.start(1000) // work in 1 sec intervals
      })
      return () => {
        recorder?.stop()
      }
      /* RecordRTC code
      let recorder = null
      navigator.mediaDevices.getUserMedia({
        audio: true
      }).then(stream => {
        console.log("got stream", stream)
        console.log("test", RecordRTC)
        // Copied from:
        // https://gist.github.com/savelee/a3a3f46f393e0e9ce0aa4318bde50b08
        recorder = RecordRTC(stream, {
          type: 'audio',
          mimeType: 'audio/wav', // I don't think we can get mp3?
          // If we set this as the sample rate, the audio files will play too
          // fast for some reason. Default and the result is understandable.
          // sample rate will probably be determined by speech to text.
          //sampleRate: 44100,

          // MediaStreamRecorder, StereoAudioRecorder, WebAssemblyRecorder
          // CanvasRecorder, GifRecorder, WhammyRecorder
          recorderType: RecordRTC.StereoAudioRecorder,

          // Dialogflow / STT requires mono audio
          numberOfAudioChannels: 1,

          // get intervals based blobs
          // value in milliseconds
          // as you might not want to make detect calls every seconds
          timeSlice: 5000,

          // as soon as the stream is available
          // The blob seems to be a discrete, complete file each time it's
          // called. So it produces a single .wav file every 5 seconds.
          ondataavailable(blob) {
            console.log("Sending blob", blob)
            socket.emit('audio-chunk', blob)
          }
        })
        recorder.startRecording()
      })
      return () => {
        if (recorder !== null) {
          recorder.stopRecording(() => {
            const file = recorder.getBlob()
            socket.emit('audio-end', file)
          })
        }
      }*/
    }
  }, [isRecording])
  return [isRecording, setIsRecording]
}

export function useSocket() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [summary, setSummary] = useState("")
  const [transcript, setTranscript] = useState([])

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    function onTranscriptUpdate(update) {
      setSummary(update.summary)
      setTranscript(update.transcript)
    }
    
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('transcript-update', onTranscriptUpdate)

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('transcript-update', onTranscriptUpdate)
    };
  }, []);
  return { isConnected, summary, transcript }
}
