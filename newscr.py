# tech_dependency_graph.py  — 构建技术依赖图（基于 Wikipedia 与 SO 标签共现）
"""
脚本功能：
1. 读取预定义技术列表
2. 对每种技术，从 Wikipedia "See also" 抓取相关技术
   和 StackOverflow 相关标签
3. 仅当抓取到的相关技术也在列表中时，创建 Tech 节点，并在它们之间建立关系
4. 将结果写入 Neo4j，生成一个技术依赖/关联图谱

使用方法：
1. pip install neo4j requests wikipedia-api beautifulsoup4
2. 设置环境变量：
   - NEO4J_URI (可选)
   - NEO4J_USER (可选)
   - NEO4J_PASS (必需)
   - STACK_API_KEY (可选，提高 SO 配额)
3. python tech_dependency_graph.py
"""
import os, re, time, random, requests
from pathlib import Path
from bs4 import BeautifulSoup
import wikipediaapi
from neo4j import GraphDatabase

# ========== 配置 ==========
TECH_LIST = [
    # Databases
    "MySQL","PostgreSQL","MongoDB","SQLite","OracleDB",
    # Frontend
    "Vue","React","Angular","Svelte","Next.js",
    # Build tools
    "Maven","Gradle","Webpack","Vite","Spring Initializr",
    # Middleware
    "Redis","Kafka","RabbitMQ","Nginx","Apache",
    # Platforms
    "AWS","Azure","GCP","Heroku","Netlify",
    # Security/Testing
    "Spring Security","JUnit","Mockito","OAuth2","JWT",
    # DevOps
    "Docker","Kubernetes","Terraform","Ansible","Jenkins",
    # AI
    "Web3.0","LLMs","LangChain","HuggingFace","PyTorch"
]
# 归一化列表 & 快速查找
def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())
TECH_NORMS = {norm(t): t for t in TECH_LIST}

# Neo4j 连接
URI   = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER  = os.getenv("NEO4J_USER", "neo4j")
PASS  = os.getenv("NEO4J_PASS","your_password") or exit("your_password")
driver = GraphDatabase.driver(URI, auth=(USER, PASS))

# ========== 写入函数 ==========
def merge_tech(tx, name):
    tx.run("MERGE (t:Tech {norm:$norm}) SET t.name=$name", norm=norm(name), name=name)

def relate(tx, a_norm, b_norm, rel_type):
    tx.run(
        f"MATCH (a:Tech {{norm:$a}}),(b:Tech {{norm:$b}}) "
        f"MERGE (a)-[r:{rel_type}]->(b)",
        a=a_norm, b=b_norm
    )

# ========== 数据源 ==========
# 1) Wikipedia "See also"
wiki = wikipediaapi.Wikipedia(user_agent="TechKGBot/1.0", language="en")
def wiki_see_also(title):
    page = wiki.page(title)
    if not page.exists(): return []
    rel = []
    for sec in page.sections:
        if 'see also' in sec.title.lower():
            rel += [line.strip() for line in sec.text.split("\n") if line.strip()]
    return rel

# 2) SO 相关标签
BASE_SO = "https://api.stackexchange.com/2.3"
def so_tags(tag, top_n=10):
    url = f"{BASE_SO}/tags/{requests.utils.quote(tag)}/related"
    params = {"site":"stackoverflow","pagesize":top_n}
    key = os.getenv("STACK_API_KEY")
    if key: params['key'] = key
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        return [item['name'] for item in r.json().get('items',[])]
    except:
        time.sleep(random.uniform(1,2)); return []

# ========== 主流程 ==========
if __name__ == '__main__':
    print("▶ 开始构建技术依赖图…")
    with driver.session() as sess:
        # 创建所有技术节点
        for tech in TECH_LIST:
            sess.execute_write(merge_tech, tech)
        # 对每个技术，抓取关系并写入
        for tech in TECH_LIST:
            tn = norm(tech)
            # Wikipedia 关联
            for rel in wiki_see_also(tech):
                rn = norm(rel)
                if rn in TECH_NORMS and rn!=tn:
                    sess.execute_write(relate, tn, rn, 'WIKI_REL')
                    print(f"[Wiki] {tech} -> {TECH_NORMS[rn]}")
            # SO 标签关联
            for tag in so_tags(tech.replace(' ','-').lower()):
                rn = norm(tag)
                if rn in TECH_NORMS and rn!=tn:
                    sess.execute_write(relate, tn, rn, 'SO_REL')
                    print(f"[SO] {tech} -> {TECH_NORMS[rn]}")
    print("✔ 完成！请在 Neo4j 查看 Tech 节点的 WIKI_REL 与 SO_REL 关系。")
