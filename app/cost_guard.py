import datetime
import redis.asyncio as redis
from fastapi import HTTPException, status
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def check_budget(user_id: str) -> None:
    current_month = datetime.datetime.now().strftime("%Y-%m")
    redis_key = f"budget:{user_id}:{current_month}"
    
    try:
        current_spending = await redis_client.get(redis_key)
        current_spending = float(current_spending) if current_spending else 0.0
        
        if current_spending >= settings.monthly_budget_limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Tài khoản đã vượt giới hạn ngân sách tháng."
            )
    except Exception:
        pass # Fail-open

async def add_cost(user_id: str, cost: float) -> None:
    current_month = datetime.datetime.now().strftime("%Y-%m")
    redis_key = f"budget:{user_id}:{current_month}"
    try:
        await redis_client.incrbyfloat(redis_key, cost)
        await redis_client.expire(redis_key, 2764800) # 32 ngày
    except redis.RedisError:
        pass