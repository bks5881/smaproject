import json
import concurrent.futures
from neo4j import GraphDatabase
# Connect to Neo4j database
uri = "neo4j+s://63e07a57.databases.neo4j.io"
user = "neo4j"
password = "8HUdVj-sahaqj8E0n858Ig9vYwNQddckXqejz3MQ_KE"

driver = GraphDatabase.driver(uri, auth=(user, password))

def process_json_line(json_line):
    # Process each JSON line here
    # This function will be called by each thread

    # Example: print the "name" field of each JSON object
    data = json.loads(json_line)
    if data["state"] in ("CA", "NY"):
        with open("output.txt", "a") as f:
            f.write(json_line)


def process_json_file(filename, num_threads):
    # Create a thread pool and submit jobs to it
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        with open(filename, "r") as f:
            # Process each JSON line in the file
            for json_line in f:
                # Submit the JSON line to the thread pool
                future = executor.submit(process_json_line, json_line)
                futures.append(future)
                # Handle any exceptions that occurred in the thread pool
                if future.exception() is not None:
                    print(f"Exception in thread pool: {future.exception()}")
            for future in concurrent.futures.as_completed(futures):
                # Handle any exceptions that occurred in the thread pool
                if future.exception() is not None:
                    print(f"Exception in thread pool: {future.exception()}")

def filter_helper(line, businesses):
    review = json.loads(line)
    if review.get("business_id") in businesses:
        with open("filtered.txt", "a") as f:
            f.write(line)
def filter_reviews(filename):

    with open(filename, "r") as f:
        temp = f.readlines()
        businesses = {}
        for line in temp:
            item = json.loads(line)
            businesses[item.get("business_id")] =item
        #businesses = json.loads(temp)
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        with open("yelp_dataset/yelp_academic_dataset_review.json", "r") as f2:
            for line in f2:
                #print(line)
            #line = f.readline()
                future = executor.submit(filter_helper,line, businesses)
                futures.append(future)
                if future.exception() is not None:
                    print(f"Exception in thread pool: {future.exception()}")
            for future in concurrent.futures.as_completed(futures):
                # Handle any exceptions that occurred in the thread pool
                if future.exception() is not None:
                    print(f"Exception in thread pool: {future.exception()}")

def insert_nodes():

    cypher = "MERGE (r:Reviewer {id: $user_id})" \
             "MERGE (b:Business {id: $business_id})" \
             "MERGE (r)-[e:REVIEWED]-(b)" \
             "SET e.rating = $stars, e.text = $text"
    count = 0
    try:
        with open("filtered.txt", "r") as f:
            futures = []
            #with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executer:
            with driver.session() as session:
                for line in f:
                    data = json.loads(line)
                    print(data)
                    session.execute_write(lambda tx: tx.run(cypher, **data))
                    #futures.append(executer.submit(helper, session, data, cypher))
                    count +=1
                    #if count >=100:
                     #break
    except :
        print("Count", str(count))
        #for future in concurrent.futures.as_completed(futures):
        #    if future.exception() is not None:
        #        print("Ooops something went wrong")
def helper(session, data, query):
    session.execute_write(lambda tx: tx.run(query, **data))
    return True
if __name__ == "__main__":
    filename = "yelp_dataset/yelp_academic_dataset_business.json"
    num_threads = 4
    # This filters the file to only businesses in California and new york
    #process_json_file(filename, num_threads)
    #filter_reviews("output.txt")
    insert_nodes()


