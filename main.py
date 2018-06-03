import asyncio
import aiohttp
import time
from typing import List


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

    def _timer_handle_cancelled(self, handle):
        pass


async def fetch(session, url):
    print('2-1')
    async with session.get(url) as response:
        print('2-2')
        return await response.text()


async def main():
    print(1)
    async with aiohttp.ClientSession() as session:
        print(2)
        html = await fetch(session, 'http://python.org')
        print(3)
        print(html)

async def foo():
    raise RuntimeError


loop = EventLoop()
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)


# loop.call_later(1, lambda: print(123))
loop.create_task(foo())
loop.run_forever()
