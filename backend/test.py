from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()  # 读取 .env
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

# 简单测试 deepseek-chat 接口
resp = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user",   "content": "Hello, DeepSeek!"}
    ],
    stream=False
)
print(resp.choices[0].message.content)
