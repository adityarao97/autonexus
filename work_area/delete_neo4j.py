from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

driver = GraphDatabase.driver(uri, auth=(user, password))

def delete_all(tx):
    tx.run("MATCH (n) DETACH DELETE n")

with driver.session() as session:
    session.execute_write(delete_all)

driver.close()
print("✅ All data deleted from Neo4j.")