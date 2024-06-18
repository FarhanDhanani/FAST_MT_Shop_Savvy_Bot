import re
import streamlit as st
from utils import MessageType
from utils import list_cart_items, get_cart_items
from utils import write_message, render_messages, display_product_details

from solutions.graph import run_cypher_statment

from solutions.tools.video_search import user_query_search_in_video
from solutions.tools.multiQueryRetriever import format_generated_queries, get_unique_union, listMapper
from solutions.tools.commands import COMMAND_01, COMMAND_02 ,COMMAND_03, COMMAND_04, COMMAND_05
from solutions.tools.pintrest_video_downloader import process_video_file
from solutions.tools.cypher import get_graph_scheema

from solutions.memory import llm_chain, cypher_chain, cypher_chain_product_details, multi_retriever_query_chain
from config import Config

VIDEO_QUERY_PROCESSING_PROMPT = """
Given a user query containing a query and a URL, extract the query and URL parts and return them as a JSON object with no extra formatting or styling
query:
{question}

OUTPUT:
"""

st.set_page_config("Shop AI", page_icon=":movie_camera:")


st.write("# Welcome to AI Shooping! 👋")

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

def generate_answer_dialog(context, query:str):
    return llm_chain({"context": context, "human_input": query}, return_only_outputs=True)


def multi_retriever_query_with_memory(question: str):
    response = multi_retriever_query_chain({"n": Config.N_VARIANTS_OF_MULTI_QUERY, "human_input": question}, return_only_outputs=True)
    formated_response = format_generated_queries(q=response['text'])
    return formated_response

def query_processor_dialogue_generation(message:str):
    multi_query = multi_retriever_query_with_memory(question=message)
    docs = get_unique_union(listMapper(multi_query))
    schema = get_graph_scheema()
    cypher_query = cypher_chain(
        {
            "input_documents": docs, 
            "human_input":  message + " | " + " | ".join(multi_query), 
            "schema":schema
        }, 
        return_only_outputs=True
    )
    cypher_response = run_cypher_statment(cypher_query["output_text"])

    dialog_response = generate_answer_dialog(context=cypher_response, 
                                            query=message +
                                            " based on the response from the Database")
    return dialog_response['text']

def query_processor_product_get_details(message:str):
    multi_query = multi_retriever_query_with_memory(question=message)
    docs = get_unique_union(listMapper(multi_query))
    schema = get_graph_scheema()
    cypher_query = cypher_chain_product_details(
        {
            "input_documents": docs, 
            "human_input": message, 
            "schema":schema
        }, 
        return_only_outputs=True
    )
    cypher_response = run_cypher_statment(cypher_query["output_text"])
    return cypher_response

def query_processor_for_video(message:str):
    regex_pattern_for_url = r'\bhttps?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\/\S*)?\b'
    video_url_extract = re.search(regex_pattern_for_url, message)
    if video_url_extract:
        video_url = video_url_extract.group(0)

        query = message.replace(video_url, "")
        query = query.replace(COMMAND_05, "")
        query = query.strip()
   
        is_processed_successfully = process_video_file(video_url, Config.SAVE_VIDEO_WITH_NAME)

        if is_processed_successfully:
            product_details = user_query_search_in_video(query, Config.FIND_K_RELEVANT_FRAMES_IN_VIDEO)
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
        product_details = query_processor_product_get_details(message)
        display_product_details(product_details=product_details,
                                content="",
                                grace_message="We apologize, but we couldn't find the mentioned products in our store.")
    elif((re.search(COMMAND_03, message)) or (re.search(COMMAND_04, message))):
        list_cart_items(get_cart_items())

    elif(re.search(COMMAND_05, message)):
        query_processor_for_video(message)
    else:
        dialog_response = query_processor_dialogue_generation(message)
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