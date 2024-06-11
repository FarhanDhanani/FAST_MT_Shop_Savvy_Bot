import numpy as np
from sklearn.cluster import KMeans
from kneed import KneeLocator
from solutions.tools.multiQueryRetriever import get_list_of_cosine_scores_from_document_map
from solutions.tools.multiQueryRetriever import get_relevant_records_for_selected_cosine_scores

def finding_sse(cosine_scores:[float])-> [float]:
    sse = []
    k_values = []
    
    # Loop the range of k values to test
    init_k = 1
    max_k = len(cosine_scores)

    for k in range(init_k, max_k):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(cosine_scores)
        sse.append(kmeans.inertia_)
        k_values.append(k)
    return sse;
    

def knee_locator(sse:list[float]) -> int:
    k_values = list(range(1, len(sse)+1))
    return KneeLocator(
    k_values,
    sse,
    curve='convex',
    direction='decreasing',
    interp_method='interp1d',
    ).knee

def kmeans_with_elbow(n_clusters:int, cosine_scores:[float]) -> [float]:
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

def get_K_relevant_records(retrieved_records:list):
    cosine_scores = get_list_of_cosine_scores_from_document_map(retrieved_records)
    
    list_of_relevant_cosine_scores = kmeans_with_elbow(
        knee_locator(
            finding_sse(cosine_scores)
        ), 
        cosine_scores)
    return get_relevant_records_for_selected_cosine_scores(list_of_relevant_cosine_scores, cosine_scores)
    