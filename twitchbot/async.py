import asyncio
import logging

LOG = logging.getLogger('debug')


class LoopManager:
    """ Class to easily use asynchronous tools. """

    def __init__(self, *coros):
        self.loop = asyncio.get_event_loop()
        for coro in coros:
            self._add_to_loop(coro)

    def _add_to_loop(self, coro):
        LOG.debug("Add '%s' to the event loop", coro)
        asyncio.ensure_future(coro(), loop=self.loop)

    def start(self):
        try:
            self.loop.run_forever()
        except (KeyboardInterrupt, SystemExit, ConnectionError):
            LOG.error("Loop error")
            raise
