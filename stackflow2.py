# filename: so_crawler_to_neo4j.py
import os, re, time, html, requests
from bs4 import BeautifulSoup
from neo4j import GraphDatabase

# ==== 配置 ====
STACK_KEY  = os.getenv("STACK_API_KEY")     # 可留空
NEO4J_URI  = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "your_password")
MAX_PER_CLASS = 2      # 每个类抓多少问答
CLASS_LIMIT   = 1000     # 最多处理多少个类节点

driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
BASE_URL = "https://api.stackexchange.com/2.3"
CODE_RE  = re.compile(r"<pre><code>(.*?)</code></pre>", re.S)

def se_get(path, **params):
    params.update({"site":"stackoverflow", "filter":"!9_bDE(fI5"})
    if STACK_KEY: params["key"] = STACK_KEY
    for _ in range(3):                                # 简易重试
        try:
            r = requests.get(f"{BASE_URL}/{path}", params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print("[warn]", e, "retrying…")
            time.sleep(2)
    return {"items":[]}

def extract_code(html_body):
    return [html.unescape(c.strip()) for c in CODE_RE.findall(html_body)]

def write_graph(tx, cls_name, q, ans, codes):
    tx.run("""
        MERGE (c:Class {name:$cls})
        MERGE (q:SOQuestion {id:$qid})
          ON CREATE SET q.title=$title, q.link=$link, q.score=$qscore
        MERGE (a:SOAnswer {id:$aid})
          ON CREATE SET a.body=$body, a.score=$ascore
        MERGE (c)-[:HAS_SO]->(q)
        MERGE (q)-[:HAS_ANSWER]->(a)
        """, cls=cls_name,
             qid=q["question_id"], title=q["title"], link=q["link"], qscore=q["score"],
             aid=ans["answer_id"], body=BeautifulSoup(ans["body"],"html.parser").get_text(" ")[:8000],
             ascore=ans["score"])

    for idx, code in enumerate(codes):
        tx.run("""
            MERGE (cb:CodeBlock {id:$cid})
              ON CREATE SET cb.content=$content
            WITH cb
            MATCH (a:SOAnswer {id:$aid})
            MERGE (a)-[:HAS_CODE]->(cb)
            """, cid=f'{ans["answer_id"]}_{idx}',
                 content=code[:4000], aid=ans["answer_id"])

def main():
    with driver.session() as sess:
        cls_names = sess.run("MATCH (c:Class) RETURN c.name AS n LIMIT $lim",
                             lim=CLASS_LIMIT).value()

    fetched = 0
    with driver.session() as sess:
        for cname in cls_names:
            print(f"\n### 处理类: {cname}")
            # 1) 搜索该类相关的高票问题
            qs = se_get("search/advanced",
                        intitle=cname,
                        accepted="True",
                        sort="votes", order="desc",
                        tagged="java", pagesize=MAX_PER_CLASS)["items"]

            for q in qs:
                aid = q.get("accepted_answer_id")
                if not aid: continue
                ans = se_get(f"answers/{aid}")["items"][0]
                codes = extract_code(ans["body"])

                sess.execute_write(write_graph, cname, q, ans, codes)
                fetched += 1
                print(f" [+] Q{q['question_id']} → A{aid}  codes:{len(codes)}")

            time.sleep(1)   # 简单限速

    print(f"\nDone! 共写入 {fetched} 条问答。")

if __name__ == "__main__":
    main()
