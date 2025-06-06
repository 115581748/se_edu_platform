"""
kg_collect_web.py
自动从 Wiki / SO / GitHub 抓取技术信息并写入 Neo4j
----------------------------------------------------
用法:
1. 在 tech_list.txt 填写主体技术 (每行一个) 例:
   Maven
   MySQL
   Redis

2. export / set 环境变量:
   NEO4J_PASS、GITHUB_TOKEN、STACK_API_KEY（可选）

3. python kg_collect_web.py
"""

import os, re, json, time, requests, xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
from github import Github
import wikipediaapi
from neo4j import GraphDatabase
import urllib.parse, random
# ========== Neo4j ==========
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI","bolt://localhost:7687"),
    auth=(os.getenv("NEO4J_USER","neo4j"),
          os.getenv("NEO4J_PASS","your_password"))
)

def norm(s:str)->str: return re.sub(r"[^a-z0-9]","",s.lower())

def merge_tech(tx, name, properties:dict):
    tx.run("""
        MERGE (t:Tech {norm:$norm})
        ON CREATE SET t.name=$name
        SET t += $props
        """, norm=norm(name), name=name, props=properties)

def relate_to_fw(tx, tech_norm, rel="USES", fw="Spring Boot"):
    tx.run("""
        MERGE (fw:Framework {name:$fw})
        MERGE (t:Tech {norm:$tech})
        MERGE (fw)-[:%s]->(t)
        """ % rel, fw=fw, tech=tech_norm)

# ========== 1) Wikipedia ==========
wiki = wikipediaapi.Wikipedia(user_agent="EduKGBot/0.2", language="en")
def wiki_summary(title):
    p = wiki.page(title)
    return p.summary.split("\n")[0] if p.exists() else None

# ========== 2) StackOverflow ==========
BASE_SO="https://api.stackexchange.com/2.3"

def so_top_tags(tag="spring-boot", top_n=20) -> list[str]:
    """安全调用 Stack Overflow，失败时返回空列表而非抛异常"""
    params = {"site": "stackoverflow", "pagesize": top_n}
    key = os.getenv("STACK_API_KEY")
    if key:
        params["key"] = key

    url = f"{BASE_SO}/tags/{urllib.parse.quote(tag)}/related"

    try:
        r = requests.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()                       # 非 2xx 抛异常
        data = r.json()                            # 解析 JSON
        return [i["name"] for i in data.get("items", [])]
    except Exception as e:
        # 输出告警但不中断后续循环
        print(f"[warn] SO API for '{tag}' failed → {e}")
        # 随机退避 1-3 秒，防止短时间再次触发限流
        time.sleep(random.uniform(1, 3))
        return []
# ========== 3) GitHub ==========
def github_stats(name):
    """返回 stars/forks 最大的 repo 作为代表"""
    token=os.getenv("GITHUB_TOKEN")
    if not token: return {}
    g=Github(token); res=g.search_repositories(query=name, sort="stars")[:1]
    if not res: return {}
    repo=res[0]
    return {"gh_repo":repo.full_name,
            "gh_stars":repo.stargazers_count,
            "gh_url":repo.html_url}

# ========== 4) 简易官网搜索 (可选) ==========



+
def first_google_result(query):
    try:
        html=requests.get(f"https://duckduckgo.com/html/?q={query}",
                          headers={"User-Agent":"Mozilla/5.0"},timeout=15).text
        soup=BeautifulSoup(html,"html.parser")
        a=soup.select_one(".result__a")
        return a["href"] if a else None
    except: return None

# ========== 主入口 ==========
if __name__=="__main__":
    techs=[line.strip() for line in Path("tech_list.txt").read_text().splitlines() if line.strip()]
    print("▶ Collecting for", techs)

    with driver.session() as sess:
        for tech in techs:
            props={}
            # ① Wiki
            summary=wiki_summary(tech);   summary and props.setdefault("summary",summary)
            # ② SO
            so_rel=so_top_tags(tech.replace(" ","-").lower()); props["so_tags"]=json.dumps(so_rel)
            # ③ GitHub
            props.update(github_stats(tech))
            # ④ 官网
            props["homepage"]=first_google_result(f"{tech} official site")

            sess.execute_write(merge_tech, tech, props)
            sess.execute_write(relate_to_fw, norm(tech))
            print(f"  [+] {tech} written with {len(props)} props")

    print("✔ Done!")
