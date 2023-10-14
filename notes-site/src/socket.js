import { useState, useEffect } from 'react'
import { io } from 'socket.io-client';
import RecordRTC from 'recordrtc'

const URL = "localhost:5000";

export const socket = io();

export function useAudio() {
  const [isRecording, setIsRecording] = useState(false)
  useEffect(() => {
    if (isRecording) {
      let recorder = null
      navigator.mediaDevices.getUserMedia({
        audio: true
      }).then(stream => {
        console.log("got stream", stream)
        console.log("test", RecordRTC)
        // Copied from:
        // https://gist.github.com/savelee/a3a3f46f393e0e9ce0aa4318bde50b08
        recorder = RecordRTC(stream, {
          //type: 'audio',
          mimeType: 'audio/wav', // I don't think we can get mp3?
          // If we set this as the sample rate, the audio files will play too
          // fast for some reason. Default and the result is understandable.
          // sample rate will probably be determined by speech to text.
          //sampleRate: 44100,
          desiredSampRate: 16000,

          // MediaStreamRecorder, StereoAudioRecorder, WebAssemblyRecorder
          // CanvasRecorder, GifRecorder, WhammyRecorder
          recorderType: RecordRTC.StereoAudioRecorder,

          // Dialogflow / STT requires mono audio
          numberOfAudioChannels: 1,

          // get intervals based blobs
          // value in milliseconds
          // as you might not want to make detect calls every seconds
          timeSlice: 1000,

          // as soon as the stream is available
          // The blob seems to be a discrete, complete file each time it's
          // called. So it produces a single .wav file every 5 seconds.
          ondataavailable(blob) {
            // the WAV header this creates is 44 bytes long
            const pcm = blob.slice(44)
            console.log("Sending blob")
            socket.emit('audio-chunk', pcm)
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
      }
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
