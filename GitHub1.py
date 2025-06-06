# filename: github_to_neo4j.py
import os
import re
from pathlib import PurePosixPath
from github import Github
from neo4j import GraphDatabase

# ====== 配置 ======
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_FULLNAME = "spring-projects/spring-boot"
NEO4J_URI     = "bolt://localhost:7687"
NEO4J_AUTH    = ("neo4j", "your_password")

# ====== 连接客户端 ======
g       = Github(GITHUB_TOKEN)                 # 连接 GitHub
repo    = g.get_repo(REPO_FULLNAME)            # 仓库对象
driver  = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)  # 连接 Neo4j

# ====== 正则：极简 Java 解析 ======
CLASS_RE  = re.compile(r"\bclass\s+([A-Z][A-Za-z0-9_]*)")
METHOD_RE = re.compile(r"\b(?:public|protected|private)?\s+\w+\s+([a-z][A-Za-z0-9_]*)\s*\([^)]*\)\s*[{;]")

def extract_entities(java_text):
    """返回 (类名, [方法名列表])"""
    cls_match = CLASS_RE.search(java_text)
    if not cls_match:
        return None, []
    cls_name  = cls_match.group(1)
    methods   = METHOD_RE.findall(java_text)
    return cls_name, methods

# ====== 遍历所有 src/main/java 下的 .java 文件 ======
def walk_java_files():
    for content in repo.get_contents("spring-boot-project"):
        stack = [content]
        while stack:
            item = stack.pop()
            if item.type == "dir":
                # 仅深入包含 src/main/java 的子目录；可删掉 if 递归更彻底
                stack.extend(repo.get_contents(item.path))
            elif item.path.endswith(".java") and "/src/main/java/" in item.path:
                yield item

# ---- 写入 Neo4j：修正版 ----
def write_to_graph(session, class_name, method_list, file_path):
    # 创建 / 合并 Class 节点
    session.run(
        """
        MERGE (c:Class {name:$cls, source:$file})
        """,
        cls=class_name,
        file=file_path,
    )

    # 创建 Method 节点 + DECLARES 关系
    for m in method_list:
        session.run(
            """
            MERGE (m:Method {name:$method})
            WITH m
            MATCH (c:Class {name:$cls})
            MERGE (c)-[:DECLARES]->(m)
            """,
            method=m,
            cls=class_name,
        )

def main():
    total = 0
    with driver.session() as session:
        for file in walk_java_files():
            java_code = file.decoded_content.decode("utf-8", errors="ignore")
            cls, methods = extract_entities(java_code)
            if cls:
                write_to_graph(session, cls, methods, file.path)
                total += 1
                print(f"[+] {file.path}  →  {cls} ({len(methods)} 方法)")
    print(f"\n共写入 {total} 个类节点。")

if __name__ == "__main__":
    main()
