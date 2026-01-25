import valkey.asyncio as valkey


async def ratelimit(key: str, limit: int, period: int, vk: valkey.Valkey):
    current = await vk.incr(key)
    if current == 1:
        await vk.expire(key, period)
    return int(current) >= limit
