import redis.asyncio as asyncio
import json


async def get_redis_server():
    return await asyncio.from_url(
        "redis://localhost:6379",
        encoding = "utf-8",
        decode_responses =True
    )

"""function to set cache data"""
async def cache_set(key:str, value, expire=120):
    redis = await get_redis_server()
    await redis.set(key, json.dumps(value), ex=expire)
    await redis.close()


"""retrieve cache data from redis server"""

async def cache_get(key:str):
    redis = await get_redis_server()
    data = await redis.get(key)
    await redis.close()
    
    return json.loads(data) if data else None

"""clear cache"""
async def cache_clear(key:str):
   redis = await get_redis_server()
   await redis.delete(key)
   await redis.close()


"""delete cache according to pattern"""
async def cache_clear_pattern(pattern:str):
   redis = await get_redis_server()
   keys = await redis.get(pattern)

   if keys:
      await redis.delete(keys)
   await redis.close()