import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

async def send_error(err, show, to):
  """An error and whether we want to show it on the frontend or just log it."""
  await sio.emit('error', to=to, data=(str(err), show))
