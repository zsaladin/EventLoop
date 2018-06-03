import asyncio
import logging
import time

from typing import List


logger = logging.getLogger(__name__)


class EventLoop(asyncio.AbstractEventLoop):
    def __init__(self):
        self._scheduled: List[asyncio.TimerHandle] = []
        self._ready: List[asyncio.Handle] = []

    def is_running(self):
        return True

    def call_at(self, when, callback, *args):
        handler = asyncio.TimerHandle(when, callback, args, self)
        self._scheduled.append(handler)
        return handler

    def call_soon(self, callback, *args):
        handler = asyncio.Handle(callback, args, self)
        self._ready.append(handler)
        return handler

    def call_later(self, delay, callback, *args):
        return self.call_at(self.time() + delay, callback, *args)

    def create_future(self):
        return asyncio.Future(loop=self)

    def create_task(self, coro):
        return asyncio.Task(coro, loop=self)

    def run_forever(self):
        while True:
            if self._check_stop():
                return

            self._check_scheduled()
            self._run_ready()

    def _check_stop(self):
        return not self.is_running()

    def _check_scheduled(self):
        self._scheduled = [handle for handle in self._scheduled if not handle._cancelled]

        now = self.time()
        self._ready.extend(handle for handle in self._scheduled if handle._when <= now)
        self._scheduled = [handle for handle in self._scheduled if handle._when > now]

    def _run_ready(self):
        for handle in self._ready:
            handle._callback(*handle._args)

        self._ready.clear()

    def time(self):
        return time.monotonic()

    def get_debug(self):
        pass

    def call_exception_handler(self, context):
        logger.error(f"{context['message']}\n"
                     f"{type(context['exception']).__name__} {context['exception']}\n"
                     f"{context['future']}")

    def _timer_handle_cancelled(self, handle):
        pass
