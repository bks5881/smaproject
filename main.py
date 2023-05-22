from neo4j import GraphDatabase
import json
from concurrent.futures import ThreadPoolExecutor

# Connect to Neo4j database
uri = "neo4j+s://63e07a57.databases.neo4j.io"
user = "neo4j"
password = "8HUdVj-sahaqj8E0n858Ig9vYwNQddckXqejz3MQ_KE"
driver = GraphDatabase.driver(uri, auth=(user, password))

# Define Cypher queries to create nodes and add edges
create_person_query = "CREATE (:Guide {user_id: $user_id})"
create_business_query = "CREATE (:Business {business_id: $business_id})"
create_edge_query = "MATCH (p:Guide {user_id: $user_id}), (b:Business {business_id: $business_id}) CREATE (p)-[:Reviews {stars: $stars, text: $text}]->(b) "

# Run Cypher queries to create nodes and add edges
def build_graph():

    with open('yelp_dataset/yelp_academic_dataset_review.json', 'r') as f:
        count = 0

        for line in f:
            if count<3423:
                count+=1
                continue
            with driver.session() as session:
                data = json.loads(line)
                print(data)
                helper(session, data, create_person_query)
                helper(session, data, create_business_query)
                helper(session, data, create_edge_query)
            count+=1
            if count >4000:
                break
            print("blah")


def helper(session, data, query):
    session.write_transaction(lambda tx: tx.run(query, **data))
    return True
build_graph()