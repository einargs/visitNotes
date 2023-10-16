import { Button } from '@/components/ui/button'
import { useState } from 'react'
import { useAudio } from './socket.js'

export function SendAudio() {
  // In a perfect world, we would wait to request access to the microphone until
  // they've clicked on the button. But this is a demo so we don't need to worry
  // about it.
  const [isRecording, setIsRecording] = useAudio()

  function onToggle() {
    setIsRecording(bool => !bool)
  }

  return (
    <Button onClick={onToggle}>
      {isRecording ? "Stop Recording" : "Start Recording"}
    </Button>
  );
}
