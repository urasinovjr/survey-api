from redis.asyncio import Redis
import json

redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)

async def cache_get_questions(version_id: int, user_id: int):
    cache_key = f"questions:{version_id}:{user_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

async def cache_set_questions(version_id: int, user_id: int, questions: list):
    cache_key = f"questions:{version_id}:{user_id}"
    await redis.set(cache_key, json.dumps([q.dict() for q in questions]), ex=3600)

async def cache_get_responses(user_id: int, version_id: int):
    cache_key = f"responses:{user_id}:{version_id}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

async def cache_set_responses(user_id: int, version_id: int, responses: list):
    cache_key = f"responses:{user_id}:{version_id}"
    await redis.set(cache_key, json.dumps([r.dict() for r in responses]), ex=3600)