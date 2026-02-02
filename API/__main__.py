import asyncio

import uvloop

from twitch import TwitchAPI


async def main():
    twitch_api = TwitchAPI()
    try:
        await twitch_api.run()
    except asyncio.CancelledError:
        await twitch_api.stop()


if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(main())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        task.cancel()
        loop.run_until_complete(task)
    finally:
        loop.close()
