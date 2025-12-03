import pandas as pd
import os
from django.conf import settings
from .models import Products

item_similarity = pd.read_pickle(os.path.join(settings.BASE_DIR / "models", "item_similarity.pkl"))

# def get_recommendations(last_viewed_titles, top_n=5):
#     recommended_titles = []

#     # Get all product titles currently in DB
#     db_titles = set(Products.objects.values_list('title', flat=True))
    
#     # Loop through all products the user viewed
#     for title in last_viewed_titles:
#         if title in item_similarity.index:
#             similar_scores = item_similarity.loc[title]
#             # Sort by similarity, exclude itself
#             similar_titles = similar_scores.sort_values(ascending=False).index.tolist()
#             similar_titles.remove(title)

#             # Only keep titles that exist in your DB
#             similar_titles = [t for t in similar_titles if t in db_titles]

#             recommended_titles.extend(similar_titles[:top_n])

#     # Remove duplicates and limit to top N overall
#     recommended_titles = list(dict.fromkeys(recommended_titles))[:top_n]

#     # Fetch actual Products from DB
#     recommended_products = Products.objects.filter(title__in=recommended_titles)

#     return recommended_products

def get_recommendations(last_viewed_titles, top_n=5):
    """
    Recommend products from the same category as the last viewed products.
    last_viewed_products: queryset of Products
    """
    recommended_products = Products.objects.none()  # empty queryset

    for product in last_viewed_titles:
        # Fetch top_n products from the same category excluding the product itself
        qs = Products.objects.filter(category=product.category).exclude(id=product.id)[:top_n]
        recommended_products = recommended_products | qs  # union querysets

    # Remove duplicates and limit total results
    recommended_products = recommended_products.distinct()[:top_n]

    return recommended_products


def get_recommendations_ml(last_viewed_products, top_n=5):
    """
    last_viewed_products: queryset of Products
    top_n: number of recommended products
    """
    # Fetch titles of products in DB
    db_titles = set(Products.objects.values_list('title', flat=True))

    recommended_scores = {}

    for product in last_viewed_products:
        title = product.product.title
        if title in item_similarity.index:
            # Get similarity scores for this product
            sim_scores = item_similarity.loc[title]

            # Keep only products that exist in DB and exclude itself
            sim_scores = sim_scores[sim_scores.index.isin(db_titles)]
            if title in sim_scores.index:
                sim_scores = sim_scores.drop(title)

            # Accumulate similarity scores
            for t, score in sim_scores.items():
                if t in recommended_scores:
                    recommended_scores[t] += score
                else:
                    recommended_scores[t] = score

    # Sort by total similarity score descending
    sorted_titles = sorted(recommended_scores.items(), key=lambda x: x[1], reverse=True)
    sorted_titles = [t for t, s in sorted_titles][:top_n]

    # Fetch corresponding Products objects
    recommended_products = Products.objects.filter(title__in=sorted_titles)

    return recommended_products
