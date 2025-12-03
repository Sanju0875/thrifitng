import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os


DATA_PATH = "womens_wear_dataset.csv" 
MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


df = pd.read_csv(DATA_PATH, sep=",", encoding="latin-1")

df.drop_duplicates(inplace=True)


user_item_matrix = df.pivot_table(
    index='Title',          
    columns='PurchaseID',   
    values='Rating'        
).fillna(0)

def standardize(row):
    if row.max() - row.min() == 0:
        return row * 0
    return (row - row.mean()) / (row.max() - row.min())

products_std = user_item_matrix.apply(standardize, axis=1)

# === STEP 4: Compute item-item similarity ===
item_similarity = cosine_similarity(products_std)
item_similarity_df = pd.DataFrame(
    item_similarity,
    index=user_item_matrix.index,
    columns=user_item_matrix.index
)

# === STEP 5: Save models ===
user_item_matrix.to_pickle(os.path.join(MODEL_DIR, "user_item_matrix.pkl"))
item_similarity_df.to_pickle(os.path.join(MODEL_DIR, "item_similarity.pkl"))

print("✅ Model files saved in:", MODEL_DIR)
