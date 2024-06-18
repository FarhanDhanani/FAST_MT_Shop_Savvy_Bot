from config import Config
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from solutions.llm import llm, cypher_llm

from langchain.chains.question_answering import load_qa_chain
from solutions.tools.cypher import CYPHER_GENERATION_TEMPLATE, CYPHER_GENERATION_PRODUCT_DETAILS_TEMPLATE
from solutions.tools.multiQueryRetriever import MULTI_QUERY_RETRIVAL_TEMPLATE  

BOT_PROMPT = """
You are a shopping assistant AI tasked with helping users find products and provide information about them. 
Given a user query and provided context, generate a short and to the point answer response providing assistance and information about products.

{chat_history}

Graph Database Output: {context}

Human: {human_input}

Chatbot:
"""

bot_memory = ConversationBufferWindowMemory(memory_key="chat_history", input_key="human_input", k=Config.MEMORY_MSG_BUFFER)
bot_prompt = PromptTemplate(
    input_variables=["chat_history", "human_input", "context"], template=BOT_PROMPT
)

llm_chain = LLMChain(
    llm=llm,
    prompt=bot_prompt,
    verbose=True,
    memory=bot_memory,
)

cypher_prompt = PromptTemplate(
        input_variables=["schema", "chat_history", "human_input", "context"], template=CYPHER_GENERATION_TEMPLATE)
cypher_chain = load_qa_chain(
    cypher_llm, chain_type="stuff", memory=bot_memory, prompt=cypher_prompt
)

cypher_product_details_prompt = PromptTemplate(
        input_variables=["schema", "chat_history", "human_input", "context"], template=CYPHER_GENERATION_PRODUCT_DETAILS_TEMPLATE)
cypher_chain_product_details = load_qa_chain(
    cypher_llm, chain_type="stuff", memory=bot_memory, prompt=cypher_product_details_prompt
)

multi_retriever_query_prompt = PromptTemplate(
    input_variables=["chat_history", "n", "human_input"],
    template=MULTI_QUERY_RETRIVAL_TEMPLATE
)
multi_retriever_query_chain = LLMChain(
    llm=cypher_llm,
    prompt=multi_retriever_query_prompt,
    verbose=True,
    memory=bot_memory,
)