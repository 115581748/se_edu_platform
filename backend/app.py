# -*- coding: utf-8 -*-
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from neo4j import GraphDatabase
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# ———— 1. 加载环境变量 ————
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("请先在 .env 文件或环境变量里设置 DEEPSEEK_API_KEY")

NEO4J_URI  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "your_password")

# ———— 2. 初始化 FastAPI & Neo4j 驱动 & DeepSeek 客户端 ————
app = FastAPI()
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
openai_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

# token 编码 & 上下文管理
MODEL_CONTEXT_TOKENS = 8192
_encoding = tiktoken.get_encoding("cl100k_base")
SYSTEM_PROMPT = "你是一个辅助软件工程教育的智能助手，请结合已学概念回答用户问题。"
SYSTEM_PROMPT_TOKENS = len(_encoding.encode(SYSTEM_PROMPT))

def calc_remaining_tokens(prompt_text: str) -> int:
    prompt_tokens = len(_encoding.encode(prompt_text))
    rem = MODEL_CONTEXT_TOKENS - SYSTEM_PROMPT_TOKENS - prompt_tokens
    return max(1024, rem)

# ———— 3. 请求/响应模型 ————
class GenerateRequest(BaseModel):
    prompt: str
    concept_label: str = "Concept"
    allowed_status: str = "taught"

class GenerateResponse(BaseModel):
    result: str

class LearnRequest(BaseModel):
    concept: str

# ———— 4. 数据库操作 ————
def fetch_allowed_topics(status: str | None):
    """
    拉取所有带有 status 属性的节点；
    status=None 则返回所有存在 status 的节点
    """
    with driver.session() as sess:
        if status:
            cy = "MATCH (n) WHERE n.status = $status RETURN n, labels(n) AS labels"
            res = sess.run(cy, status=status)
        else:
            cy = "MATCH (n) WHERE exists(n.status) RETURN n, labels(n) AS labels"
            res = sess.run(cy)
        topics = []
        for rec in res:
            node = rec["n"]
            props = dict(node._properties)
            props["labels"] = rec["labels"]
            topics.append(props)
        return topics


def mark_as_learned(concept: str, status: str = "learned"):
    """标记指定名称节点的 status 属性为已学"""
    with driver.session() as sess:
        sess.run(
            "MATCH (n {name:$name}) SET n.status=$st", name=concept, st=status
        )

# ———— 5. 图谱数据接口 ————
@app.get("/api/graph-data")
# backend/app.py

@app.get("/api/graph-data")
def get_graph_data(limit: int = 50, status: str | None = None):
    """
    如果传了 status，就只拿 status=xxx 的节点与它们的关系；
    否则拿所有节点关系。
    """
    if status:
        cypher = """
        MATCH (n)-[r]->(m)
        WHERE n.status = $status AND m.status = $status
        RETURN n, r, m
        LIMIT $limit
        """
        params = {"status": status, "limit": limit}
    else:
        cypher = """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT $limit
        """
        params = {"limit": limit}

    with driver.session() as session:
        result = session.run(cypher, **params)
        # ...（同之前的 nodes_map/rels 逻辑）...


# ———— 6. DeepSeek-Reasoner 问答调用 ————
def call_deepseek_chat(prompt_text: str) -> str:
    try:
        resp = openai_client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt_text},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=calc_remaining_tokens(prompt_text),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DeepSeek 调用失败：{e}")
    try:
        return resp.choices[0].message.content
    except:
        raise HTTPException(status_code=500, detail=f"DeepSeek 返回格式异常：{resp}")

# ———— 7. /ai/generate 接口 ————
@app.post("/api/ai/generate", response_model=GenerateResponse)
def ai_generate(req: GenerateRequest):
    topics = fetch_allowed_topics(req.allowed_status)
    if not topics:
        raise HTTPException(status_code=404, detail="未找到任何已标记为 taught 的概念")
    bg = []
    for t in topics:
        name = t.get("name", "<no-name>")
        desc = t.get("description", "")
        st   = t.get("status")
        lbls = t.get("labels", [])
        bg.append(f"● [{lbls[0] if lbls else '?'}] {name}: {desc} (status={st})")
    full_prompt = (
        "请结合下面的已学概念及它们的简介，回答用户提问：\n\n"
        "=== 已学概念及简介 ===\n" + "\n".join(bg) +
        "\n\n=== 用户问题 ===\n" + req.prompt
    )
    return GenerateResponse(result=call_deepseek_chat(full_prompt))

# ———— 8. 管理 & 学习端点 ————
@app.post("/api/admin/tag_missing_status")
def tag_missing_status(default_status: str = "untaught"):
    """
    给所有没有 status 属性的节点统一标记 default_status（=untaught）
    """
    with driver.session() as sess:
        sess.run(
            """
            MATCH (n)
            WHERE n.status IS NULL
            SET n.status = $s
            """,
            s=default_status
        )
    return {"ok": True, "tagged_as": default_status}

@app.get("/api/learning/topics")
def list_topics(status: str):
    """
    ?status=untaught 或 ?status=taught
    """
    with driver.session() as sess:
        result = sess.run(
            """
            MATCH (n)
            WHERE n.status = $status
            RETURN labels(n) AS labels, n.name AS name, n.status AS status
            """,
            status=status
        )
        return [
            {"labels": rec["labels"], "name": rec["name"], "status": rec["status"]}
            for rec in result
        ]

@app.post("/api/learning/mark", status_code=204)
def mark_topic(req: LearnRequest):
    """
    把节点 name=req.concept 的 status 改成 taught
    """
    with driver.session() as sess:
        sess.run(
            """
            MATCH (n {name: $name})
            SET n.status = 'taught'
            """,
            name=req.concept
        )