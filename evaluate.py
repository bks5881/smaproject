import pandas as pd
import json
import numpy as np
user_recommendations = pd.read_csv("item_similarities.csv", index_col=0)
user_id = "-3AooxIkg38UyUdlz5oXdw"

min_rating = 1  # Minimum rating in your dataset
max_rating = 5  # Maximum rating in your dataset
user_recommendations = (user_recommendations - 0) / (1 - 0) * (max_rating - min_rating) + min_rating
recommendations = user_recommendations.loc[user_id].sort_values(ascending=False)
print(type(recommendations))
business = {}

with open("businesses_CA_NY.txt", "r") as file:
    for line in file:
        temp = json.loads(line)
        business[temp.get("business_id")]  = temp
#print(business)
for key, val in recommendations.items():
    print(key)
    if val is not np.nan and key is not None:
        print("User , ", str(user_id)," will rate the place ", str(business.get(key).get("name")), "with following rating", str(val))