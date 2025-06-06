# filename: stackoverflow_to_neo4j.py
import os, json, time, html, re
import requests
from bs4 import BeautifulSoup
from neo4j import GraphDatabase
import requests, time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== 配置 =====
TAGS          = ["spring-boot", "java"]      # 想换其他标签自行调整
PAGES         = 2                            # 每页 100 条，乘出来≈200问
STACK_KEY     = os.getenv("STACK_API_KEY")   # 可为空
NEO4J_URI     = "bolt://localhost:7687"
NEO4J_AUTH    = ("neo4j", "your_password")

driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

# ===== 工具函数 =====
BASE_URL = "https://api.stackexchange.com/2.3"
STACK_KEY = os.getenv("STACK_API_KEY")

# ① 建立带重试策略的会话
retry_strategy = Retry(
    total       = 5,              # 最多重试 5 次
    backoff_factor = 1.5,         # 1.5, 3, 4.5, ...
    status_forcelist = [502, 503, 504, 429],
    allowed_methods  = ["GET"],
)
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry_strategy))


def se_get(path, **params):
    """包装 Stack Exchange API GET，并自动重试 SSL/连接异常"""
    params.update({
        "site": "stackoverflow",
        "filter": "!9_bDE(fI5",   # 返回 body_markdown
    })
    if STACK_KEY:
        params["key"] = STACK_KEY

    url = f"{BASE_URL}/{path}"
    for attempt in range(6):        # 额外捕获 SSLError
        try:
            r = session.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.SSLError as e:
            if attempt == 5:
                raise
            wait = 2 ** attempt
            print(f"[SSL] {e} -> retry in {wait}s")
            time.sleep(wait)


CODE_RE = re.compile(r"<pre><code>(.*?)</code></pre>", re.S)

def extract_code(html_body):
    return [html.unescape(code.strip()) for code in CODE_RE.findall(html_body)]

# ===== Neo4j 写入 =====

def write_so(session, q, ans, code_blocks):
    session.run(
        """
        MERGE (q:SOQuestion {id:$qid})
        ON CREATE SET q.title=$title, q.link=$link, q.score=$qscore, q.tags=$tags
        WITH q
        MERGE (a:SOAnswer {id:$aid})
        ON CREATE SET a.body=$abody, a.score=$ascore
        MERGE (q)-[:HAS_ANSWER]->(a)
        """,
        qid=q["question_id"], title=q["title"], link=q["link"],
        qscore=q["score"], tags=q["tags"],
        aid=ans["answer_id"],
        # 改这里 —— 用 HTML body 或转纯文本
        abody=BeautifulSoup(ans["body"], "html.parser").get_text(" ")[:8000],
        ascore=ans["score"]
    )
# ===== 主流程 =====
def main():
    fetched = 0
    with driver.session() as sess:
        for page in range(1, PAGES + 1):
            # 1. 搜索高分问题
            qs = se_get("search/advanced",
                        tagged=";".join(TAGS),
                        sort="votes", order="desc",
                        page=page)

            for q in qs["items"]:
                if not q.get("accepted_answer_id"):
                    continue  # 只处理有采纳答案的问题

                # 2. 拉取该答案
                ans_id = q["accepted_answer_id"]
                ans = se_get(f"answers/{ans_id}", filter="withbody")["items"][0]

                # 3. 提取代码块
                code_blocks = extract_code(ans["body"])

                # 4. 写入图数据库
                write_so(sess, q, ans, code_blocks)
                fetched += 1
                print(f"[+] Q{q['question_id']} -> A{ans_id}  (codes:{len(code_blocks)})")

            print(f"Page {page} done, sleeping 1s to respect rate-limit")
            time.sleep(1)  # 简单限速

    print(f"\n共写入 {fetched} 个问答节点。")

if __name__ == "__main__":
    main()
