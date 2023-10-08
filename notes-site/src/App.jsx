import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { socket, useSocket } from './socket'
import { SendAudio } from './SendAudio.jsx'

function TranscriptLine({line}) {
  const isDoctor = line.startsWith("D:")
  const type = isDoctor ? "bg-slate-100" : ""
  return (
    <li className={`w-full block p-2 ${type}`}>
      {line}
    </li>
  )
}

function SummaryBox({summary}) {
  return (
    <div className="sticky top-20 basis-1/3 rounded bg-muted shadow-md mx-2 p-2">
      <h2 className="text-2xl px-2 pb-2">Summary</h2>
      <div className="rounded p-2 bg-background">
        {summary ? summary : "No summary generated yet."}
      </div>
    </div>
  )
}

function TranscriptBox({transcript}) {
  return (
    <div className="basis-2/3 w-full block">
      <h2 className="text-2xl p-2">Transcript</h2>
      <ul>
        {transcript.map((line, index) =>
          <TranscriptLine line={line} key={index} />
        )}
      </ul>
    </div>
  )
}

function Header({ isConnected }) {
  function moreTranscript() {
    socket.emit('send-transcript')
  }
  function resetTranscript() {
    socket.emit('reset-transcript')
  }
  return (
    <header className="sticky top-0 z-10 bg-background w-full flex flex-row p-4 items-center justify-between shadow-md">
      <div className="flex flex-row items-baseline space-x-4">
        <h1 className="text-4xl">Simple Prototype</h1>
        <span className="block text-3xl">Connected: {isConnected ? "yes" : "no"}</span>
      </div>
      <div className="flex flex-row items-center space-x-4">
        <Button onClick={resetTranscript}>Reset Transcript</Button>
        <Button onClick={moreTranscript}>More Transcript</Button>
        <SendAudio />
      </div>
    </header>
  )
}

function App() {
  const {isConnected, transcript, summary } = useSocket()

  return (
    <>
      <Header isConnected={isConnected} />
      <main className="p-4 space-y-4">
        <div className="flex flex-row items-center space-x-4">
          <p>
            Click the button to tell the server to send the next line of dialogue.
          </p>
        </div>
        <div className="flex flex-row items-start">
          <TranscriptBox transcript={transcript} />
          <SummaryBox summary={summary} />
        </div>
      </main>
    </>
  )
}

export default App
