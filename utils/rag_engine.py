import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from app.config import settings

# Thư mục lưu trữ index của FAISS để không phải tạo lại mỗi lần chạy
VECTOR_STORE_PATH = "faiss_index"
DATA_PATH = "./data"

# Khởi tạo Vector Store toàn cục
vectorstore = None

def init_vector_store():
    global vectorstore
    
    # Sử dụng model embedding rẻ và xịn nhất của OpenAI hiện tại
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY, 
        model="text-embedding-3-small"
    )
    
    # Nếu đã có index lưu trên ổ cứng, tải lên để tiết kiệm chi phí API
    if os.path.exists(VECTOR_STORE_PATH):
        print("Đang tải FAISS index từ ổ cứng...")
        vectorstore = FAISS.load_local(
            VECTOR_STORE_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        return

    print("Đang đọc các file .txt và tạo FAISS index mới...")
    # 1. Đọc tất cả file .txt trong thư mục data/ (hỗ trợ utf-8 cho tiếng Việt)
    loader = DirectoryLoader(
        DATA_PATH, 
        glob="*.txt", 
        loader_cls=TextLoader, 
        loader_kwargs={'autodetect_encoding': True}
    )
    docs = loader.load()
    
    # 2. Cắt nhỏ văn bản (Chunking) để nhét vừa ngữ cảnh LLM
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,   # Mỗi đoạn khoảng 700 ký tự
        chunk_overlap=100 # Chồng lấn 100 ký tự để không mất ý giữa 2 đoạn
    )
    splits = text_splitter.split_documents(docs)
    
    # 3. Tạo Vector Database và lưu xuống ổ cứng
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(VECTOR_STORE_PATH)
    print("Đã tạo và lưu FAISS index thành công!")

def retrieve_context(query: str, k: int = 3) -> str:
    """
    Tìm kiếm k đoạn văn bản liên quan nhất đến câu hỏi.
    """
    if not vectorstore:
        raise ValueError("Vector store chưa được khởi tạo!")
    
    # Lấy 3 đoạn văn bản giống với câu hỏi nhất
    docs = vectorstore.similarity_search(query, k=k)
    
    # Nối chúng lại thành một chuỗi văn bản
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    return context