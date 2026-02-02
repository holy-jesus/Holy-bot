import time
import os
import secrets

from sqlalchemy import select
from aiohttp import ClientSession
from twitchio import Client as TwitchClient
from twitchio.authentication import OAuth, UserTokenPayload, RefreshTokenPayload
from twitchio.exceptions import HTTPException
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from holybot_shared.communicator import Client
from holybot_shared.db import TwitchToken, User, factory
from holybot_shared.SharedProto.holybot.api import UserLoggedIn, SimpleResponse

KEY = os.getenv("TOKEN_SECRET")
NONCE_SIZE = 12


client = Client("API")


@client.wrap_class
class TwitchAPI:
    def __init__(self):
        self.session = ClientSession()

        self.client_id = os.getenv("TWITCH_CLIENT_ID")
        self.client_secret = os.getenv("TWITCH_CLIENT_SECRET")

        self.twitch = TwitchClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            bot_id="",
            scopes=[],
            session=self.session,
        )

        self.oauth = OAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            session=self.session,
        )

    # Public methods

    @client.event()
    async def recheck_tokens(self):
        pass

    @client.event()
    async def get_token(self, payload: UserLoggedIn) -> SimpleResponse:
        user = await self._get_user(payload.user_id)
        if not user:
            return SimpleResponse(success=False, message="User not found")

        token = await self.fetch_token(user, payload.code, payload.redirect_uri)
        if not token:
            return SimpleResponse(success=False, message="Failed to fetch token")

        return SimpleResponse(success=True, message="Token fetched successfully")

    # Token methods

    async def fetch_token(
        self, user: User, code: str, redirect_uri: str
    ) -> TwitchToken:
        payload = await self.oauth.user_access_token(code, redirect_uri)
        twitch_token = await self._store_token(user, payload)

    async def refresh_token(self, twitch_token: TwitchToken) -> TwitchToken:
        payload = await self.oauth.refresh_token(
            twitch_token.refresh_token, twitch_token.scopes
        )
        await self._update_token(twitch_token, payload)

    async def revoke_token(self, twitch_token: TwitchToken) -> None:
        token = self.__decrypt_secret(twitch_token.token)
        try:
            await self.oauth.revoke_token(token)
        except HTTPException:
            pass
        await self._delete_token(twitch_token)

    async def validate_token(self, twitch_token: TwitchToken) -> bool:
        token = self.__decrypt_secret(twitch_token.token)
        try:
            await self.oauth.validate_token(token)
            return True
        except HTTPException:
            await self.revoke_token(twitch_token)
            return False

    # Database methods

    async def _get_user(self, user_id: str) -> User | None:
        async with factory() as session:
            return (
                await session.execute(select(User).where(User.id == user_id))
            ).scalar_one_or_none()

    async def _get_token(self, user_id: str) -> TwitchToken | None:
        async with factory() as session:
            twitch_token = (
                await session.execute(
                    select(TwitchToken).where(TwitchToken.user_id == user_id)
                )
            ).scalar_one_or_none()

            if not twitch_token:
                return None

            if twitch_token.expires_at < time.time():
                await self.refresh_token(twitch_token)

            return twitch_token

    async def _store_token(
        self,
        user: User,
        payload: UserTokenPayload,
    ):
        encrypted_token = self.__encrypt_secret(payload.access_token)
        encrypted_refresh_token = self.__encrypt_secret(payload.refresh_token)

        twitch_token = TwitchToken(
            token=encrypted_token,
            refresh_token=encrypted_refresh_token,
            expires_at=payload.expires_in + time.time(),
            scopes=payload.scope,
            user_id=user.id,
            user=user,
        )

        async with factory() as session:
            async with session.begin():
                await session.add(twitch_token)

        return twitch_token

    async def _update_token(
        self, twitch_token: TwitchToken, payload: RefreshTokenPayload
    ):
        twitch_token.token = self.__encrypt_secret(payload.access_token)
        twitch_token.refresh_token = self.__encrypt_secret(payload.refresh_token)
        twitch_token.expires_at = payload.expires_in + time.time()
        twitch_token.scopes = payload.scope

        async with factory() as session:
            async with session.begin():
                await session.update(twitch_token)

    async def _delete_token(self, twitch_token: TwitchToken):
        async with factory() as session:
            async with session.begin():
                await session.delete(twitch_token)

    # Encryption and decryption methods

    def __encrypt_secret(self, secret: str):
        aes = AESGCM(KEY)

        nonce = secrets.token_bytes(NONCE_SIZE)
        encrypted_secret = aes.encrypt(nonce, secret, None)

        return nonce + encrypted_secret

    def __decrypt_secret(self, secret: str):
        aes = AESGCM(KEY)

        nonce = secret[:NONCE_SIZE]
        encrypted_secret = secret[NONCE_SIZE:]

        return aes.decrypt(nonce, encrypted_secret, None)

    async def run(self):
        await client.connect()

    async def stop(self):
        await client.close()
