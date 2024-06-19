import streamlit as st
from config import Config
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQA
from solutions.llm import llm
from langchain_core.runnables import chain
from solutions.embedder import embeddings

INDEX_NAME_LOCAL_MXBAI_EMBEDDINGS = "productsMetaIndex"
EMBEDDING_NODE_PROPERTY_LOCAL_MXBAI_EMBEDDINGS = "mxbai-embeddings"

INDEX_NAME_OPEN_AI_TEXT_EMBEDDING_3_SMALL = "productsMetaIndex2"
EMBEDDING_NODE_PROPERTY_OPEN_AI_TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"

index_name = INDEX_NAME_OPEN_AI_TEXT_EMBEDDING_3_SMALL if Config.USE_OPEN_AI_EMBEDDER else INDEX_NAME_LOCAL_MXBAI_EMBEDDINGS
embedding_node_property = EMBEDDING_NODE_PROPERTY_OPEN_AI_TEXT_EMBEDDING_3_SMALL if Config.USE_OPEN_AI_EMBEDDER else EMBEDDING_NODE_PROPERTY_LOCAL_MXBAI_EMBEDDINGS

# tag::vector[]
neo4jvector = Neo4jVector.from_existing_index(
    embeddings,                                         # <1>
    url=st.secrets["NEO4J_URI"],                        # <2>
    username=st.secrets["NEO4J_USERNAME"],              # <3>
    password=st.secrets["NEO4J_PASSWORD"],              # <4>
    index_name=index_name,                              # <5>
    node_label="Product",                               # <6>
    text_node_property="ProductMetaInfo",               # <7>
    embedding_node_property=embedding_node_property,    # <8>
    retrieval_query="""
RETURN
    node.ProductMetaInfo AS text,
    score,
    {
        QuantityPerUnit: node.QuantityPerUnit,
        simScore: score
    } AS metadata
"""
)
# end::vector[]

# tag::retriever[]
retriever = neo4jvector.as_retriever(search_kwargs={"k": 3})
# end::retriever[]

# tag::qa[]
kg_qa = RetrievalQA.from_chain_type(
    llm,                  # <1>
    chain_type="stuff",   # <2>
    retriever=retriever,  # <3>
    verbose=True,
    return_source_documents = True
)
# end::qa[]

@chain
def neo4jSimillaritySearchUsingK(_dict):
    results = neo4jvector.similarity_search(query=_dict["question"], k=_dict["k"])
    return results

# tag::generate-response[]
def generate_response(prompt):
    """
    Use the Neo4j Vector Search Index
    to augment the response from the LLM
    """

    # Handle the response
    response = kg_qa({"query": prompt, "verbose": True})
    return response['result']
# end::generate-response[]


"""
The `kg_qa` can now be registered as a tool within the agent.

# tag::importtool[]
from langchain.tools import Tool
# end::importtool[]

# tag::importkgqa[]
from tools.vector import kg_qa
# end::importkgqa[]

# tag::tool[]
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True
        ),
    Tool.from_function(
        name="Vector Search Index",  # <1>
        description="Provides information about movie plots using Vector Search", # <2>
        func = kg_qa, # <3>
        return_direct=True
    )
]
# end::tool[]
"""