# LLM API Agent

## Cài đặt cục bộ (Local)
1. Tạo môi trường ảo: `python -m venv venv`
2. Kích hoạt môi trường và cài thư viện: `pip install -r requirements.txt`
3. Copy file `.env.example` thành `.env` và điền thông tin.
4. Chạy app: `uvicorn app.main:app --reload`

## Chạy với Docker
Lệnh: `docker-compose up --build -d`