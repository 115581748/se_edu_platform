import os
import json
import requests

# 1. 把你的 Hugging Face API Token 写在这里，或者用 os.getenv("HF_TOKEN") 读取环境变量
HF_TOKEN = os.getenv("HF_TOKEN", "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") 

API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "inputs": "写一个线程安全的单例模式示例（Java）",
    "parameters": {
        "max_new_tokens": 128,
        "do_sample": True,
        "top_p": 0.9,
        "temperature": 0.7
    }
}

resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
print("Status Code:", resp.status_code)
print("Response JSON:", resp.json())
