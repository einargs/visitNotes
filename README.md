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
hypercorn app:asgi -b localhost:8000
```

See hypercorn docs for more.

## Transcript
Eventually the transcript should contain objects that indicate whether the
doctor or patient is speaking. Every time a recognized event is fired we'll
add that to the transcript list, and use speaker recognition to tell whether
it's the doctor or patient. (We may not be able to tell whether it's the doctor
or patient who is speaking, in which case I suppose it'll be an object with a
speaker id note.)

Then, when turning it into documents for langchain, we can try and condense
multiple sentences in sequence from the same speaker into one document. There
are also other kinds of metadata it might allow us to annotate with.

It's important to remember that there can easily be more than two people
speaking to a doctor in a meeting.

# Pydoc
You may need to call `python -m pydoc -b` to launch pydoc as aware of packages
installed in the virtual environment.

## Doctor vs. Patient
One nice feature might be writing a module to determine whether the doctor or
patient is speaking.

# Queries/Pie in the Sky
- We can enable the user to request the AI to make changes to the summary. "Hey,
  the patient said it started two days ago, not one day ago." etc.
- We can highlight important information in the transcript.
  - Clicking on it could bring up a context menu to include it in the summary or
    find related medical codes?
