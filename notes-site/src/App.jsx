import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { useSocket } from './socket'
import { SendTranscript, SendAudio } from './SendAudio.jsx'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Loader2 } from 'lucide-react'
import logo from '/audio-logo.png'

function TranscriptLine({line}) {
  const isDoctor = line['speaker'] == 'Guest-1'
  const type = isDoctor ? "bg-slate-100" : ""
  const speaker = isDoctor ? "Doctor" : "Patient"
  return (
    <li className={`w-full block p-2 ${type}`}>
      {speaker}: {line['text']}
    </li>
  )
}

function LoadingSummary() {
  return (
    <div className="rounded p-2 bg-background flex flex-col items-center">
      <Loader2 size={96} color="#3ca334" strokeWidth={2}
        className="animate-spin" />
    </div>
  )
}

function SummaryBox({summary, generatingSummary}) {
  const text = (
    <div className="rounded p-2 bg-background">
      <p>{summary ? summary : "No summary generated yet."}</p>
    </div>
  )
  return (
    <div className="sticky top-20 basis-1/3 rounded bg-muted shadow-md mx-2 p-2">
      <h2 className="text-2xl px-2 pb-2">Doctor Notes</h2>
        {generatingSummary ? <LoadingSummary /> : text}
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
  return (
    <header className="sticky top-0 z-10 bg-background w-full flex flex-row p-4 items-center justify-between shadow-md">
      <div className="flex flex-row items-center space-x-4">
        <img className="h-12" src={logo} alt="Logo" />
        <h1 className="text-4xl">TrueBlueMD</h1>
        {/*<span className="block text-2l">{isConnected ? "Connected" : "Not Connected"}</span>*/}
      </div>
      <div className="flex flex-row items-center space-x-4">
        <SendTranscript />
        <SendAudio />
      </div>
    </header>
  )
}

function ErrorAlert({error, dismissError}) {
  function onChange(bool) {
    if (!bool) {
      dismissError()
    }
  }
  return (
    <AlertDialog open={error !== null} onOpenChange={onChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>An error occured</AlertDialogTitle>
          <AlertDialogDescription>
            {error}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction>Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

function App() {
  const {isConnected, generatingSummary, transcript,
    summary, error, setError } = useSocket()
  function handleDismiss() {
    setError(null)
  }

  return (
    <>
      <Header isConnected={isConnected} />
      <main className="p-4 space-y-4">
        <ErrorAlert error={error} dismissError={handleDismiss} />
        <div className="flex flex-col space-y-4 px-16">
          <p>
            To use the microphone to record a live sentence, click Start
            Transcription and select microphone from the dropdown menu. To use
            a simulated, pre-recorded conversation from a dataset created by
            doctors, select a recording from the Prerecorded Interviews section
            of the dropdown menu.
          </p>
          <p>
            Alternatively, you can use an existing transcript of one of those
            conversations. Click Existing Transcript to select a transcript
            corresponding to one of the audio files.
          </p>
        </div>
        <div className="flex flex-row items-start">
          <TranscriptBox transcript={transcript} />
          <SummaryBox summary={summary} generatingSummary={generatingSummary} />
        </div>
      </main>
    </>
  )
}

export default App
