import re
import ast
import json
import numpy as np
from operator import itemgetter
from solutions.llm import cypher_llm, llm
from langchain import PromptTemplate
from langchain.load import dumps, loads
from langchain_core.runnables import chain
from solutions.tools.vector import neo4jvector
from langchain_core.output_parsers import StrOutputParser
from solutions.tools.silhouetteScore import get_K_relevant_records

FETCH_K_DOCUMENTS_FOR_EACH_QUERY = 3
MINIMUM_CUTOFF_THRESHOLD:float = 0.0

# Multi Query: Different Perspectives
MULTI_QUERY_RETRIVAL_TEMPLATE = """
As an AI language model assistant for Northwind E-commerce Store, your task is to generate {n} different versions of the given user question in clear English. 

Ensure that the generated output does not include any additional introductory or clarification phrases! 

Ensure to enclosed all {n} generated versions in python List brackets separated by commas

Ensure to include original question as well in the output list in English

Ensure each version is in clear English language

{chat_history}

Human: {human_input}

Chatbot:
"""

JSON_FORMAT_TEMPLATE = """
Return the JSON string with correct syntax containing a list of strings having no objects. The output should be formatted in a single line with in the square brackets and no additional details and no  styling.
{input}
"""

MAX_TRIES_TO_CORRECT_JSON_STRING = 3

neo4jvectorMultiQueryRetrieverTopK =  neo4jvector.as_retriever(search_kwargs={"k": FETCH_K_DOCUMENTS_FOR_EACH_QUERY})
neo4jvectorMultiQueryRetrieverThreshold = neo4jvector.as_retriever(search_type="similarity_score_threshold", 
                                                                   search_kwargs={'score_threshold': MINIMUM_CUTOFF_THRESHOLD})


def get_unique_union(documents: list[list]):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))

    loaded_docs =  [loads(doc) for doc in unique_docs]
    # Return
    return get_unique_docs(loaded_docs)

def clean_json(product_json:str)->str:
    json_str = product_json.replace("\r", '')
    json_str = json_str.replace("\n", '')
    json_str = json_str.replace("\'", '')
    return json_str

def get_unique_docs(documents: list):
    unique_product_ids = set()
    unique_product_and_sim_score = []
    for doc in documents:
        page_content_str = clean_json(doc.page_content)
        doc_object = json.loads(page_content_str)
        doc_product_id = doc_object["ProductID"]
        if doc_product_id not in unique_product_ids:
            unique_product_ids.add(doc_product_id)
            unique_product_and_sim_score.append(doc)
    return unique_product_and_sim_score

def get_unique_documents(documents: list):
    unique_product_ids = set()
    unique_product_and_sim_score = []
    for doc in documents:
        page_content_str = clean_json(doc.page_content)
        doc_object = json.loads(page_content_str)
        doc_product_id = doc_object["ProductID"]
        doc_sim_score = doc.metadata["simScore"]
        if doc_product_id not in unique_product_ids:
            unique_product_ids.add(doc_product_id)
            unique_product_and_sim_score.append(
                {
                    "ProductID":doc_product_id, 
                    "simScore":doc_sim_score,
                    "doc": doc
                }
            )
    return unique_product_and_sim_score

def process_query(query:str):
    documents = neo4jvectorMultiQueryRetrieverThreshold.get_relevant_documents(query)
    unique_documets = get_unique_documents(documents)
    return get_K_relevant_records(unique_documets);

def listMapper(queries:list):
    return map(process_query,queries)

def parse_list(text:str):
    pattern = r"\[([^\[\]]*?)\]"
    matches = re.findall(pattern, text)
    if matches:
        return matches;
    return None

def format_generated_queries(q:str, no_of_tries=0):
    try:
        list_of_queries = ast.literal_eval(q)
    except Exception as e:
        if(no_of_tries<MAX_TRIES_TO_CORRECT_JSON_STRING):
            correct_format_chain = (PromptTemplate.from_template(template=JSON_FORMAT_TEMPLATE) | cypher_llm)
            formated_query = format_generated_queries(correct_format_chain.invoke({"input":q}), no_of_tries+1)
            return formated_query
        else:
            custom_parsed_list = parse_list(q)
            if custom_parsed_list:
                return custom_parsed_list
            else:
                raise e
    return  list_of_queries 

def multi_retriever_query():
    return (
        {
            "question": itemgetter("question"), 
            "n":itemgetter("k"), 
        } | PromptTemplate.from_template(MULTI_QUERY_RETRIVAL_TEMPLATE) 
        | cypher_llm
        | StrOutputParser() 
        | format_generated_queries
        | listMapper
        #| neo4jvectorMultiQueryRetrieverTopK.map()
        | get_unique_union
    )