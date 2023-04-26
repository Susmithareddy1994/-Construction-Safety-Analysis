# -*- coding: utf-8 -*-
"""Construction Safety Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1q0__iilKOqgdBFIzoP0SqKWsTaBguIQS
"""

# Imported Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

#Converted CSV file into Data Frame Using Pandas Library
df =pd.read_csv("/content/combined_data (2).csv")
df.head(6)

# Data Information
df.info()

#Checking the Null Values in the Dataset
df.isnull().sum()

df['keywords']

#Columns in the Dataset
df.columns

features = ['keywords']

df = df.dropna(subset = features)

df.isnull().sum()

# Commented out IPython magic to ensure Python compatibility.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

import re
import string
import nltk
from nltk.corpus import stopwords
nltk.download('punkt')

def preprocess_text(text: str, remove_stopwords: bool) -> str:
    """This utility function sanitizes a string by:
    - removing links
    - removing special characters
    - removing numbers
    - removing stopwords
    - transforming in lowercase
    - removing excessive whitespaces
    Args:
        text (str): the input text you want to clean
        remove_stopwords (bool): whether or not to remove stopwords
    Returns:
        str: the cleaned text
    """

    # remove links
    text = re.sub(r"http\S+", "", text)
    # remove special chars and numbers
    text = re.sub("[^A-Za-z]+", " ", text)
    # remove stopwords
    if remove_stopwords:
        # 1. tokenize
        tokens = nltk.word_tokenize(text)
        # 2. check if stopword
        tokens = [w for w in tokens if not w.lower() in stopwords.words("english")]
        # 3. join back together
        text = " ".join(tokens)
    # return text in lower case and stripped of whitespaces
    text = text.lower().strip()
    return text

df['cleaned'] = df['keywords'].apply(lambda x: preprocess_text(x, remove_stopwords=True))

df.head(3)

# initialize the vectorizer
vectorizer = TfidfVectorizer(sublinear_tf=True, min_df=5, max_df=0.95)
# fit_transform applies TF-IDF to clean texts - we save the array of vectors in X
X = vectorizer.fit_transform(df['cleaned'])

Sum_of_squared_distances = []
K = range(1,10)
for k in K:
    km = KMeans(init="k-means++", n_clusters=k)
    km = km.fit(X)
    Sum_of_squared_distances.append(km.inertia_)
ax = sns.lineplot(x=K, y=Sum_of_squared_distances)
ax.lines[0].set_linestyle("--")
plt.xlabel('k')
plt.ylabel('Sum of Squared Distances')
plt.title('Elbow Method For Optimal k')
plt.show()

from sklearn.cluster import KMeans

# initialize kmeans with 3 centroids
kmeans = KMeans(n_clusters= 3, random_state=42)
# fit the model
kmeans.fit(X)
# store cluster labels in a variable
clusters = kmeans.labels_

from sklearn.decomposition import PCA

# initialize PCA with 2 components
pca = PCA(n_components=2, random_state=42)
# pass our X to the pca and store the reduced vectors into pca_vecs
pca_vecs = pca.fit_transform(X.toarray())
# save our two dimensions into x0 and x1
x0 = pca_vecs[:, 0]
x1 = pca_vecs[:, 1]

# assign clusters and pca vectors to our dataframe 
df['cluster'] = clusters
df['x0'] = x0
df['x1'] = x1

from numba import none
from sklearn.cluster import KMeans
# initialize kmeans with 3 centroids
kmeans = KMeans(n_clusters= 3, random_state= 0)
# fit the model
kmeans.fit(X)
# store cluster labels in a variable
clusters = kmeans.labels_

def get_top_keywords(n_terms):
    """This function returns the keywords for each centroid of the KMeans"""
    df = pd.DataFrame(X.todense()).groupby(clusters).mean() # groups the TF-IDF vector by cluster
    terms = vectorizer.get_feature_names_out() # access tf-idf terms
    for i,r in df.iterrows():
        print('\nCluster {}'.format(i))
        print(','.join([terms[t] for t in np.argsort(r)[-n_terms:]])) # for each row of the dataframe, find the n terms that have the highest tf idf score
            
get_top_keywords(20)

# map clusters to appropriate labels 
cluster_map = {0: "Falls", 1: "Struck by Object", 2: "Electrocutions"}
# apply mapping
df['cluster'] = df['cluster'].map(cluster_map)

df

# set image size
plt.figure(figsize=(8,8))
# set a title
plt.title("TF-IDF + KMeans Clustering", fontdict={"fontsize": 9})
# set axes names
plt.xlabel("X0", fontdict={"fontsize": 8})
plt.ylabel("X1", fontdict={"fontsize": 8})
# create scatter plot with seaborn, where hue is the class used to group the data
sns.scatterplot(data=df, x='x0', y='x1', hue='cluster', palette="viridis")
plt.show()

df.cluster.value_counts()

100.* df.cluster.value_counts() / len(df.cluster)

"""# Falls  - 65.25%
#Struck by Object - 17.82%
#Electrocutions - 16.91%
"""