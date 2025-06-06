from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))

def load_data():
    with driver.session() as session:
        session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///frameworks.csv' AS row
            MERGE (f:Framework {name: row.name})
            MERGE (l:Language {name: row.language})
            MERGE (f)-[:USES]->(l)
        """)

if __name__ == "__main__":
    load_data()
    print("Data loaded successfully into Neo4j.")
    
