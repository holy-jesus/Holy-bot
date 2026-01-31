import valkey.asyncio as valkey


async def ratelimit(key: str, limit: int, period: int, vk: valkey.Valkey) -> bool:
    """
    True если лимит превышен
    False если лимит не превышен
    """
    current = await vk.incr(key)
    if current == 1:
        await vk.expire(key, period)
    return int(current) >= limit
