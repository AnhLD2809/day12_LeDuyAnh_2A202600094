import time
import uuid
import redis.asyncio as redis
from fastapi import HTTPException, status
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)
MAX_REQUESTS = 10
WINDOW_SECONDS = 60

async def check_rate_limit(user_id: str) -> None:
    redis_key = f"rate_limit:{user_id}"
    current_time = time.time()
    window_start = current_time - WINDOW_SECONDS

    async with redis_client.pipeline(transaction=True) as pipe:
        try:
            pipe.zremrangebyscore(redis_key, 0, window_start)
            pipe.zcard(redis_key)
            unique_member = f"{current_time}-{uuid.uuid4()}"
            pipe.zadd(redis_key, {unique_member: current_time})
            pipe.expire(redis_key, WINDOW_SECONDS)
            
            results = await pipe.execute()
            request_count = results[1]
            
            if request_count >= MAX_REQUESTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau."
                )
        except redis.RedisError:
            pass # Fail-open