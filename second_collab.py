import pandas as pd

# Step 1: Load the JSON file and extract necessary information
data = []
with open('filtered.txt', 'r') as file:
    for line in file:
        data.append(eval(line))  # Evaluate each line as a dictionary

df = pd.DataFrame(data)  # Convert the list of dictionaries to a DataFrame
print(df.loc[0])
# Find duplicate entries based on 'user_id' and 'business_id'
#duplicates = df[df.duplicated(subset=['user_id', 'business_id'], keep=False)]

# Print the duplicate entries
#print("Duplicate entries:")
#print(duplicates.loc[0])
#df = df.groupby(['user_id', 'business_id'], as_index=False)['stars'].mean()
# Step 2: Create a user-item matrix
matrix = df.pivot_table(index='user_id', columns='business_id', values='stars', aggfunc='mean')

#matrix = df.pivot(index='user_id', columns='business_id', values='stars')
matrix.fillna(0, inplace=True)  # Replace missing values with 0

# Step 3: Calculate similarities
# User-based similarities
print(matrix)
user_similarities = pd.DataFrame(index=matrix.index, columns=matrix.index)
for i in matrix.index:
    for j in matrix.index:
        user_similarities.loc[i, j] = 1 - (abs(matrix.loc[i] - matrix.loc[j]).sum() / matrix.shape[1])

# Item-based similarities
item_similarities = pd.DataFrame(index=matrix.columns, columns=matrix.columns)
for i in matrix.columns:
    for j in matrix.columns:
        item_similarities.loc[i, j] = 1 - (abs(matrix[i] - matrix[j]).sum() / matrix.shape[0])

# Step 4: Make recommendations
user_id = 'wSTuiTk-sKNdcFyprzZAjg'  # Example user_id
business_id = 'B5XSoSG3SfvQGtKEGQ1tSQ'  # Example business_id

# User-based recommendations
user_ratings = matrix.loc[user_id]
user_similarities[user_id].sort_values(ascending=False)  # Similarities between the user and other users
user_recommendations = user_ratings[user_ratings == 0]
user_recommendations = user_recommendations.rename('rating')
user_recommendations = pd.concat([user_recommendations, user_similarities[user_id]], axis=1)
user_recommendations.columns = ['rating', 'similarity']

# Item-based recommendations
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
