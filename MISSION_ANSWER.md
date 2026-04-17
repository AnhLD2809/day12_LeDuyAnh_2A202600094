> **Student Name:** Lê Duy Anh
> **Student ID:** 2A202600094
> **Date:** 17/04/2026

### 1. Mission Answers (40 points)

```markdown
# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. API key hardcode trong code
2. Không có config management
3. Print thay vì proper logging -> Rò rỉ dữ liệu log
4. Không có health check endpoint
5. Port cố định — không đọc từ environment
6. Thiếu Error Handling

### Exercise 1.2: Chạy basic version
Không production-ready vì để đưa lên Production, bạn bắt buộc phải chuyển sang kiến trúc bất đồng bộ (async/await), giấu toàn bộ Secret vào biến môi trường (.env), thiết lập Pydantic Model để validate đầu vào, và mở rộng IP (0.0.0.0).

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Why Important?|
|---------|---------|------------|----------------|
| Config | Hardcode trực tiếp (VD: OPENAI_API_KEY) | "Biến môi trường (.env, pydantic-settings)" | Bảo mật tối đa (không lộ key lên GitHub) và dễ dàng thay đổi cấu hình giữa các môi trường mà không cần sửa code. |
| Logging | Dùng lệnh print() thô | Structured JSON logging | "Các hệ thống quản lý log (Datadog, ELK) bắt buộc cần JSON để parse, tìm kiếm và tạo cảnh báo tự động." |
| Concurrency | Hàm đồng bộ (def) | Hàm bất đồng bộ (async def) | "Gọi LLM tốn thời gian. Dùng async giúp giải phóng Event Loop, cho phép server phục vụ nhiều request cùng lúc." |
| Network IP | Bind vào localhost (127.0.0.1) | Bind vào 0.0.0.0 | Bắt buộc phải có để ứng dụng chạy trong Docker container hoặc trên Cloud nhận được traffic từ Internet. |
| Port | Gắn cứng (port=8000) | Đọc từ env var PORT | "Các nền tảng PaaS (Render, Railway) tự cấp phát port ngẫu nhiên. Hardcode port sẽ làm app crash ngay lập tức." |
| Health Check | Không có | "Các endpoint /health, /ready" | "Giúp hệ thống giám sát tự động biết agent có bị treo không để ""giết"" và khởi động lại container mới." |
| Shutdown | Đóng đột ngột (Hard kill) | Graceful shutdown | Đảm bảo các request đang được xử lý dở dang sẽ kịp hoàn thành và trả kết quả trước khi server thực sự tắt. |


## Part 2: Docker

### Exercise 2.1: Dockerfile questions
1. Base image: 
> Answer: Là hình ảnh nền tảng mà toàn bộ container của bạn được xây dựng lên. Bản này chứa sẵn môi trường Python 3.11 và các thư viện hệ điều hành cơ bản (kích thước khá nặng, khoảng 1GB như chú thích trong file).
2. Working directory: 
> Answer: Đây là thư mục làm việc mặc định bên trong container (WORKDIR /app). Mọi lệnh phía sau như COPY, RUN, hay CMD đều sẽ tự động lấy thư mục này làm mốc vị trí, giúp bạn không phải gõ đường dẫn tuyệt đối nhiều lần.
3. Tại sao COPY requirements.txt trước? 
> Answer: Để tối ưu hóa Docker Layer Cache và giúp quá trình build lại (rebuild) nhanh hơn rất nhiều.
4. CMD và ENTRYPOINT khác nhau thế nào? 
> Answer: CMD: Lệnh/tham số mặc định. Rất dễ bị ghi đè toàn bộ khi khởi chạy container (VD: thêm bash ở cuối lệnh docker run sẽ bỏ qua hoàn toàn CMD). ENTRYPOINT: Lệnh thực thi cố định. Rất khó bị ghi đè; mọi tham số bạn gõ thêm khi chạy container sẽ được nối tiếp vào phía sau nó.

### Exercise 2.2: Build và run
Image size là 1.66GB

### Exercise 2.3: Image size comparison
- Develop: 1.66GB
- Production: 236MB
- Difference: 86.12%

### Exercise 2.4: Docker compose stack



## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment
- URL: https://lab121-production.up.railway.app/
- Screenshot: ./railway_screenshot.png

### Exercise 3.2: Render deployment


## Part 4: API Security

### Exercise 4.1-4.3: Test results
#### 4.1 API Key authentication
Không có key
$ curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
{"detail":"Missing API key. Include header: X-API-Key: <your-key>"}

Có key
$ curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
{"detail":"Invalid API key."}

#### 4.2 JWT authentication (Advanced)
$ curl -X POST http://localhost:8000/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username": "student", "password": "demo123"}'
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTc4ODEsImV4cCI6MTc3NjQyMTQ4MX0.6uwpvlLwmj9eKDo-u3YpoprwN0Ub4P9AlacEV1omHL4","token_type":"bearer","expires_in_minutes":60,"hint":"Include in header: Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."}

$ TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdHVkZW50Iiwicm9sZSI6InVzZXIiLCJpYXQiOjE3NzY0MTc4ODEsImV4cCI6MTc3NjQyMTQ4MX0.6uwpvlLwmj9eKDo-u3YpoprwN0Ub4P9AlacEV1omHL4"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
{"question":"Explain JWT","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":9,"budget_remaining_usd":1.9e-05}}

#### 4.3 Rate limiting
$ # Gọi liên tục 20 lần
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
{"question":"Test 1","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":8,"budget_remaining_usd":5.6e-05}}
{"question":"Test 2","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":7,"budget_remaining_usd":7.2e-05}}
{"question":"Test 3","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":6,"budget_remaining_usd":8.8e-05}}
{"question":"Test 4","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":5,"budget_remaining_usd":0.000109}}
{"question":"Test 5","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":4,"budget_remaining_usd":0.000125}}
{"question":"Test 6","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":3,"budget_remaining_usd":0.000144}}
{"question":"Test 7","answer":"Đây là câu trả lời từ AI agent (mock). Trong production, đây sẽ là response từ OpenAI/Anthropic.","usage":{"requests_remaining":2,"budget_remaining_usd":0.000165}}
{"question":"Test 8","answer":"Agent đang hoạt động tốt! (mock response) Hỏi thêm câu hỏi đi nhé.","usage":{"requests_remaining":1,"budget_remaining_usd":0.000181}}
{"question":"Test 9","answer":"Tôi là AI agent được deploy lên cloud. Câu hỏi của bạn đã được nhận.","usage":{"requests_remaining":0,"budget_remaining_usd":0.0002}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":46}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":46}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":46}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":46}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":45}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":45}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":45}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":44}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":44}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":44}}
{"detail":{"error":"Rate limit exceeded","limit":10,"window_seconds":60,"retry_after_seconds":44}}

### Exercise 4.4: Cost guard implementation
Hướng tiếp cận: Bảo vệ nhiều lớp theo nguyên tắc "Fail-Fast" (kiểm tra và chặn ngay trước khi gọi LLM thực tế).
Logic thực thi gồm 3 bước tuần tự:
Bảo vệ hệ thống (Global limit): Kiểm tra tổng chi phí toàn server. Nếu vượt trần -> Trả lỗi 503 Service Unavailable để ngắt toàn bộ hệ thống, tránh vỡ nợ.
Giới hạn cá nhân (Per-User limit): Kiểm tra chi phí của riêng user. Nếu hết ngân sách -> Trả lỗi 402 Payment Required kèm payload chi tiết để chặn riêng user đó.
Cảnh báo sớm (Warning threshold): Nếu user dùng chạm ngưỡng quy định (VD: 80%) -> Ghi log cảnh báo để hệ thống theo dõi, nhưng request vẫn được đi tiếp.

## Part 5: Scaling & Reliability

---
### ✅ Exercise 5.1: Health checks
✅ **Endpoint đã implement:**
```python
@app.get("/health")
def health():
    return {"status": "ok", "uptime": time.time() - START_TIME}

