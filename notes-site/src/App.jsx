import { useState, useEffect } from 'react'
import { socket, sendAudio } from './socket.js'

function SendAudio() {
  const [isLoading, setIsLoading] = useState(false)
  function onSendAudio() {
    setIsLoading(true)
    sendAudio(() => {
      setIsLoading(false)
    })
  }

  return (
    <button className="bg-indigo-500 text-white rounded text-lg px-2 py-1 shadow-md"
      onClick={onSendAudio} disabled={isLoading}>Send Audio</button>
  );
}

function TranscriptLine({line}) {
  const isDoctor = line.startsWith("D:")
  const type = isDoctor ? "bg-slate-100" : ""
  return (
    <li className={`w-full block p-2 ${type}`}>
      {line}
    </li>
  )
}

function App() {
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

  return (
    <>
      <header className="sticky top-0 z-10 bg-white w-full flex flex-row p-4 items-center justify-between shadow-md">
        <div className="flex flex-row items-baseline space-x-4">
          <h1 className="text-4xl">Simple Prototype</h1>
          <span className="block text-3xl">Connected: {isConnected ? "yes" : "no"}</span>
        </div>
        <SendAudio />
      </header>
      <main className="p-4 space-y-4">
        <div className="flex flex-row items-center space-x-4">
          <p>
            Click the button to tell the server to send the next line of dialogue.
          </p>
        </div>
        <div className="flex flex-row items-start">
          <div className="basis-2/3 w-full block">
            <h2 className="text-2xl p-2">Transcript</h2>
            <ul>
              {transcript.map((line, index) =>
                <TranscriptLine line={line} key={index} />
              )}
            </ul>
          </div>
          <div className="sticky top-20 basis-1/3 rounded bg-slate-100 shadow-md mx-2 p-2">
            <h2 className="text-2xl px-2 pb-2">Summary</h2>
            <div className="rounded p-2 bg-white">
              {summary ? summary : "No summary generated yet."}
            </div>
          </div>
        </div>
      </main>
    </>
  )
}

export default App
