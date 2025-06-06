import os, json, requests

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-your_deepseek_api_key")
if not DEEPSEEK_API_KEY:
    print("⚠️ 缺少 DEEPSEEK_API_KEY")
    exit(1)

url = "https://api.deepseek.com"
headers = {
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "deepseek-r1-qwen3-8b",
    "prompt": "请用一句话概述什么是 Django？",
    "max_tokens": 30,
    "temperature": 0.7,
    "top_p": 0.9
}

r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
print("HTTP Status:", r.status_code)
try:
    print("Response:", json.dumps(r.json(), ensure_ascii=False, indent=2))
except:
    print("无法解析 JSON：", r.text)
