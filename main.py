import asyncio
from loop import EventLoop


async def main():
    await asyncio.sleep(1)
    print('main')

    asyncio.ensure_future(main())
    loop.call_soon(print, 'call_soon')


loop = EventLoop()
asyncio.set_event_loop(loop)


loop.create_task(main())
loop.run_forever()
