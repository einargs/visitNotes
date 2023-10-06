# Frontend Outline (Transcript Only)
This is just an outline of how it'll work with only the transcript.

- Client initiates session and selects which chat log to use.
- Client sends dummy packet that will eventually be audio.
- Server replies with a chunk of dialogue and an updated summary.

## Incorporating Audio
- We'll have to research how to properly send audio information. Do websockets
  work or do we need WebRTC.

## Queries/Pie in the Sky
- We can enable the user to request the AI to make changes to the summary. "Hey,
  the patient said it started two days ago, not one day ago." etc.
- We can enable the user to perform natural language queries of both patient
  records or the conversation so far.
- We can highlight important information in the transcript.
  - Clicking on it could bring up a context menu to include it in the summary or
    find related medical codes?

