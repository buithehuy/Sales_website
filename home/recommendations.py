import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from home.models import Item
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from home.models import OrderItem

# Load items data
items = Item.objects.all()
data = [
    {
        'title': item.title,
        'description': item.description_long,
        'category': item.category
    }
    for item in items
]

df = pd.DataFrame(data)

# TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['description'])

# Compute the cosine similarity matrix
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Mapping from item titles to index
indices = pd.Series(df.index, index=df['title']).drop_duplicates()

# Function to get recommendations based on item title
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]  # Get the top 10 recommendations
    item_indices = [i[0] for i in sim_scores]
    return df['title'].iloc[item_indices]



# Load order data
orders = OrderItem.objects.all()
data = [
    {
        'user_id': order.user.id,
        'item_id': order.item.id,
        'quantity': order.quantity
    }
    for order in orders
]

df1 = pd.DataFrame(data)

# Create pivot table
pivot_table = df1.pivot(index='item_id', columns='user_id', values='quantity').fillna(0)
sparse_matrix = csr_matrix(pivot_table)

# Fit KNN model
model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
model_knn.fit(sparse_matrix)

# Function to get recommendations based on item ID
def get_knn_recommendations(item_id, model=model_knn, data=pivot_table, n_recommendations=2):
    distances, indices = model.kneighbors(data.loc[item_id, :].values.reshape(1, -1), n_neighbors=n_recommendations+1)
    recommendations = data.index[indices.flatten()].tolist()
    return recommendations[1:]  # Exclude the queried item itself
