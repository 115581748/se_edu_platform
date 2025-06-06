import requests, os, json

HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type":  "application/json"
}
payload = {
    "inputs": "你好，测试一下这段文本能不能生成内容",
    "parameters": { "max_new_tokens": 50, "do_sample": True }
}

resp = requests.post(HF_API_URL, headers=headers, data=json.dumps(payload))
print(resp.status_code, resp.text)
