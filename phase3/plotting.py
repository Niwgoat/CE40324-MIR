import seaborn as sns

from yellowbrick.cluster import kelbow_visualizer, intercluster_distance
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# from .preprocess import *
from phase3.clustering import return_clustered_csv, kmeans, load_data, vectorize, get_res, grid_search, GMM, \
    hierarchical, return_clustered_csv_gmm

sns.set_theme()
sns.set_style("dark")

# loading data
data, major_labels, minor_labels = load_data(stem=False, lemmatize=True, remove_conjunctions=True)
tfidf, w2v = vectorize(data, w2v_options=dict(size=64, iter=128, min_count=2))
pca_tfidf = PCA(64, random_state=666).fit_transform(tfidf.toarray())

# cluster diagrams
get_res(return_clustered_csv(data, kmeans, pca_tfidf, w2v, options=dict(random_state=666), save=False), data=data)

# elbow charts and Inter-cluster Distance Maps
print("TF-IDF:\n")
_ = kelbow_visualizer(KMeans(random_state=666), pca_tfidf, k=(2, 16), metric='silhouette')
_ = intercluster_distance(KMeans(n_clusters=5, random_state=666), pca_tfidf)
print("\nW2V:\n")
_ = kelbow_visualizer(KMeans(random_state=666), w2v, k=(2, 16), metric='silhouette')
_ = intercluster_distance(KMeans(n_clusters=5, random_state=666), w2v)

get_res(gmm_res=return_clustered_csv(
    data,
    GMM,
    tfidf=pca_tfidf, w2v=w2v,
    options=dict(n_components=len(major_labels), random_state=666),
    save=True), data=data)

get_res(hier_res=return_clustered_csv(
    data,
    hierarchical,
    tfidf=pca_tfidf, w2v=w2v,
    options=dict(n_components=len(major_labels)),
    save=True), data=data)


get_res(gmm_res=return_clustered_csv_gmm(
    data,
    GMM,
    tfidf=pca_tfidf, w2v=w2v,
    options=dict(n_components=len(major_labels), random_state=666),
    options_tfidf=dict(covariance_type='full', max_iter=600),
    options_w2v=dict(covariance_type='full', max_iter=600),
    save=True), data=data)
