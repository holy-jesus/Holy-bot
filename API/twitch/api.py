from twitchio import Client


class TwitchAPI:
    def __init__(self):
        self.client = Client(TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET)

    def get_user(self, username: str):
        pass
