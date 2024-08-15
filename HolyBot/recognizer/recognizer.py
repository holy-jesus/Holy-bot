import asyncio
import sys
from time import perf_counter, time

import aiofiles
import aiohttp
import uvloop
from fake_headers import Headers
from loguru import logger
from shazamio import Shazam

from connectors import Client

logger.remove()
logger.add(sys.stdout, level="TRACE", enqueue=True)


class Recognizer:
    client = Client(name="recognizer", host="localhost", port=42069)

    def __init__(self) -> None:
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.session: aiohttp.ClientSession = None
        self.shazam: Shazam = None
        self.client.instance_of_class = self
        self.client.loop = self.loop
        self.client_id = "ue6666qo983tsx6so1t0vnawi233wa"
        self.headers = Headers(headers=True).generate()
        self.headers.update(
            {
                "Client-Id": self.client_id,
                "Referer": "https://www.twitch.tv/",
                "Origin": "https://www.twitch.tv",
            }
        )
        self.information = {}

    async def _make_request(self, method, url, headers=None, json=None, data=None):
        for _ in range(3):
            try:
                logger.trace(f"Делаю {method} запрос на {url[:25]}")
                return await self.session.request(
                    method, url, headers=headers, json=json, data=data
                )
            except aiohttp.ClientError as e:
                logger.exception(e)

    async def _get_m3u8(self, login: str) -> str:
        operation = {
            "operationName": "PlaybackAccessToken",
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "0828119ded1c13477966434e15800ff57ddacf13ba1911c129dc2200705b0712",
                }
            },
            "variables": {
                "isLive": True,
                "login": login.lower(),
                "isVod": False,
                "vodID": "",
                "playerType": "twitch_everywhere",
            },
        }
        response = await self._make_request(
            "POST",
            "https://gql.twitch.tv/gql",
            headers=self.headers,
            json=operation,
        )
        json = await response.json()
        if "data" not in json:
            logger.error("Не смог получить PlaybackAccessToken, выхожу.")
            return None
        playback_token = (await response.json())["data"]["streamPlaybackAccessToken"]
        logger.trace(f"Успешно получил PlaybackAccessToken {playback_token}")
        response = await self._make_request(
            "GET",
            f"https://usher.ttvnw.net/api/channel/hls/{login}.m3u8?client_id={self.client_id}"
            f"&token={playback_token['value']}&sig={playback_token['signature']}&allow_source=true&allow_audio_only=true",
            headers=self.headers,
        )
        playlists = self._m3u8_parser(await response.text())
        logger.trace(f"Успешно получил плейлисты: {playlists}")
        if not playlists:
            logger.error("Не получил плейлисты, выхожу")
            return None
        else:
            return playlists[-1]

    def _m3u8_parser(self, content: str) -> list | None:
        uris = []
        if content.endswith("#EXT-X-ENDLIST"):
            return None
        for s in content.split():
            if s.startswith("https"):
                uris.append(s)
            elif s.startswith("#EXT-X-TWITCH-PREFETCH:"):
                uris.append(s.lstrip("#EXT-X-TWITCH-PREFETCH:"))
        return uris

    async def _download_fragment(self, segments, uri):
        response = await self._make_request("GET", uri, headers=self.headers)
        segments[uri] = await response.content.read()

    async def _thread(self, login) -> None:
        for _ in range(3):
            stream = await self._get_m3u8(login)
            if stream:
                logger.debug("Успешно получил стрим.")
                break
            logger.info("Не смог получить стрим, повторная попытка через 5 сек.")
            await asyncio.sleep(5)
        else:
            self.information[login] = {
                "task": None,
                "segments": {},
                "errors": [],
            }
            logger.error("Слишком много неуспешных попыток, выхожу.")
            return
        segments = self.information[login]["segments"]

        while True:
            try:
                start_time = perf_counter()
                response = await self._make_request("GET", stream, headers=self.headers)
                segments_uri = self._m3u8_parser(await response.text())
                if segments_uri is None:
                    # That means that stream has ended and we need to stop function
                    logger.debug(f"Стрим закончился. Логин: {login}")
                    break
                segments_uri = segments_uri[:-7:-1]
                for uri in segments_uri:
                    if uri not in segments:
                        await self._download_fragment(segments, uri)
                for uri in list(segments):
                    if uri not in segments_uri:
                        del segments[uri]
                    else:
                        break
                """
                audio = b""
                for segment in segments.values():
                    audio = audio + segment
                await self.__save_audio(str(i), audio)
                i += 1
                """
                await asyncio.sleep(2 - (perf_counter() - start_time))
            except Exception as e:
                logger.exception(e)
                timestamp = time()
                errors = self.information[login]["errors"]
                for error in errors:
                    if timestamp - error > 10:
                        errors.remove(error)
                errors.append(timestamp)
                if len(errors) > 5:
                    logger.error(f"Слишком много ошибок. Выхожу. Логин: {login}")
                    break
        self.information[login] = {"task": None, "segments": {}, "errors": []}

    async def __save_audio(self, filename, audio):
        file = await aiofiles.open(f"{filename}.ts", "wb")
        await file.write(audio)
        await file.close()

    async def _get_song(self, audio):
        song_name = None
        for _ in range(2):
            try:
                shazam_response = await self.shazam.recognize(audio)
                break
            except aiohttp.ClientError as e:
                logger.exception(e)
        else:
            return None
        if len(shazam_response["matches"]) != 0:
            song_name = f"{shazam_response['track']['subtitle']} - {shazam_response['track']['title']}"
        return song_name

    @client.event("recognize")
    async def recognize(self, login: str) -> str:
        try:
            audio = b""
            if login not in self.information:
                self.information[login] = {
                    "task": None,
                    "segments": {},
                    "errors": [],
                }
            if self.information[login]["task"] is None or self.information[login]["task"].done():
                await self.on_online(login)
                await asyncio.sleep(16)
            for num, segment in enumerate(
                self.information[login]["segments"].copy().values()
            ):
                audio = audio + segment
            song = await self._get_song(audio)
            return song or "none"
        except Exception as e:
            logger.exception(e)
            return "error"

    @client.event("online")
    async def on_online(self, login: str):
        if login not in self.information:
            self.information[login] = {
                "task": None,
                "segments": {},
                "errors": [],
            }
        if self.information[login]["task"] is not None:
            if not self.information[login]["task"].done():
                self.information[login]["task"].cancel()
        task = self.loop.create_task(self._thread(login))
        logger.debug(f"Начал _thread для {login}")
        self.information[login]["task"] = task

    async def start(self) -> None:
        self.session = aiohttp.ClientSession()
        self.shazam = Shazam()
        await self.client.connect()

    def run(self) -> None:
        try:
            self.loop.create_task(self.start())
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    recognizer = Recognizer()
    recognizer.run()