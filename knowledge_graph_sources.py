# kg_collect_web.py  — 在线采集并写入 Spring Boot 生态知识图谱
"""
脚本功能：
1. 批量读取待补全技术列表
2. 从 Wikipedia、Stack Overflow、GitHub、DuckDuckGo 抓取技术属性
3. 将节点属性和关系写入 Neo4j，支持自定义属性字段

使用方法：
1. pip install neo4j requests beautifulsoup4 wikipedia-api PyGithub
2. 设置环境变量：
   - NEO4J_URI (可选，默认 bolt://localhost:7687)
   - NEO4J_USER (可选，默认 neo4j)
   - NEO4J_PASS (必需)
   - GITHUB_TOKEN (可选，GitHub API Token)
   - STACK_API_KEY (可选，StackExchange Key)
3. python kg_collect_web.py
"""
import os, re, json, time, random, requests, xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
from github import Github
import wikipediaapi
from neo4j import GraphDatabase

# ========== Neo4j 连接 ==========
NEO4J_URI  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS","your_password")  # 必填
if not NEO4J_PASS:
    raise RuntimeError("请设置环境变量 NEO4J_PASS")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ========== 工具函数 ==========
def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())

# 合并技术节点，接受自定义属性字典
def merge_tech(tx, name: str, tech_type: str, props: dict):
    norm_name = norm(name)
    # 构造 SET 片段
    set_props = ", ".join(f"t.{k} = ${k}" for k in props)
    query = f"""
    MERGE (t:{tech_type} {{norm:$norm}})
    ON CREATE SET t.name = $name, t.type = $type
    {"SET " + set_props if set_props else ""}
    """
    params = {
        "norm": norm_name,
        "name": name,
        "type": tech_type,
        **props
    }
    tx.run(query, **params)

# 关系写入，可携带属性
def relate(tx, from_norm: str, to_norm: str, rel: str, props: dict = None):
    props = props or {}
    set_props = ", ".join(f"r.{k} = ${k}" for k in props)
    query = f"""
    MATCH (a {{norm:$from_}}), (b {{norm:$to}})
    MERGE (a)-[r:{rel}]->(b)
    {"SET " + set_props if set_props else ""}
    """
    params = {"from_": from_norm, "to": to_norm, **props}
    tx.run(query, **params)

# ========== 1) Wikipedia 简介 ==========
wiki = wikipediaapi.Wikipedia(user_agent="EduKGBot/0.2", language="en")
def wiki_summary(title: str) -> str:
    page = wiki.page(title)
    if page.exists():
        return page.summary.split("\n")[0]
    return None

# ========== 2) Stack Overflow 相关标签 ==========
BASE_SO = "https://api.stackexchange.com/2.3"
def so_related_tags(tag: str, top_n: int = 5) -> list[str]:
    url = f"{BASE_SO}/tags/{requests.utils.quote(tag)}/related"
    params = {"site": "stackoverflow", "pagesize": top_n}
    key = os.getenv("STACK_API_KEY")
    if key:
        params["key"] = key
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return [i["name"] for i in data.get("items", [])]
    except Exception as e:
        print(f"[warn] SO API '{tag}' 失败: {e}")
        time.sleep(random.uniform(1,3))
        return []

# ========== 3) GitHub 仓库统计 ==========
def github_stats(name: str) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {}
    g = Github(token)
    try:
        repos = g.search_repositories(query=name, sort="stars", order="desc")
        if repos.totalCount > 0:
            repo = repos[0]
            return {
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "repo": repo.full_name
            }
    except Exception as e:
        print(f"[warn] GitHub API '{name}' 失败: {e}")
    return {}

# ========== 4) 官网搜索（DuckDuckGo） ==========
def first_search_result(query: str) -> str:
    try:
        html = requests.get(f"https://duckduckgo.com/html/?q={query}",
                            headers={"User-Agent": "Mozilla/5.0"}, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")
        a = soup.select_one(".result__a")
        return a["href"] if a else None
    except Exception:
        return None

# ========== 技术类别映射 ==========
CATEGORIES = {
    "Database":   ["MySQL","PostgreSQL","MongoDB","SQLite","OracleDB"],
    "Frontend":   ["Vue","React","Angular","Svelte","Next.js"],
    "Tool":       ["Maven","Gradle","Webpack","Vite","Spring Initializr"],
    "Library":    ["Spring Security","JUnit","Mockito","OAuth2","JWT"],
    "Middleware": ["Redis","Kafka","RabbitMQ","Nginx","Apache"],
    "Platform":   ["AWS","Azure","GCP","Heroku","Netlify"],
    "DevOps":     ["Docker","Kubernetes","Terraform","Ansible","Jenkins"],
    "AI":         ["Web3.0","LLMs","LangChain","HuggingFace","PyTorch"]
}

# ========== 主流程 ==========
if __name__ == "__main__":
    # 读取 tech_list.txt 或使用所有类别中的技术
    path = Path("tech_list.txt")
    if path.exists():
        techs = [l.strip() for l in path.read_text().splitlines() if l.strip()]
    else:
        techs = sum(CATEGORIES.values(), [])

    print("▶ 开始采集技术:", techs)
    with driver.session() as sess:
        # 确保 Spring Boot 框架节点存在
        sess.execute_write(merge_tech, "Spring Boot", "Framework", {})
        for tech in techs:
            # 决定类别
            tech_type = next((cat for cat, lst in CATEGORIES.items() if tech in lst), "Tech")
            props = {}
            # Wikipedia 简介
            summary = wiki_summary(tech)
            if summary: props["summary"] = summary
            # SO 标签
            tags = so_related_tags(tech.replace(" ", "-"))
            if tags: props["so_tags"] = ",".join(tags)
            # GitHub 统计
            gh = github_stats(tech)
            props.update(gh)
            # 官网链接
            url = first_search_result(f"{tech} official site")
            if url: props["homepage"] = url
            # 写入节点 & 属性
            sess.execute_write(merge_tech, tech, tech_type, props)
            # 建立与 Spring Boot 关系
            sess.execute_write(relate, norm("Spring Boot"), norm(tech), "USES", {"source": "aggregated"})
            print(f"[+] {tech} ({tech_type}) 写入，属性数={len(props)}")

    print("\n✔ 全部完成！请在 Neo4j 中查询查看效果。")
