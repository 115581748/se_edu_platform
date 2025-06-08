# -*- coding: utf-8 -*-
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from dotenv import load_dotenv
from openai import OpenAI  # DeepSeek API 兼容 OpenAI SDK

# ———— 1. 加载环境变量 ————
load_dotenv()  # 从 backend/.env 里读取

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("请先在 .env 文件或环境变量里设置 DEEPSEEK_API_KEY")

NEO4J_URI  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "your_password")

# ———— 2. 初始化 FastAPI & Neo4j 驱动 & DeepSeek 客户端 ————
app = FastAPI()
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# 使用 OpenAI SDK 调用 DeepSeek API（兼容 OpenAI 格式）
# base_url 可以写 "https://api.deepseek.com/v1" 或者直接 "https://api.deepseek.com"
openai_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# ———— 3. 请求/响应模型 ————
class GenerateRequest(BaseModel):
    prompt: str
    concept_label: str = "Concept"
    allowed_status: str = "taught"

class GenerateResponse(BaseModel):
    result: str

# ———— 4. 从 Neo4j 拉取“已教学”概念及简介 ————
def fetch_allowed_topics(status: str):
    """
    返回所有带有 status 属性的节点，格式化为 dict：
       [
         {"labels": [...], "name": "...", "status": "...", ...任意其它属性...},
         …
       ]
    """
    with driver.session() as sess:
        result = sess.run(
            """
            MATCH (n)
            WHERE n.status IS NOT NULL AND n.status = $status
            RETURN n, labels(n) AS labels
            """,
            status=status
        )
        topics = []
        for rec in result:
            node = rec["n"]
            props = dict(node)               # { 'name': ..., 'description': ..., 'status': ..., … }
            props["labels"] = rec["labels"]  # 手动加上 labels
            topics.append(props)
        return topics

# ———— 5. 从 Neo4j 拿“图数据” JSON（节点 + 关系）——前端 Neovis/Vis.js 用到 ————
@app.get("/api/graph-data")
def get_graph_data(limit: int = 50):
    """
    返回 JSON 格式：
    {
      "nodes": [{ "id": "...", "labels": [...], "name": "...", ... }, ...],
      "relationships": [{ "id": "...", "type": "...", "source": "...", "target": "...", ... }, ...]
    }
    用户可通过 /api/graph-data?limit=100 请求更多数据
    """
    cypher = """
    MATCH (n:Class)-[r]->(m)
    RETURN n, r, m
    LIMIT $limit
    """
    with driver.session() as session:
        result = session.run(cypher, limit=limit)

        nodes_map = {}
        rels = []
        for record in result:
            n = record["n"]
            m = record["m"]
            r = record["r"]
            # 把节点挂到 nodes_map（去重）
            if n.id not in nodes_map:
                nodes_map[n.id] = {
                    "id": str(n.id),
                    "labels": list(n.labels),
                    **n._properties,
                }
            if m.id not in nodes_map:
                nodes_map[m.id] = {
                    "id": str(m.id),
                    "labels": list(m.labels),
                    **m._properties,
                }
            # 组合关系
            rels.append({
                "id": str(r.id),
                "type": r.type,
                "source": str(r.start_node.id),
                "target": str(r.end_node.id),
                **r._properties,
            })

        return {
            "nodes": list(nodes_map.values()),
            "relationships": rels
        }

# ———— 6. 调用 DeepSeek-Reasoner（R1）问答接口 ————
def call_deepseek_chat(prompt_text: str) -> str:
    """
    使用 OpenAI SDK 方式调用 DeepSeek-Reasoner（模型名："deepseek-reasoner"）
    返回生成的回答文本
    """
    try:
        resp = openai_client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": "你是一个辅助软件工程教育的智能助手，请结合已学概念回答用户问题。"},
                {"role": "user",   "content": prompt_text},
            ],
            temperature=0.7,
            top_p=0.9,
            # max_tokens=512,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek 调用失败：{e}")
    
    print(resp)
    # 返回的结构：resp.choices[0].message.content
    try:
        return resp.choices[0].message.content
    except Exception:
        raise HTTPException(status_code=500, detail=f"DeepSeek 返回格式异常：{resp}")

# ———— 7. /ai/generate 接口：先拿已教概念拼背景，再调用模型 ————
@app.post("/api/ai/generate", response_model=GenerateResponse)
def ai_generate(req: GenerateRequest):
    # 1) 从 Neo4j 拉取所有标为 'taught' 的概念
    topics = fetch_allowed_topics(req.allowed_status)
    if not  topics:
        raise HTTPException(status_code=404, detail="未找到任何已标记为 taught 的概念")

    # 举例，把每个 topic 的 name/description/status 拼成一段背景
    background_lines = []
    for topic in topics:
        name   = topic.get("name", "<no-name>")
        desc   = topic.get("description", "")
        status = topic.get("status")
        labels = topic.get("labels", [])
        label0 = labels[0] if labels else "Unknown"
        if desc:
            background_lines.append(f"● [{label0}] {name}:{desc} (status={status})")
        else:
            background_lines.append(f"● [{label0}] {name} (status={status})")
        background_text = "\n".join(background_lines)

    # 3) 构造最终发给模型的 prompt
    full_prompt = (
        "请结合下面的已学概念及它们的简介，回答用户提问：\n\n"
        "=== 已学概念及简介 ===\n"
        f"{background_text}\n\n"
        "=== 用户问题 ===\n"
        f"{req.prompt}\n\n"
        "请基于上述概念及简介给出详细且准确的解答。"
    )

    # 4) 调用 DeepSeek-Reasoner
    answer = call_deepseek_chat(full_prompt)
    return GenerateResponse(result=answer)

# ———— 8. 启动说明 ————
# 保存为 backend/app.py 后，在此目录下执行：
#    uvicorn app:app --reload --host 0.0.0.0 --port 8000
@app.post("/admin/tag_missing_status")
def tag_missing_status(default_status: str = "untaught"):
    """
    给所有没有 status 属性的节点，设置默认 status。
    """
    with driver.session() as sess:
        sess.run(
            """
            MATCH (n)
            WHERE NOT exists(n.status)
            SET n.status = $s
            """,
            s=default_status
        )
    return {"ok": True, "tagged_as": default_status}