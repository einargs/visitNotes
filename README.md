# Frontend
The source for the frontend website is in `frontend-site`.

You'll need Node.js 18+ installed. If your package manager doesn't have it,
you can download it from (here)[https://nodejs.org/en/download/current].
We're using pnpm. To install it, go
(here)[https://pnpm.io/installation#using-npm].

To run the frontend in development mode, `cd` into `notes-site` and run
`pnpm run dev`.

# Backend
We're going to use Quart (basically Flask but for asyncio), python-socketio,
which has better support for sessions and also works with asyncio. To run it,
we're using hypercorn. As such, just run:
```
hypercorn app:asgi -b localhost:5174
```

See hypercorn docs for more.

# Incorporating Audio
- We'll have to research how to properly send audio information. Do websockets
  work or do we need WebRTC.

# Queries/Pie in the Sky
- We can enable the user to request the AI to make changes to the summary. "Hey,
  the patient said it started two days ago, not one day ago." etc.
- We can highlight important information in the transcript.
  - Clicking on it could bring up a context menu to include it in the summary or
    find related medical codes?
