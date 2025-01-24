import pandas

from utils.loaders import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
from utils.class_databasemanager import DatabaseManager


def plot_embeddings_2d(embeddings, labels, texts):

    tsne = TSNE(n_components=2, random_state=42, perplexity=5)
    embeddings_2d = tsne.fit_transform(embeddings)

    plt.figure(figsize=(10, 7))
    scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], c=labels, cmap='tab10', s=60)
    plt.colorbar(scatter, label="Cluster")

    for i, text in enumerate(texts):
        plt.annotate(f"{labels[i]}: " + text, (embeddings_2d[i, 0], embeddings_2d[i, 1]), fontsize=9, alpha=0.7)

    plt.title("2D Visualisation of Embeddings")
    plt.grid(True)
    plt.show()


def ravel(d):
    d_ravel = {}
    for sport_name in d.keys():
        for category_name in d[sport_name].keys():
            for tournament_name in d[sport_name][category_name].keys():
                k = sport_name + " " + category_name + " " + tournament_name
                d_ravel[k] = d[sport_name][category_name][tournament_name]
    return d_ravel


urls = [
    load_json("winamax_urls.json"),
    load_json("zebet_urls.json"),
    load_json("netbet_urls.json"),
]

sports = []
for url in urls:
    sports += url.keys()
n = len(sports)

print(sports)
np.random.seed(42)
np.random.shuffle(sports)
sports = list(set(sports))
"""
db = DatabaseManager("../../data/database.csv")
print(db.data.keys())
sports = db.data["Home Team Unparse"] + pandas.DataFrame([" vs "] * len(db.data.index), columns=["vs"])["vs"] +  db.data["Away Team Unparse"]
sports = np.unique(list(sports))[:-1]
print(sports)
"""
# model name: 'all-MiniLM-L6-v2', 'paraphrase-albert-small-v2'
model = SentenceTransformer("../models/all-MiniLM-L6-v2")
# model.save("../models/all-MiniLM-L6-v2")

embeddings = model.encode(sports)
clustering = DBSCAN(eps=0.1, min_samples=1, metric='cosine').fit(embeddings)

match = {}
for sport, label in zip(sports, clustering.labels_):
    if label not in match.keys():
        match[label] = []
    match[label].append(sport)

for id, sport in match.items():
    print(id, sport)

plot_embeddings_2d(embeddings, clustering.labels_, sports)
