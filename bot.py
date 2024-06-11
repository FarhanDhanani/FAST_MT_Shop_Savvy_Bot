import re
import json
import time
import streamlit as st
from time import sleep
from utils import MessageType
from utils import list_product_items, list_cart_items, get_cart_items
from utils import write_message, render_messages, display_product_details
#from solutions.agent import generate_response
from operator import itemgetter
from langchain import PromptTemplate
from langchain_core.runnables import chain
from langchain.chains import LLMChain, SequentialChain

from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever

from solutions.llm import cypher_llm, llm
from solutions.graph import run_cypher_statment

from solutions.tools.video_search import user_query_search_in_video
from solutions.tools.multiQueryRetriever import multi_retriever_query
from solutions.tools.vector import neo4jSimillaritySearchUsingK, retriever
from solutions.tools.commands import COMMAND_01, COMMAND_02 ,COMMAND_03, COMMAND_04, COMMAND_05
from solutions.tools.pintrest_video_downloader import process_video_file
from solutions.tools.cypher import generate_cypher, get_cypher_prompt, get_graph_scheema, CYPHER_GENERATION_TEMPLATE, CYPHER_GENERATION_PRODUCT_DETAILS_TEMPLATE

BOT_PROMPT = """
You are a shopping assistant AI tasked with helping users find products and provide information about them. 
Given a user query and provided context, generate a short and to the point answer response providing assistance and information about products.

context:
{context}

question:
{question}
"""

VIDEO_QUERY_PROCESSING_PROMPT = """
Given a user query containing a query and a URL, extract the query and URL parts and return them as a JSON object with no extra formatting or styling
query:
{question}

OUTPUT:
"""
# tag::setup[]
# Page Config
st.set_page_config("Ebert", page_icon=":movie_camera:")
# end::setup[]

st.write("# Welcome to AI Shooping! 👋")

# st.markdown("""
# This component supports **markdown formatting**, which is handy.

# [Check out their documentation](https://docs.streamlit.io) for more information on how to get started.
# """)

# tag::session[]
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Hi, I'm the ShopSavvy Bot!  How can I help you?", 
            "type":MessageType.SIMPLE.value
        }
    ]

if "cart_items" not in st.session_state:
    st.session_state.cart_items = []
    # [
    #     {
    #         "ProductName": "chai",
    #         "UnitPrice": 18.00,
    #         "QuantityPerUnit": 1,
    #         "NumberOfUnitOrdered": 1,
    #         "CategoryID":1
    #     },
    #     {
    #         "ProductName": "ii",
    #         "UnitPrice": 18.00,
    #         "QuantityPerUnit": 1,
    #         "NumberOfUnitOrdered": 1
    #         "CategoryID":1
    #     }
    # ]
# end::session[]

def generate_answer_dialog(context:str, question:str):
    return (
        {
                "context": itemgetter("context"),
                "question": itemgetter("question") 
        } 
        | PromptTemplate.from_template(template=BOT_PROMPT)
        | llm
    )

def get_cypher_chain(cypher_template:str):
    return (
        {
            "context": multi_retriever_query(),
            "schema": itemgetter('schema'),
            "question": itemgetter("question")
        }
        | PromptTemplate.from_template(template=cypher_template)
        | cypher_llm 
        | run_cypher_statment
    ) 

def query_processor_dialogue_generation(message:str, cypher_template:str):
    cypher_chain = get_cypher_chain(cypher_template=cypher_template)
    cypher_response = cypher_chain.invoke({
        "question":message,
        "k":1,
        "schema":get_graph_scheema()
    })
    dialog_response_chain = generate_answer_dialog(context=cypher_response, question=message)
    dialog_response =  dialog_response_chain.invoke({
        "question":message,
        "context":cypher_response
    })
    return dialog_response

def query_processor_product_get_details(message:str, cypher_template:str):
    cypher_chain = get_cypher_chain(cypher_template=cypher_template)
    cypher_response = cypher_chain.invoke({
        "question":message,
        "k":1,
        "schema":get_graph_scheema()
    })
    return cypher_response

def query_processor_for_video(message:str):
    regex_pattern_for_url = r'\bhttps?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/\S*)?\b'
    video_url_extract = re.search(regex_pattern_for_url, message)
    if video_url_extract:
        video_url = video_url_extract.group(0)

        query = message.replace(video_url, "")
        query = query.replace(COMMAND_05, "")
        query = query.strip()
   
        is_processed_successfully = process_video_file(video_url, "abc.mp4")

        if is_processed_successfully:
            product_details = user_query_search_in_video(query)
            display_product_details(product_details=product_details,
                                    content="",
                                    grace_message="We apologize, but we couldn't find the mentioned products in our store.")
        else:
            write_message('assistant', "Appologies, there might be an issue, I can't access the video in provided video url")
    else:
        write_message('assistant', "Appologies, there might be an issue, I can't find and process the video url")
    return

def query_processor(message:str)->str:
    if((re.search(COMMAND_01, message)) or (re.search(COMMAND_02, message))):
        product_details = query_processor_product_get_details(message, 
                                                              CYPHER_GENERATION_PRODUCT_DETAILS_TEMPLATE)
        display_product_details(product_details=product_details,
                                content="",
                                grace_message="We apologize, but we couldn't find the mentioned products in our store.")
    elif((re.search(COMMAND_03, message)) or (re.search(COMMAND_04, message))):
        list_cart_items(get_cart_items())

    elif(re.search(COMMAND_05, message)):
        query_processor_for_video(message)
    else:
        dialog_response = query_processor_dialogue_generation(message, 
                                                              CYPHER_GENERATION_TEMPLATE)
        write_message('assistant', dialog_response)
    return ;


# tag::submit[]
# Submit handler
def handle_submit(message):
    """
    Submit handler:

    You will modify this method to talk with an LLM and provide
    context using data from Neo4j.
    """

    # Handle the response
    with st.spinner('Thinking...'):
        # # TODO: Replace this with a call to your LLM
        #list_product_items('assistant', message, items)
        #response = generate_cypher(message)
        query_processor(message)
 
        
    return
# end::submit[]

with st.sidebar:
    st.header("CHAT COMMANDS")
    st.subheader("Command to get Product Details")
    st.write(COMMAND_01+"\n")
    st.write(COMMAND_02+"\n")
    st.subheader("Command to view Cart Details")
    st.write(COMMAND_03+"\n")
    st.write(COMMAND_04+"\n")
    st.subheader("Command to pose Video Query")
    st.write(COMMAND_05)

# tag::chat[]
# Display messages in Session State
render_messages(st.session_state.messages)


# Handle any user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)
# end::chat[]