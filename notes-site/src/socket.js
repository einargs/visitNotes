import { useState, useEffect } from 'react'
import { io } from 'socket.io-client';
import RecordRTC from 'recordrtc'

// export const socket = io("localhost:8000");
// TODO: set up a config variable or something where it can be localhost in
// development and non-localhost in production. Or get the dev server proxy
// working again.
export const socket = io();

export function useAudio() {
  const [recordingSource, setRecordingSource] = useState(null)
  useEffect(() => {
    if (recordingSource === null) {
      return
    }
    let recorder = null
    let audioContext = null
    let streamPromise 
    if (recordingSource == "mic") {
      streamPromise = navigator.mediaDevices.getUserMedia({
        audio: true
      })
    } else {
      const audio = new Audio(recordingSource)
      audio.play()
      console.log("audio", audio)
      const context = new AudioContext()
      context.resume()
      console.log("context", context)
      audioContext = context
      const source = context.createMediaElementSource(audio)
      const dest = context.createMediaStreamDestination()
      source.connect(dest)
      source.connect(context.destination)
      streamPromise = Promise.resolve(dest.stream)
    }

    streamPromise.then(stream => {
      console.log("got stream", stream)
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
      audioContext?.resume()
    })
    return () => {
      if (recorder !== null) {
        recorder.stopRecording(() => {
          const file = recorder.getBlob()
          socket.emit('audio-end', file)
        })
      }
      audioContext?.close()
    }
  }, [recordingSource])
  return [recordingSource, setRecordingSource]
}

export function useSocket() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState("")
  const [transcript, setTranscript] = useState([])

  useEffect(() => {
    function onConnect() {
      setIsConnected(true);
    }

    function onDisconnect() {
      setIsConnected(false);
    }

    function onTranscriptUpdate(transcript) {
      setTranscript(transcript)
    }

    function onNewSummary(summary) {
      setSummary(summary)
    }

    function onError(err) {
      setError(err)
    }
    
    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);
    socket.on('transcript-update', onTranscriptUpdate)
    socket.on('new-summary', onNewSummary)
    socket.on('error', onError)

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      socket.off('transcript-update', onTranscriptUpdate)
      socket.off('error', onError)
      socket.off('new-summary', onNewSummary)
    };
  }, []);
  return { isConnected, summary, transcript, error, setError }
}
