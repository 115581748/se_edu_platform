# filename: knowledge_web_scraper.py
"""
脚本：从网络爬取更多技术相关知识，扩展已有Neo4j知识图谱
依赖：requests, beautifulsoup4, wikipedia-api, PyGithub, neo4j, stackapi
"""
import os
import re
import time
import requests
from bs4 import BeautifulSoup
from github import Github
import wikipediaapi
from stackapi import StackAPI
from neo4j import GraphDatabase

# ============ 配置 ============
NEO4J_URI  = os.getenv("NEO4J_URI",  "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "your_password")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
STACK_SITE = StackAPI('stackoverflow')
GITHUB = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
WIKI = wikipediaapi.Wikipedia(user_agent="EduKGScraper/0.1", language="en")

# ============ Neo4j 连接 ============
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# ============ 辅助函数 ============
def norm(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())

# 扩展节点属性写入
def merge_tech(tx, name: str, tech_type: str, summary=None,
               so_count=None, stars=None, forks=None):
    props = { 'norm': norm(name), 'name': name, 'type': tech_type }
    if summary: props['summary'] = summary
    if so_count is not None: props['so_count'] = so_count
    if stars    is not None: props['stars']   = stars
    if forks    is not None: props['forks']   = forks

    stmt = (
        "MERGE (t:Tech {norm:$norm})\n"
        "ON CREATE SET t += $props"
        ""
    )
    tx.run(stmt, props=props, norm=props['norm'])

# 关系写入
def relate(tx, a: str, b: str, rel: str):
    tx.run(
        f"MATCH (x:Tech {{norm:$a}}), (y:Tech {{norm:$b}}) "
        f"MERGE (x)-[r:{rel}]->(y)", a=a, b=b)

# ============ 数据抓取 ============
# 1. Wikipedia 摘要
def fetch_wiki_summary(topic: str) -> str:
    page = WIKI.page(topic)
    return page.summary.split('\n')[0] if page.exists() else ''

# 2. SO 问题数
def fetch_so_count(tag: str) -> int:
    try:
        info = STACK_SITE.fetch('tags/{}/info'.format(tag), pagesize=1)
        return info['items'][0]['count']
    except:
        return 0

# 3. GitHub 搜索仓库
from urllib.parse import quote_plus

def fetch_github_stats(topic: str):
    try:
        # 搜索前两个匹配仓库
        repos = GITHUB.search_repositories(query=topic, sort='stars', order='desc')
        if repos.totalCount > 0:
            repo = repos[0]
            return repo.stargazers_count, repo.forks_count
    except:
        pass
    return None, None

# ============ 主流程 ============
if __name__ == '__main__':
    # 自定义待抓取列表
    topics = [
        'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'OracleDB',
        'Vue.js', 'React', 'Angular', 'Svelte', 'Next.js',
        'Maven', 'Gradle', 'Webpack', 'Vite', 'Spring Initializr',
        'Redis', 'Kafka', 'RabbitMQ', 'Nginx', 'Apache',
        'AWS', 'Azure', 'GCP', 'Heroku', 'Netlify',
        'Spring Security', 'JUnit', 'Mockito', 'OAuth2', 'JWT',
        'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins',
        'Web3.0', 'LLMs', 'LangChain', 'Hugging Face', 'PyTorch'
    ]

    with driver.session() as session:
        for topic in topics:
            print(f"[*] 处理 {topic}...")
            summary = fetch_wiki_summary(topic)
            tag = topic.lower().replace('.', '').replace(' ', '-')
            so_count = fetch_so_count(tag)
            stars, forks = fetch_github_stats(topic)

            # 写入节点属性
            session.execute_write(merge_tech,
                                  topic, 'Tech',
                                  summary, so_count, stars, forks)
            time.sleep(1)

        # 示例：互相关联（可根据需要调整）
        for i in range(len(topics)-1):
            a, b = topics[i], topics[i+1]
            session.execute_write(relate, norm(a), norm(b), 'RELATED_TO')

    print("✔ 爬取并写入完毕！")
