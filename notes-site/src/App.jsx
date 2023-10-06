import { useState, useEffect } from 'react'
import { socket, sendAudio } from './socket.js'
import './App.css'

function App() {
  const [isConnected, setIsConnected] = useState(socket.connected);
  const [summary, setSummary] = useState("")
  const [transcript, setTranscript] = useState([])
  const [isLoading, setIsLoading] = useState(false)

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

  function onSendAudio() {
    setIsLoading(true)
    sendAudio(() => {
      setIsLoading(false)
    })
  }

  return (
    <>
      <h1>Ugly Prototype</h1>
      <p>Connected: {isConnected ? "yes" : "no"}</p>
      <p>
        Click the button to tell the server to send the next line of dialogue.
      </p>
      <button onClick={onSendAudio} disabled={isLoading}>Send Audio</button>
      <div className="holding">
        <div className="transcript">
          <ul>
            {transcript.map(line => <li key={line}>{line}</li>)}
          </ul>
        </div>
        <div className="summary">
          {summary}
        </div>
      </div>
    </>
  )
}

export default App