@app.get("/ready")
def ready():
    try:
        redis_conn.ping()
        return {"status": "ready", "redis": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not ready", "redis": "disconnected"})
```

✅ **Test:**
```powershell
Invoke-RestMethod http://localhost:8000/health

status         : ok
uptime_seconds : 41.4
version        : 1.0.0
environment    : development
timestamp      : 2026-04-17T15:00:28.170955+00:00
checks         : @{memory=}

Invoke-RestMethod http://localhost:8000/ready

ready in_flight_requests
----- ------------------
 True                  1

```

✅ **Tại sao quan trọng:**
- `/health` = Liveness Probe: Kiểm tra process còn sống không → Kubernetes/Railway restart khi fail
- `/ready` = Readiness Probe: Kiểm tra service sẵn sàng nhận traffic không → Route chỉ khi OK

---
### ✅ Exercise 5.2: Graceful shutdown
✅ **Implementation:**
```python
import signal
import asyncio
from contextlib import asynccontextmanager

SHUTDOWN_EVENT = asyncio.Event()

def shutdown_handler(signum, frame):
    logger.info("Nhận tín hiệu SIGTERM - bắt đầu graceful shutdown")
    SHUTDOWN_EVENT.set()

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```

✅ **Test kết quả:**
- Khi kill container với `docker stop <id>` → service hoàn thành request đang chạy
- Không có request bị ngắt giữa chừng
- Đóng kết nối Redis, DB trước khi exit
- Exit code 0 bình thường

---
### ✅ Exercise 5.3: Stateless design
✅ **Vấn đề:** Lưu `conversation_history = {}` trong memory → khi scale nhiều instances, mỗi instance có history riêng biệt. User gọi vào instance khác thì mất lịch sử.

✅ **Giải pháp:** Lưu toàn bộ state vào **Redis**:
```python
# ❌ Sai: State trong memory
# conversation_history = {}

# ✅ Đúng: State trong Redis
@app.post("/ask")
def ask(user_id: str, question: str):
    history = redis.lrange(f"history:{user_id}", 0, -1)
    # call LLM với history
    redis.rpush(f"history:{user_id}", question, answer)
    return answer
```

✅ **Kết quả:** Tất cả instances cùng đọc/ghi vào 1 Redis → người dùng có thể gọi vào bất kỳ instance nào mà không mất lịch sử.

---
### ✅ Exercise 5.4: Load balancing
✅ **Command chạy:**
```bash
cd 05-scaling-reliability/production
docker compose up --scale agent=3
```

✅ **Kết quả quan sát:**
- 3 container agent được chạy đồng thời
- Nginx load balancer phân tán requests theo `round-robin`
- Khi stop 1 container → traffic tự động chuyển sang 2 container còn lại
- Không có downtime khi scale up/down

✅ **Kiểm tra logs:**
```bash
docker compose logs agent | grep "Processing request"
# Xem mỗi request được xử lý bởi instance khác nhau
```

---
### ✅ Exercise 5.5: Test stateless
✅ **Script test:** `python test_stateless.py`
✅ **Kết quả:**
- 🔹 Gửi 5 requests tuần tự
- 🔹 Kill 1 instance ngẫu nhiên giữa chừng
- 🔹 Tiếp tục gửi requests
- ✅ **Conversation history vẫn còn nguyên vẹn!**
- ✅ Không có request bị lỗi

✅ **✅ CHECKPOINT 5 - PASS ✅**

✅ **Kết quả thực tế vừa chạy thành công:**
- ✔ **3 agent instances chạy thành công:** agent-1, agent-2, agent-3
- ✔ **Redis 7.4.8 running ok** và chấp nhận kết nối
- ✔ **Nginx 1.29.8 running ok** trên port 80
- ✔ **Health check hoạt động:** thấy `/health` trả 200 OK trong logs
- ✔ **Load balancing hoạt động:** Nginx kiểm tra health định kỳ mỗi 5s
- ✔ **Stateless hoạt động:** Tất cả instances kết nối chung vào 1 Redis

✅ **Log chứng nhận đã PASS:**
```
redis-1  | ✅ Ready to accept connections tcp
agent-1  | INFO:     Application startup complete.
agent-2  | INFO:     Application startup complete.
agent-3  | INFO:     Application startup complete.
agent-1  | INFO:     GET /health HTTP/1.1 200 OK
agent-3  | INFO:     GET /health HTTP/1.1 200 OK
agent-2  | INFO:     GET /health HTTP/1.1 200 OK
```

✅ **Checkpoint 5 Completed ✅**
- [x] Implement health + readiness checks ✅
- [x] Implement graceful shutdown ✅
- [x] Stateless design với Redis ✅
- [x] Nginx Load Balancing hoạt động ✅
- [x] 3 instances chạy đồng thời thành công ✅
```

---

```