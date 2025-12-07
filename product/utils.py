import pandas as pd
import os
from django.conf import settings
from .models import Product, OrderItem

# Load precomputed similarity matrix
item_similarity = pd.read_pickle(os.path.join(settings.BASE_DIR, "models", "item_similarity.pkl"))

def get_recommendations_from_transactions(order_items, top_n=5):
    """
    Simple category-based recommendation using products from successful transactions.
    order_items: queryset of OrderItem
    """
    recommended_products = Product.objects.none()
    
    products_in_orders = [item.product for item in order_items if item.product is not None]
    
    for product in products_in_orders:
        qs = Product.objects.filter(category=product.category).exclude(id=product.id)
        recommended_products = recommended_products | qs

    recommended_products = recommended_products.distinct()[:top_n]
    return recommended_products


def get_recommendations_ml_from_transactions(order_items, top_n=5):
    """
    ML-based recommendation using precomputed item similarity.
    order_items: queryset of OrderItem
    top_n: number of recommended products
    """
    recommended_scores = {}
    db_titles = set(Product.objects.values_list('title', flat=True))
    
    # Extract product titles from order items
    purchased_titles = [item.product.title for item in order_items if item.product is not None]

    for title in purchased_titles:
        if title in item_similarity.index:
            # similarity scores for this product
            sim_scores = item_similarity.loc[title]
            # Only keep products in DB, exclude the product itself
            sim_scores = sim_scores[sim_scores.index.isin(db_titles)]
            sim_scores = sim_scores.drop(title, errors='ignore')
            
            for t, score in sim_scores.items():
                recommended_scores[t] = recommended_scores.get(t, 0) + score

    # Sort by accumulated score
    sorted_titles = sorted(recommended_scores.items(), key=lambda x: x[1], reverse=True)
    top_titles = [t for t, _ in sorted_titles][:top_n]

    recommended_products = Product.objects.filter(title__in=top_titles)
    return recommended_products