from solutions.graph import graph
from langchain import PromptTemplate
from solutions.llm import cypher_llm
from typing import Any, List, Dict
from langchain_core.runnables import chain

# end::import[]

# tag::prompt[]
CYPHER_GENERATION_TEMPLATE = """
You are an expert of writting Cypher query statements Neo4j Graph Database.
Convert the user's question into Cypher statements based on the schema.

Use only the provided relationship types and properties in the schema and the provided context.
Do not use any other relationship types or properties that are not provided.


Output only Cypher query statements with no extra information, as shown in example below

Example 
Question: 
"List all the products names with a price greater than $100"

Output:
"MATCH (p:Product) WHERE p.UnitPrice > 100 RETURN p"

Context
{context}

Schema:
{schema}

Question:
{question}

Output:
"""


CYPHER_GENERATION_PRODUCT_DETAILS_TEMPLATE = """
You specialize in writing Cypher query statements for Neo4j Graph Database. 

Convert the user's question into Cypher statements based on the schema and context. 

Write a Cypher query to retrieve all the details of the products relevant to the query. Use RETURN P in the query.

Use only the provided relationship types and properties in the schema and the provided context. Do not use any other relationship types or properties that are not provided.

Output only Cypher query statements with no extra information, as shown in the example below:

Example 
Question: 
"List all the products names with a price greater than $100"

Output:
"MATCH (p:Product) WHERE p.UnitPrice > 100 RETURN p"

Context:
{context}

Schema:
{schema}

Question:
{question}

Output:
"""

def construct_schema(
    structured_schema: Dict[str, Any],
    include_types: List[str],
    exclude_types: List[str],
) -> str:
    """Filter the schema based on included or excluded types"""

    def filter_func(x: str) -> bool:
        return x in include_types if include_types else x not in exclude_types

    filtered_schema: Dict[str, Any] = {
        "node_props": {
            k: v
            for k, v in structured_schema.get("node_props", {}).items()
            if filter_func(k)
        },
        "rel_props": {
            k: v
            for k, v in structured_schema.get("rel_props", {}).items()
            if filter_func(k)
        },
        "relationships": [
            r
            for r in structured_schema.get("relationships", [])
            if all(filter_func(r[t]) for t in ["start", "end", "type"])
        ],
    }

    # Format node properties
    formatted_node_props = []
    for label, properties in filtered_schema["node_props"].items():
        props_str = ", ".join(
            [f"{prop['property']}: {prop['type']}" for prop in properties]
        )
        formatted_node_props.append(f"{label} {{{props_str}}}")

    # Format relationship properties
    formatted_rel_props = []
    for rel_type, properties in filtered_schema["rel_props"].items():
        props_str = ", ".join(
            [f"{prop['property']}: {prop['type']}" for prop in properties]
        )
        formatted_rel_props.append(f"{rel_type} {{{props_str}}}")

    # Format relationships
    formatted_rels = [
        f"(:{el['start']})-[:{el['type']}]->(:{el['end']})"
        for el in filtered_schema["relationships"]
    ]

    return "\n".join(
        [
            "Node properties are the following:",
            ",".join(formatted_node_props),
            "Relationship properties are the following:",
            ",".join(formatted_rel_props),
            "The relationships are the following:",
            ",".join(formatted_rels),
        ]
    )

# tag::generate-response[]
def generate_cypher(prompt)->str:
    # Handle the response
    cypher_query = cypher_llm.invoke(prompt)
    return cypher_query
# end::generate-response[]

@chain
def get_cypher_prompt()->PromptTemplate:
    prompt = PromptTemplate.from_template(template=CYPHER_GENERATION_TEMPLATE)
    # formated_prompt:str = prompt.format(schema=construct_schema(graph.get_structured_schema, [], []),
    #                                     question=message)
    return prompt

def get_graph_scheema()->str:
    return construct_schema(graph.get_structured_schema, [], [])


