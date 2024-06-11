import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def finding_optimal_k_via_silhouette_methode(cosine_scores:[float])-> [float]:
    silhouette_scores = []
    k_values = []

    # Loop the range of k values to test
    # we have set init_k=2 because SILHOUETTE COEFFICIENT needs atleast two
    # clusters to begin its processing.
    init_k = 2
    max_k = len(cosine_scores)

    for k in range(init_k, max_k):
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(cosine_scores)
        silhouette_avg = silhouette_score(cosine_scores, labels)
        silhouette_scores.append(silhouette_avg)
        k_values.append(k)
    return k_values[np.argmax(silhouette_scores)]

def kmeans_with_silhouette_methode(n_clusters:int, cosine_scores:[float]) -> [float]:
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(cosine_scores)

    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    largest_centroid_index = np.argmax(centroids)
    list_of_relevant_cosine_scores = []

    for point,label in zip (cosine_scores, labels):
        if(label==largest_centroid_index):
            list_of_relevant_cosine_scores.append(point)
    return list_of_relevant_cosine_scores

def get_list_of_cosine_scores_from_document_map(retrieved_records:list):
    cosine_scores = []
    for doc in retrieved_records:
        cosine_scores.append(doc["simScore"])
    return np.array(cosine_scores).reshape(-1,1)

def get_relevant_records_for_selected_cosine_scores(retrieved_records:list, cosine_scores:list):
    relevant_docs = []
    for doc in retrieved_records:
        if doc["simScore"] in cosine_scores:
            relevant_docs.append(doc["doc"])
    return relevant_docs

def get_K_relevant_records(retrieved_records:list):
    cosine_scores = get_list_of_cosine_scores_from_document_map(retrieved_records)
    
    list_of_relevant_cosine_scores = kmeans_with_silhouette_methode(
        finding_optimal_k_via_silhouette_methode(cosine_scores), 
        cosine_scores)
    return get_relevant_records_for_selected_cosine_scores(retrieved_records, list_of_relevant_cosine_scores)