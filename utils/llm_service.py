from openai import AsyncOpenAI, OpenAIError
from typing import List, Dict, Tuple
from app.config import settings

# Khởi tạo client OpenAI
client = AsyncOpenAI(api_key=settings.LLM_API_KEY)

async def call_llm(history: List[Dict[str, str]], question: str, context: str = "") -> Tuple[str, float]:
    """
    Gọi LLM thực tế. Nếu thất bại, tự động chuyển sang chế độ Mock/Fallback.
    """
    # 1. Chuẩn bị Prompt
    SYSTEM_PROMPT = {
        "role": "system",
        "content": (
            "Bạn là một trợ lý AI thông minh. Nhiệm vụ của bạn là trả lời câu hỏi của người dùng "
            "DỰA TRÊN NGỮ CẢNH ĐƯỢC CUNG CẤP dưới đây.\n\n"
            "QUY TẮC NGHIÊM NGẶT:\n"
            "1. CHỈ sử dụng thông tin từ tài liệu ngữ cảnh.\n"
            "2. Nếu tài liệu không chứa thông tin để trả lời, hãy nói: 'Tôi không tìm thấy thông tin này trong tài liệu.' Không tự bịa ra câu trả lời.\n"
            "3. Trả lời súc tích, rõ ràng.\n\n"
            f"TÀI LIỆU NGỮ CẢNH:\n{context}"
        )
    }

    messages = [SYSTEM_PROMPT] + history + [{"role": "user", "content": question}]
    
    # 2. Gọi API trong khối try-except để bắt lỗi
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=500,
            # Tùy chọn timeout để không bắt user đợi quá lâu nếu mạng lag
            timeout=10.0 
        )
        
        answer_content = response.choices[0].message.content
        usage = response.usage
        
        # Tính phí (gpt-4o-mini)
        prompt_cost = (usage.prompt_tokens / 1_000_000) * 0.150
        completion_cost = (usage.completion_tokens / 1_000_000) * 0.600
        total_cost = prompt_cost + completion_cost
        
        return answer_content, total_cost

    except OpenAIError as e:
        # Bắt các lỗi cụ thể từ OpenAI (RateLimit, APIConnectionError, AuthenticationError...)
        print(f"[CẢNH BÁO] Lỗi OpenAI API: {e}")
        return _mock_fallback_response(question), 0.0
        
    except Exception as e:
        # Bắt các lỗi hệ thống khác không lường trước được
        print(f"[LỖI NGHIÊM TRỌNG] Lỗi hệ thống khi gọi LLM: {e}")
        return _mock_fallback_response(question), 0.0


# --- Hàm Tiện ích (Helper) ---

def _mock_fallback_response(question: str) -> str:
    """
    Hàm sinh câu trả lời giả lập khi hệ thống thật gặp sự cố.
    """
    # Bạn có thể làm cho mock response thông minh hơn một chút (ví dụ: dùng regex để nhận diện câu chào hỏi cơ bản)
    # Nhưng ở mức cơ bản, chỉ cần trả về thông báo lỗi lịch sự là đủ.
    
    fallback_message = (
        "🤖 **[Chế độ Ngoại tuyến]**\n\n"
        "Hiện tại đường truyền đến hệ thống AI đang gặp sự cố gián đoạn. "
        "Hệ thống đã ghi nhận lại câu hỏi của bạn:\n"
        f"> *\"{question}\"*\n\n"
        "Vui lòng thử lại sau ít phút. Xin lỗi bạn vì sự bất tiện này!"
    )
    
    return fallback_message