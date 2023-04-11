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


def adamic_adar_score(adj_matrix):
    # Calculate the degree of each node
    degree = np.sum(adj_matrix, axis=1)

    # Compute the inverse logarithmic degree for each node
    inv_log_degrees = np.where(degree > 0.0, 1 / np.log(degree), 0)

    # Compute the diagonal matrix of inverse logarithmic degrees
    inv_log_degrees_mat = np.diag(inv_log_degrees)

    # Compute the normalized adjacency matrix
    norm_adj_matrix = adj_matrix / degree[:, np.newaxis]

    # Compute the Adamic-Adar score matrix
    aa_score_matrix = inv_log_degrees_mat @ norm_adj_matrix @ inv_log_degrees_mat

    # Set the diagonal elements to zero
    np.fill_diagonal(aa_score_matrix, 1)

    return aa_score_matrix


def adamic_adar_link_prediction(adj_matrix, num_top_predictions):
    # Calculate the Adamic-Adar score for all pairs of nodes
    np.fill_diagonal(adj_matrix, 1)
    aa_score = adamic_adar_score(adj_matrix)

    # Get the indices of the top num_top_predictions pairs of nodes with the highest Adamic-Adar score
    top_indices = np.argpartition(aa_score, -num_top_predictions, axis=None)[-num_top_predictions:]
    top_indices = np.unravel_index(top_indices, aa_score.shape)

    # Create a list of predicted edges
    predicted_edges = []
    for i in range(num_top_predictions):
        source = top_indices[0][i]
        target = top_indices[1][i]
        if adj_matrix[source][target] == 0:
            score = aa_score[source][target]
            predicted_edges.append(((source, target), score))


    return predicted_edges


results = graph.run(query)
nodes = set()
edges = []

count = 0
for record in results:
    node = record['n']

    #nodes.add(record['m'])
    edge = record['r']
    if edge is not None:
        edges.append((node, edge, record['m']))
        nodes.add(node)
        nodes.add(record['m'])
        count +=1
        if len(nodes)>=10000:
            break
    #print(edge)

# Create a dictionary mapping node IDs to indices in the adjacency matrix
node_index = {node.identity: i for i, node in enumerate(nodes)}

# Create an empty adjacency matrix
adj_matrix = np.zeros((len(nodes), len(nodes)))

# Populate the adjacency matrix with edge weights
for edge in edges:
    source = node_index[edge[0].identity]
    target = node_index.get(edge[2].identity)
    if target is None:
        target = len(nodes)
        nodes.add(edge[2])
        node_index[edge[2].identity] = target
        adj_matrix.resize((target + 1, target + 1))
    weight = edge[1]['rating']
    adj_matrix[source][target] = weight
print(len(adj_matrix))
print(len(adj_matrix[0]))
edges = adamic_adar_link_prediction(adj_matrix,3)
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

print(edges)
