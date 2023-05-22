import pandas as pd
import concurrent.futures

# Step 1: Load the JSON file and extract necessary information
data = []
with open('filtered.txt', 'r') as file:
    for line in file:
        data.append(eval(line))  # Evaluate each line as a dictionary

df = pd.DataFrame(data)  # Convert the list of dictionaries to a DataFrame
print(df.loc[0])

# Step 2: Create a user-item matrix
matrix = df.pivot_table(index='user_id', columns='business_id', values='stars', aggfunc='mean')
matrix.fillna(0, inplace=True)  # Replace missing values with 0
matrix = matrix.loc[matrix.astype(bool).sum(axis=1) >= 20]
matrix = matrix.loc[:, matrix.astype(bool).sum(axis=0) >= 40]

# Step 3: Calculate similarities
# User-based similarities
print(matrix)
user_similarities = pd.DataFrame(index=matrix.index, columns=matrix.index)


def calculate_user_similarity(i, j):
    return 1 - (abs(matrix.loc[i] - matrix.loc[j]).sum() / matrix.shape[1])


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for i in matrix.index:
        for j in matrix.index:
            futures.append(executor.submit(calculate_user_similarity, i, j))

    # Retrieve results
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        i_row = max((i // matrix.shape[1])-1, 0)
        j_col = max( (i % matrix.shape[1])-1, 0)
        if i_row>=user_similarities.shape[0] or j_col>=user_similarities.shape[1]:
            break
        print(i_row, j_col)
        print(user_similarities.shape)
        user_similarities.iloc[i_row,j_col] = future.result()

# Item-based similarities
item_similarities = pd.DataFrame(index=matrix.columns, columns=matrix.columns)


def calculate_item_similarity(i, j):
    return 1 - (abs(matrix[i] - matrix[j]).sum() / matrix.shape[0])


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for i in matrix.columns:
        for j in matrix.columns:
            futures.append(executor.submit(calculate_item_similarity, i, j))

    # Retrieve results
    for i, future in enumerate(concurrent.futures.as_completed(futures)):
        i_row = i // matrix.shape[1]
        j_col = i % matrix.shape[1]
        item_similarities.iloc[i_row, j_col] = future.result()
item_similarities.to_csv("item_similarities.csv")
user_similarities.to_csv("user_similarities.csv")
# Step 4: Make recommendations
'''
user_id = 'wSTuiTk-sKNdcFyprzZAjg'  # Example user_id
business_id = 'B5XSoSG3SfvQGtKEGQ1tSQ'  # Example business_id

# User-based recommendations
user_ratings = matrix.loc[user_id]
user_similarities[user_id].sort_values(ascending=False)  # Similarities between the user and other users
user_recommendations = user_ratings[user_ratings == 0]
user_recommendations = user_recommendations.rename('rating')
user_recommendations = pd.concat([user_recommendations, user_similarities[user_id]], axis=1)
user_recommendations.columns = ['rating', 'similarity']
'''

# Item-based recommendations
'''
item_ratings = matrix.T.loc[business_id]
item_similarities[business_id].sort_values(ascending=False)  # Similarities between the item and other items
item_recommendations = item_ratings[item_ratings == 0]
item_recommendations = item_recommendations.rename('rating')
item_recommendations = pd.concat([item_recommendations, item_similarities[business_id]], axis=1)
item_recommendations.columns = ['rating', 'similarity']

print("User-based recommendations:")
print(user_recommendations)

print("\nItem-based recommendations:")
print(item_recommendations)
'''