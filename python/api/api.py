import os
import uvicorn
import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from local_model import LocalModel


from mysql_client import MySQLPool

# 加载环境变量
load_dotenv()
ip = os.getenv("IP")
path = os.getenv("MODEL_PATH")
model = LocalModel(path, "cpu")

# 初始化数据库连接池
db = MySQLPool()

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



@app.get("/addpropmt")
async def root(user_id: int, session_id: int, prompt: str):
    # 向数据库插入 prompt
    db.add_propmt(user_id, session_id, prompt)
    return {"message": "Prompt added successfully"}


# 聊天接口
@app.post("/chatbyqwen3")
async def chat(request: ChatRequest):
    user_id = request.userId
    session_id = request.sessionId
    question = request.question
    prompt = request.prompt
    # 获取最近五条聊天记录作为上下文
    context = db.get_last_five_chats(user_id, session_id)
    # 创建用户消息
    user_message = {"role": "user", "content": question}
    # 将 prompt 加入到上下文
    system_message = {"role": "system", "content": prompt}
    context.insert(0, system_message)  # 插入到上下文的最前面

    # 将用户消息加入上下文
    context.append(user_message)

    # 使用上下文生成回答
    try:
        # answer = model.load_qwe3(ip, context)
        answer = model.load_tongyi(context)
        if len(context)<4:
            system_message={"role": "system", "content": "请我帮你总结一下刚才的问答内容，生成一个标题,不要超过10个字。例如：AI助手友好问候并提供帮助"}
             # 插入到上下文的最前面
            total=f"用户问题：{question}\nAI回答：{answer}"+"帮我总结一下以上内容"
            summary = model.load_tongyi([system_message,{"role": "user", "content": total}])
        else:
            summary=None
        return {"answer": answer, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
