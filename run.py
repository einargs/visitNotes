# This just exists for the pyproject.toml script
import app
import asyncio
import signal
from hypercorn.config import Config

def run():
  config = Config()

  shutdown_event = asyncio.Event()

  def _signal_handler(*_: Any) -> None:
          shutdown_event.set()

  loop = asyncio.get_event_loop()
  loop.add_signal_handler(signal.SIGTERM, _signal_handler)
  loop.run_until_complete(
      serve(app, config, shutdown_trigger=shutdown_event.wait)
  )

