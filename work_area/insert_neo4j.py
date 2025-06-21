from neo4j import GraphDatabase

# Neo4j connection
uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"  # Change this

driver = GraphDatabase.driver(uri, auth=(user, password))


# 1. Generate 4-level binary tree with LEFT and RIGHT edges
def generate_binary_tree(levels=4):
    entities = []
    relations = []

    for i in range(1, 2 ** levels):  # 1 to 15
        level = i.bit_length()
        node_name = f"Node_{i}"

        # 👇 Add a custom summary
        summary = f"This is a node at level {level}, position {i} in the tree."

        entities.append({
            "name": node_name,
            "type": "TreeNode",
            "level": level,
            "summary": summary
        })

        if i > 1:
            parent_index = i // 2
            relation_type = "LEFT" if i % 2 == 0 else "RIGHT"
            relations.append({
                "source": f"Node_{parent_index}",
                "target": node_name,
                "type": relation_type
            })

    return entities, relations


# 2. Create nodes
def create_nodes(tx, entities):
    for entity in entities:
        entity_copy = entity.copy()
        label = entity_copy.pop("type")
        name_val = entity_copy.pop("name")
        props = ", ".join([f"{k}: ${k}" for k in entity_copy])
        if props:
            cypher = f"MERGE (n:{label} {{name: $name}}) SET n += {{{props}}}"
            tx.run(cypher, name=name_val, **entity_copy)
        else:
            cypher = f"MERGE (n:{label} {{name: $name}})"
            tx.run(cypher, name=name_val)


# 3. Create relationships
def create_relationships(tx, relations):
    for rel in relations:
        rel_type = rel["type"]
        cypher = (
            "MATCH (a {name: $source}), (b {name: $target}) "
            f"MERGE (a)-[r:{rel_type}]->(b)"
        )
        tx.run(cypher, source=rel["source"], target=rel["target"])


# 4. Execute all
def main():
    entities, relations = generate_binary_tree(levels=4)
    print(f"Creating {len(entities)} nodes and {len(relations)} relationships...")

    with driver.session() as session:
        session.execute_write(create_nodes, entities)
        session.execute_write(create_relationships, relations)

    print("✅ 4-level binary tree created successfully!")
    driver.close()


if __name__ == "__main__":
    main()
