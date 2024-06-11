import json
import streamlit as st
from langchain_core.runnables import chain
from langchain_community.graphs import Neo4jGraph

IMAGE_INDEX_NAME = "productsSTImageIndex"

graph = Neo4jGraph(
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
)

@chain
def run_cypher_statment(
    cypherQuery
    ):
    response = graph.query(cypherQuery)
    return json.dumps(response);

def get_simple_content_based_query(category_ids: list[int], product_list:list[int]):
    query = f"""
    MATCH (p:Product)
    WHERE (p.CategoryID IN {category_ids}) AND (NOT p.ProductName IN {product_list})
    RETURN p LIMIT 1
    """
    return query

def simple_content_based_filtering(category_ids: list[int], product_names: list[str]):
    query = get_simple_content_based_query(category_ids, product_names)
    response = graph.query(query)
    return json.dumps(response)

def get_k_simillar_product_to_image(image_embeddings, k:int=1)->str:
    image_embeddings_str = "[" + ", ".join(str(elem) for elem in image_embeddings) + "]"
    query = f"""
    MATCH (p:Product)
    CALL db.index.vector.queryNodes('{IMAGE_INDEX_NAME}', {k}, {image_embeddings_str})
    YIELD node, score
    WHERE p.ProductID= node.ProductID 
    RETURN p
    """
    response = graph.query(query)
    return response