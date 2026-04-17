import json
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, status
from contextlib import asynccontextmanager # THÊM MỚI
from pydantic import BaseModel
from contextlib import asynccontextmanager

from app.config import settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_budget, add_cost
from utils.llm_service import call_llm
from utils.rag_engine import init_vector_store, retrieve_context # THÊM MỚI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Khi bật App (Startup) ---
    print("Application startup: Khởi tạo RAG Index...")
    init_vector_store()
    
    yield # App đang chạy...
    
    # --- Khi tắt App (Nhận tín hiệu SIGTERM / Shutdown) ---
    print("Received SIGTERM. Bắt đầu Graceful Shutdown...")
    # Đóng các kết nối Database/Redis một cách an toàn
    await redis_client.aclose()
    print("Graceful Shutdown hoàn tất!")

app = FastAPI(title="RAG LLM API", version="1.0.0", lifespan=lifespan)
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

class AskRequest(BaseModel):
    user_id: str
    question: str

@app.get("/health", tags=["System"])
async def health():
    """Kiểm tra xem Container có đang sống hay không (Liveness)."""
    return {"status": "ok", "message": "Service is running"}

@app.get("/ready", tags=["System"])
async def ready():
    """Kiểm tra xem App đã kết nối được với các dịch vụ phụ trợ (Redis/Database) chưa (Readiness)."""
    try:
        ping = await redis_client.ping()
        if ping:
            return {"status": "ready", "redis": "connected"}
    except Exception as e:
        # Quan trọng: Nếu lỗi phải trả về 503 Service Unavailable để báo cho hệ thống biết app chưa sẵn sàng
        raise HTTPException(status_code=503, detail="Not ready")

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str

# Gắn decorator trực tiếp vào hàm chứa logic thật
@app.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    # Auth sẽ chặn ở đây, nếu đúng key mới lấy được user_id đi tiếp
    user_id: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget)
):
    redis_key = f"chat_history:{user_id}"
    
    try:
        # 1. RAG: Lấy ngữ cảnh từ 5 file TXT
        context = retrieve_context(request.question)

        # 2. Lấy lịch sử hội thoại
        history_data = await redis_client.get(redis_key)
        history = json.loads(history_data) if history_data else []

        # 3. Gọi LLM (Truyền thêm context)
        llm_response, cost = await call_llm(history, request.question, context)

        # 4. Lưu phí & Lịch sử
        await add_cost(user_id, cost)
        
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": llm_response})
        history = history[-10:] 
        await redis_client.setex(redis_key, 3600, json.dumps(history))

        # Trả về đúng format Pydantic model
        return AskResponse(answer=llm_response)

    except Exception as e:
        print(f"Lỗi: {e}")
        raise HTTPException(status_code=500, detail="Lỗi nội bộ hệ thống.")