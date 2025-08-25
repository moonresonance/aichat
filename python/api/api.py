import os

import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from python.local_model import LocalModel

load_dotenv()
ip = os.getenv("IP")
path=os.getenv("MODEL_PATH")
model=LocalModel(path,"cpu")



class ChatRequest(BaseModel):
    question: str
    prompt: str


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 你的前端地址，如果是其他端口请修改
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS, POST, GET 等
    allow_headers=["*"],  # 允许所有请求头
)

@app.post("/chatbyqwen3")
async def chat(request: ChatRequest):
    question=request.question
    prompt=request.prompt
    if prompt is None:
        prompt="你是个智能助手"
    answer=model.load_qwe3(ip,prompt,question)
    return {"answer":answer}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)







