import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Read the JSON file
df = pd.read_json("sub_sample.json", lines=True)

# Create user-item matrix
user_item_matrix = df.pivot(index='user_id', columns='business_id', values='stars')
user_item_matrix.fillna(0, inplace=True)

# Calculate user similarity
user_similarity = cosine_similarity(user_item_matrix)

# Define target user and item
target_user_id = "OhECKhQEexFypOMY6kypRw"
target_business_id = 'gebiRewfieSdtt17PTW6Zg'

# Find similar users to the target user
similar_users_indices = user_similarity[user_item_matrix.index == target_user_id].argsort()[0][-2::-1]


# Predict the target user's rating for the item
prediction = user_item_matrix.iloc[similar_users_indices, user_item_matrix.columns == target_business_id].mean()
#
print(f'prediction : {prediction}')

