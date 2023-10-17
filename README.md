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

# Docker
To build the docker images, you're going to need [nix
installed](https://nixos.org/download.html).

Then, go to the root project directory and run `nix build .#docker`. This will
install all of the tools, build everything, and then place it in `./result`. You
can then load it into docker with `docker load < ./result`.

Then to run it locally, do:
```
docker run --env-file=./.env -p 8000:80 -t visit-notes:latest
```
This launches the docker with environment variables taken from the .env file --
which `load_dotenv` also uses -- which is where we keep all of the api keys for
chatgpt and azure speech recognition. It then binds the local port 8000 to the
port 80 on the docker container, allowing you to load the website with
`localhost:8000`. Then it attaches it to the terminal so that we can see output
and any errors.

To open a shell inside the container you'll want to run:
```
docker run -p 8000:80 --env-file=./.env -it --entrypoint=/bin/sh visit-notes:latest -i
```

You can mount an external file or folder via the mount argument. This mounts a
folder test in the working directory as `/test` in the root of the container.
```
--mount type=bind,source="$(pwd)"/test,target=/test
```

This is very important, because azure speech services only outputs internal
errors to a logfile. You can control the path of this by setting the
`SPEECH_LOG_FILE` environmental variable.

A good default run command is:
```
docker run -d --env-file=./.env -p 8000:80 --env SPEECH_LOG_FILE=/speech-log.txt \
  --mount type=bind,source="$(pwd)"/speech-log.txt,target=/speech-log.txt \
  -t visit-notes:latest
```

This uses `-d` to run it in the background. To stop it, use `docker ps` to list
all running containers and get the id, and then do `docker stop <container-id>`.
You will need to do this even if you run it without `-d`.

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
