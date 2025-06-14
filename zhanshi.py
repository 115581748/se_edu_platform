# —— 节点插入与属性合并 ——  
def merge_tech(tx, name, properties: dict):
    """
    1. 用 MERGE 保证 idempotency；
    2. ON CREATE 时填充名称与类型，SET t += $props 实现属性更新/补全。
    """
    query = """
    MERGE (t:Tech {norm:$norm})
    ON CREATE SET t.name = $name, t.type = $type
    SET t += $props
    """
    params = {
        "norm": norm(name),
        "name": name,
        "type": properties.pop("category", "Tech"),
        "props": properties
    }
    tx.run(query, **params)

# —— 依赖关系写入 ——  
def relate_to_fw(tx, tech_norm, rel="USES", fw="Spring Boot"):
    """
    1. MERGE 框架节点与技术节点；
    2. MERGE 依赖关系，避免重复边。
    """
    tx.run(f"""
      MERGE (fw:Framework {{name:$fw}})
      MERGE (t:Tech {{norm:$tech}})
      MERGE (fw)-[:{rel}]->(t)
      """,
      fw=fw, tech=tech_norm)
