from twitchapi import TwitchApi
from dotenv import load_dotenv
import os

load_dotenv(".env")


TwitchApi(
    client_id=os.getenv("app_id"),
    secret=os.getenv("app_secret"),
).start()
