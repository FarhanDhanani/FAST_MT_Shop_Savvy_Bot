import glob
import json
from PIL import Image
from solutions.graph import get_k_simillar_product_to_image
from sentence_transformers import SentenceTransformer, util

FOLDER_NAME = "data"
ROOT_PATH = "./"+FOLDER_NAME+"/"
FILE_NAME_HEAD = "frame"

MODEL_PATH = './models/ST-clip'

model = SentenceTransformer(MODEL_PATH)

def read_downloaded_files(path:str)-> list:
    images = []
    for f in glob.iglob(path):
        image = Image.open(f)
        images.append(image)

    return images

def find_K_relevant_images_in_video(query:str, k:int=1)->list[str]:
    images = read_downloaded_files(ROOT_PATH+"/*")
    image_embeddings = model.encode([image for image in images])
    query_embedding = model.encode(query)
    results = util.semantic_search(query_embedding, image_embeddings, top_k=k)[0]
    relevant_file_paths = []
    for result in results:
        file_path = images[result['corpus_id']].filename
        relevant_file_paths.append(file_path)

    return relevant_file_paths

def user_query_search_in_video(query:str, k_for_relevant_frames:int=1):
    relevant_file_paths = find_K_relevant_images_in_video(query, k_for_relevant_frames)
    print(relevant_file_paths)
    responses = []
    for file_path in relevant_file_paths:
        image = Image.open(file_path)
        image_embeddings = model.encode(image)
        response = get_k_simillar_product_to_image(image_embeddings)
        if responses:
            responses.append(response)
        else:
            responses = response
    return json.dumps(responses)