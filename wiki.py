from neo4j import GraphDatabase
import wikipediaapi

# 初始化
wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="MySE-LearningBot/0.1 (myemail@example.com)"
)
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

# 抓一个词条
page = wiki.page("Spring Boot")

with driver.session() as sess:
    sess.run(
        """
        MERGE (t:Tech {name:$name})
        ON CREATE SET t.source='wikipedia', t.summary=$summary
        """,
        name="spring boot",
        summary=page.summary[:8000]
    )
print("写入完成")
