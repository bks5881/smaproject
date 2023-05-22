from py2neo import Graph
import numpy as np
# Connect to Neo4j database
uri = "neo4j+s://63e07a57.databases.neo4j.io"
user = "neo4j"
password = "8HUdVj-sahaqj8E0n858Ig9vYwNQddckXqejz3MQ_KE"

graph = Graph(uri, auth=(user, password))

query = """
MATCH (n)
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m
"""


def adamic_adar_score_bipartite(adj_matrix, left_nodes, right_nodes):
    # Calculate the inverse log degree for each node in the left partition
    degree = np.sum(adj_matrix, axis=1)
    #inv_log_degree = np.where(degree > 0.0, 1 / np.log(degree), 0)
    inv_log_degree = np.zeros(len(left_nodes))
    for i, node in enumerate(left_nodes):
        degree = np.sum(adj_matrix[i])
        inv_log_degree[i] = 1 / np.log(degree) if degree > 0 else 0

    # Calculate the Adamic-Adar score for all pairs of nodes
    aa_score = np.zeros((len(left_nodes), len(right_nodes)))
    for i in range(len(left_nodes)):
        for j in range(len(right_nodes)):
            common_neighbors = np.nonzero(left_nodes[i] * right_nodes[j])[0]
            aa_score[i][j] = np.sum(inv_log_degree[common_neighbors])

    return aa_score


def adamic_adar_link_prediction(adj_matrix, nodes, restaurants,num_top_predictions):
    # Calculate the Adamic-Adar score for all pairs of nodes
    #np.fill_diagonal(adj_matrix, 1)
    aa_score = adamic_adar_score_bipartite(adj_matrix, nodes, restaurants)

    predicted_edges = []
    for i in range(adj_matrix.shape[0]):
        for j in range(i+1, adj_matrix.shape[1]):
            if adj_matrix[i][j] == 0:
                score = aa_score[i][j]
                predicted_edges.append(((i, j), score))

    # Sort the predicted edges by score in descending order
    predicted_edges.sort(key=lambda x: x[1], reverse=True)

    return predicted_edges[0:num_top_predictions]


results = graph.run(query)
nodes = set()
edges = []
restuarants = set()
count = 0
for record in results:
    node = record['n']

    #nodes.add(record['m'])
    edge = record['r']
    if edge is not None:
        edges.append((node, edge, record['m']))
        #edges.append((record['m'], edge,node))
        nodes.add(node)
        restuarants.add(record['m'])
        #nodes.add(record['m'])
        count +=1
        if len(nodes)>=100:
            break
    #print(edge)

# Create a dictionary mapping node IDs to indices in the adjacency matrix
node_index = {node.identity: i for i, node in enumerate(nodes)}
restuarants_index = {node.identity: i for i, node in enumerate(restuarants)}
lookup_settings = {node.identity: node for node in nodes}
for j, restuarant in enumerate(restuarants):
    lookup_settings[restuarant.identity] = j
# Create an empty adjacency matrix
adj_matrix = np.zeros((len(nodes), len(restuarants)))

# Populate the adjacency matrix with edge weights
for edge in edges:
    source = node_index[edge[0].identity]
    target = restuarants_index.get(edge[2].identity)
    '''
    if target is None:
        target = len(nodes)
        nodes.add(edge[2])
        node_index[edge[2].identity] = target
        adj_matrix.resize((target + 1, target + 1))
    '''
    weight = edge[1]['rating']
    adj_matrix[source][target] = weight
print(len(adj_matrix))
print(len(adj_matrix[0]))
edges = adamic_adar_link_prediction(adj_matrix,list(node_index.keys()), list(restuarants_index.keys()),3)
print(edges)

def adamic_adar_link_prediction2(adj_matrix, num_top_predictions):
    # Find the indices of the missing edges in the adjacency matrix
    missing_edges = np.argwhere(adj_matrix == 0)

    # Calculate the Adamic-Adar score for each missing edge
    scores = []
    for edge in missing_edges:
        # Find the common neighbors of the two nodes in the missing edge
        common_neighbors = np.nonzero(adj_matrix[edge[0]] * adj_matrix[edge[1]])[0]

        # Calculate the Adamic-Adar score
        score = sum([1 / np.log(adj_matrix[neighbor].sum()) for neighbor in common_neighbors])
        scores.append(score)

    # Combine the missing edges and their scores into a list of tuples
    predicted_edges = list(map(tuple, missing_edges))
    results = list(zip(predicted_edges, scores))

    # Sort the results by score in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    # Return the top predicted edges and their scores
    return results[:num_top_predictions]
#edges = adamic_adar_link_prediction2(adj_matrix,3)
for edge in edges:
    print("" + str(lookup_settings[edge[0][0]]) +"--> " + str(lookup_settings[edge[0][1]]))
print(edges)
