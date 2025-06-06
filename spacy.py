# 使用spaCy抽取实体
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Spring Boot is a Java-based framework.")
entities = [(ent.text, ent.label_) for ent in doc.ents]  # 输出：[('Spring Boot', 'ORG')]

# 存入Neo4j
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    session.run("CREATE (f:Framework {name: $name})", name=entities[0][0])
    