import os
import uvicorn
import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from python.local_model import LocalModel
import mysql.connector  # 用于 MySQL 数据库访问
from mysql.connector import Error

# 加载环境变量
load_dotenv()
ip = os.getenv("IP")
path = os.getenv("MODEL_PATH")
model = LocalModel(path, "cpu")

# 配置 MySQL 数据库连接
DATABASE_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", "20031224"),
    'database': os.getenv("DB_NAME", "aichat"),
    'port': os.getenv("DB_PORT", 3306)  # 默认端口
}

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 请求模型
class ChatRequest(BaseModel):
    userId: int  # 用户ID
    sessionId: int  # 会话ID
    question: str
    prompt: str = "你是个智能助手"  # 默认值


# FastAPI 实例
app = FastAPI()

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 你的前端地址，如果是其他端口请修改
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS, POST, GET 等
    allow_headers=["*"],  # 允许所有请求头
)


# 获取数据库中的最后五条聊天记录作为上下文
def get_last_five_chats(user_id: str, session_id: str):
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(dictionary=True)  # 使用字典形式返回查询结果
        query = """
        SELECT role, content FROM chat
        WHERE user_id = %s AND session_id = %s ORDER BY id DESC LIMIT 10
        """
        cursor.execute(query, (user_id, session_id))
        rows = cursor.fetchall()
        conn.close()

        # 将查询结果构造成一个上下文消息列表
        context = [{"role": row["role"], "content": row["content"]} for row in rows]

        return context
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# 聊天接口
@app.post("/chatbyqwen3")
async def chat(request: ChatRequest):
    user_id = request.userId
    session_id = request.sessionId
    question = request.question
    prompt = request.prompt
    # 获取最近五条聊天记录作为上下文
    context = get_last_five_chats(user_id, session_id)
    # 创建用户消息
    user_message = {"role": "user", "content": question}
    # 将 prompt 加入到上下文
    system_message = {"role": "system", "content": prompt}
    context.insert(0, system_message)  # 插入到上下文的最前面

    # 将用户消息加入上下文
    context.append(user_message)

    # 使用上下文生成回答
    try:
        answer = model.load_qwe3(ip, context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
