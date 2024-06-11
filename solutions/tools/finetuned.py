from langchain.chains import GraphCypherQAChain
# tag::import-prompt-template[]
from langchain.prompts.prompt import PromptTemplate
# end::import-prompt-template[]

from solutions.llm import llm
from solutions.llm import cypher_llm
from solutions.graph import graph

# tag::prompt[]
CYPHER_GENERATION_TEMPLATE = """
You are an expert of writting Cypher query statements for Neo4j Graph Database.
Convert the user's question into Cypher statements based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Mention only Cypher query statements in the output with no extra information, as shown in example below

Example 
Question: 
write a Cypher Query that retrieves the price of the products named as "Chai"

Output:
MATCH (p:Product {Name: \'Chai\'}) RETURN p.UnitPrice

Schema:
{schema}

Question:
{question}

Cypher Query:
"""
# end::prompt[]

# tag::template[]
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
# end::template[]


# tag::cypher-qa[]
cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    qa_llm=llm,
    cypher_llm=cypher_llm,
    cypher_prompt=cypher_prompt,
    validate_cypher=True
)
# tag::cypher-qa[]

# tag::generate-response[]
def generate_cypher_response(prompt):
    """
    Use the Neo4j recommendations dataset to provide
    context to the LLM when answering a question
    """

    # Handle the response
    response = cypher_qa.run(prompt)

    return response['result']
# end::generate-response[]

"""
The `kg_qa` can now be registered as a tool within the agent.

# tag::importcypherqa[]
from tools.cypher import cypher_qa
# end::importcypherqa[]

# tag::tool[]
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True
        ),
    Tool.from_function(
        name="Vector Search Index",
        description="Provides information about movie plots using Vector Search",
        func = kg_qa,
        return_direct=True
    ),
    Tool.from_function(
        name="Graph Cypher QA Chain",  # <1>
        description="Provides information about Movies including their Actors, Directors and User reviews", # <2>
        func = cypher_qa, # <3>
        return_direct=True
    ),
]
# end::tool[]
"""