import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Read the JSON file
df = pd.read_json("filtered.txt", lines=True)

# Create user-item matrix
matrix = df.pivot_table(index='user_id', columns='business_id', values='stars', aggfunc='mean')
matrix.fillna(0, inplace=True)  # Replace missing values with 0
matrix = matrix.loc[matrix.astype(bool).sum(axis=1) >= 20]
matrix = matrix.loc[:, matrix.astype(bool).sum(axis=0) >= 40]
matrix_norm = matrix.subtract(matrix.mean(axis=1), axis = 'rows')
print(matrix_norm.head())
user_similarity = matrix_norm.corr()
user_similarity.head()
# Calculate user similarity
#user_similarity = cosine_similarity(matrix)
picked_userid = 1
# Remove picked user ID from the candidate list
#user_similarity.drop(index="", inplace=True)
# Take a look at the data
user_similarity.head()
# Create a DataFrame with user_id as index and business_id as columns
user_similarity_df = pd.DataFrame(user_similarity, index=user_similarity.index, columns=user_similarity.columns)

user_similarity_df.to_csv("sk_learn_collaborative.csv")
