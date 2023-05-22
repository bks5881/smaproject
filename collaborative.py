import numpy as np
import pandas as pd

def pearson_correlation(user1, user2):
    # Get the indices of items that both users have rated
    common_items = np.intersect1d(np.where(user1 != 0), np.where(user2 != 0))

    # Calculate the mean rating of each user for the common items
    user1_mean = np.mean(user1[common_items])
    user2_mean = np.mean(user2[common_items])

    # Calculate the numerator and denominator of the Pearson correlation coefficient
    numerator = np.sum((user1[common_items] - user1_mean) * (user2[common_items] - user2_mean))
    denominator = np.sqrt(
        np.sum((user1[common_items] - user1_mean) ** 2) * np.sum((user2[common_items] - user2_mean) ** 2))

    # Handle the case where the denominator is zero
    if denominator == 0:
        return 0

    # Calculate the Pearson correlation coefficient
    corr = numerator / denominator

    return corr


def predict_rating(user_id, item_id, user_item_matrix):
    # Get the ratings of the item by all users
    item_ratings = user_item_matrix[:, item_id]

    # Get the indices of users who have rated the item
    rated_users = np.where(item_ratings != 0)[0]

    # Calculate the Pearson correlation coefficient between the user and each rated user
    similarities = [pearson_correlation(user_item_matrix[user_id], user_item_matrix[rated_user]) for rated_user in
                    rated_users]

    # Get the ratings of the rated users for the item
    ratings = item_ratings[rated_users]

    # Calculate the weighted sum of the ratings and similarities
    numerator = np.sum(similarities * ratings)
    denominator = np.sum(np.abs(similarities))

    # Handle the case where the denominator is zero
    if denominator == 0:
        return 0

    # Calculate the predicted rating
    predicted_rating = numerator / denominator

    return predicted_rating

def step1():

    # Load the reviews dataset into a pandas DataFrame
    reviews_df = pd.read_json("sub_sample.json", lines=True)
    # Extract the unique users and items
    unique_users = reviews_df["user_id"].unique()
    unique_items = reviews_df["business_id"].unique()

    # Create the user-item matrix
    user_item_matrix = np.zeros((len(unique_users), len(unique_items)))

    # Loop through the reviews and fill in the matrix
    for index, row in reviews_df.iterrows():
        user_idx = np.where(unique_users == row["user_id"])[0][0]
        item_idx = np.where(unique_items == row["business_id"])[0][0]
        user_item_matrix[user_idx, item_idx] = row["stars"]
    print(user_item_matrix)
    return [user_item_matrix,unique_users,unique_items]
def step2():
    # Sample user-item matrix
    user_item_matrix,unique_users,unique_items = step1()

    # Test the functions with sample data
    user_id = int(np.where(unique_users=="Uk3X2AypU8AqvcYEVf7s6Q")[0][0])
    item_id = int(np.where(unique_items=="eL4lyE7LNoXEMvpcJ8WNVw")[0][0])
    predicted_rating = predict_rating(user_id, item_id, user_item_matrix)
    print(f"Predicted rating of user {user_id} for item {item_id}: {predicted_rating}")
step2()