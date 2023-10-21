import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { useAudio } from './socket.js'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import carUrl from '@recordings/CAR0001.mp3'
import resUrl from '@recordings/RES0001.mp3'
import genUrl from '@recordings/GEN0001.mp3'
import mskUrl from '@recordings/MSK0001.mp3'

function AudioPicker() {
  const [recordingSource, setRecordingSource] = useAudio()

  function sourceSetter(value) {
    return () => setRecordingSource(value)
  }

  const fileSources = [
    { name: "Cardiac", path: carUrl },
    { name: "Respiratory", path: resUrl },
    { name: "General", path: genUrl },
    { name: "Misc", path: mskUrl },
  ]

  if (recordingSource == null) return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button>Start Transcription</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Live Sources</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onSelect={sourceSetter("mic")}>
          Microphone
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuLabel>Prerecorded Interviews</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {fileSources.map((src, index) =>
          <DropdownMenuItem key={index} onSelect={sourceSetter(src.path)}>
            {src.name}
          </DropdownMenuItem>)
        }
      </DropdownMenuContent>
    </DropdownMenu>
  )
  else return (
    <Button onClick={sourceSetter(null)}>Stop Transcription</Button>
  )

}

export function SendAudio() {
  return (
    <TooltipProvider delayDuration="500">
      <Tooltip>
        <TooltipTrigger asChild>
          <div>
          <AudioPicker />
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>Choose audio source</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
