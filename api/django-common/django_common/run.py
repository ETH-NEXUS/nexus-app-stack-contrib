# Code copied from https://stackoverflow.com/questions/52232177/runtimeerror-timeout-context-manager-should-be-used-inside-a-task/69514930#69514930
# An asyncio run implementation that runs in any environment e.g. Gunicorn.
import asyncio
import threading
from typing import Awaitable, TypeVar


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


_LOOP = asyncio.new_event_loop()
_LOOP_THREAD = threading.Thread(
    target=_start_background_loop, args=(_LOOP,), daemon=True
)
_LOOP_THREAD.start()

T = TypeVar("T")


def asyncio_run(coro: Awaitable[T], timeout=30) -> T:
    """
    Runs the coroutine in an event loop running on a background thread,
    and blocks the current thread until it returns a result.
    This plays well with gevent, since it can yield on the Future result call.

    :param coro: A coroutine, typically an async method
    :param timeout: How many seconds we should wait for a result before raising an error
    """
    return asyncio.run_coroutine_threadsafe(coro, _LOOP).result(timeout=timeout)


def asyncio_gather(*futures, return_exceptions=False) -> list:
    """
    A version of asyncio.gather that runs on the internal event loop
    """
    async def gather():
        return await asyncio.gather(*futures, return_exceptions=return_exceptions)

    return asyncio.run_coroutine_threadsafe(gather(), loop=_LOOP).result()
