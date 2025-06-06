# filename: mark_concepts_taught.py

from neo4j import GraphDatabase

# ———— 1. 配置 Neo4j 连接 ————
NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "your_password"      # 根据你自己的密码填入

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))


# ———— 2. 批量插入 Concept 节点（仅 name 和 description） ————
def batch_insert_concepts(tx, name: str, description: str):
    """
    如果图中不存在同名的 Concept，就创建一个新节点并设置 description；
    如果已经存在，只保留已有 description（可根据需要改为更新 description）。
    """
    tx.run(
        """
        MERGE (c:Concept {name: $name})
        ON CREATE SET c.description = $description
        """,
        name=name,
        description=description
    )


# ———— 3. 批量将指定名称的节点标记为 status = "taught" ————
def mark_concepts_as_taught(tx, names: list):
    """
    通过 UNWIND 一次性把所有要打标记的 name 都匹配到，并给它们加上 status="taught"。
    """
    tx.run(
        """
        UNWIND $names AS nm
        MATCH (c:Concept {name: nm})
        SET c.status = "taught"
        """,
        names=names
    )


def main():
    # （1）示例数据：所有要插入的概念列表
    # 你可以根据需要改成读自 CSV、JSON 或者自己在代码中写死
    # all_concepts = [
    #     ("Spring Security", "用于 Spring Boot 应用的安全认证与授权框架"),
    #     ("JUnit", "Java 语言中的单元测试框架"),
    #     ("Mockito", "Java 中的 Mock 测试库，用于模拟对象行为"),
    #     ("Docker", "轻量化容器化平台"),
    #     ("Kubernetes", "容器编排系统，用来管理 Docker 容器集群"),
    #     ("Redis", "内存数据库，常用于缓存"),
    #     ("Kafka", "分布式消息系统"),
    #     ("OAuth2", "一种用于授权的开放标准协议"),
    #     ("JWT", "JSON Web Token，用于在客户端与服务器之间安全传输信息"),
    #     ("Vue", "流行的前端框架"),
    #     ("React", "Facebook 推出的前端库"),
    #     ("Angular", "Google 推出的前端框架"),
    #     ("Node.js", "基于 Chrome V8 引擎的 JavaScript 运行时"),
    #     # … 你可以继续往列表里补充需要的概念
    # ]

    # （2）示例：所有要打上“已教学”标记（status="taught"）的概念名称列表
    # 只有 name 在这个列表里的节点，才会被打上 status="taught"
    names_to_mark_taught = [
        "class",
        # "JUnit",
        # "Mockito",
        # "Docker",
        # "Redis",
        # … 如果你想把更多概念也标成“已教学”，就加到这里
    ]

    # ———— 3.1 批量插入所有 Concept 节点（仅 name+description） ————
    with driver.session() as session:
        for (name, desc) in all_concepts:
            session.write_transaction(batch_insert_concepts, name, desc)
    print(f"[+] 已插入或合并 {len(all_concepts)} 个 Concept 节点（仅 name+description）。")

    # ———— 3.2 一次性批量打上 status="taught" ————
    with driver.session() as session:
        session.write_transaction(mark_concepts_as_taught, names_to_mark_taught)
    print(f"[+] 已将 {len(names_to_mark_taught)} 个 Concept 节点标记为 status=\"taught\"。")

    driver.close()


if __name__ == "__main__":
    main()
