import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from product.models import Product

class Command(BaseCommand):
    help = "Train product similarity matrix for recommendations based on catalog"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching all products...")
        products = Product.objects.all()
        if not products.exists():
            self.stdout.write(self.style.WARNING("No products found. Exiting."))
            return

        # Create a dataframe with text features (title + description + category)
        df = pd.DataFrame(list(products.values('id', 'title', 'description', 'category')))
        df['text'] = df['title'] + ' ' + df['description'] + ' ' + df['category']

        self.stdout.write("Computing TF-IDF vectors...")
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['text'])

        self.stdout.write("Computing item-item similarity matrix...")
        similarity_matrix = cosine_similarity(tfidf_matrix)
        similarity_df = pd.DataFrame(similarity_matrix, index=df['title'], columns=df['title'])

        # Save matrix
        models_dir = os.path.join(settings.BASE_DIR, "models")
        os.makedirs(models_dir, exist_ok=True)
        path = os.path.join(models_dir, "item_similarity.pkl")
        similarity_df.to_pickle(path)

        self.stdout.write(self.style.SUCCESS(f"Catalog-based similarity matrix saved to {path}"))
