import os
from dotenv import load_dotenv
from langchain_community.graphs import Neo4jGraph ## allow LLM to exe query on Neo4J instance
from langchain.chains import GraphCypherQAChain ## user NL query -> Cypher query -> run in Neo4J instance -> response/result
# from src.langchain_custom.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

load_dotenv()
# NEO4J_URI = os.getenv("NEO4J_URI")
# NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
# NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
# HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")
# HOSPITAL_CYPHER_MODEL = os.getenv("HOSPITAL_CYPHER_MODEL")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

HOSPITAL_QA_MODEL = os.getenv("HOSPITAL_QA_MODEL")
HOSPITAL_CYPHER_MODEL = os.getenv("HOSPITAL_CYPHER_MODEL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_Password")
NEO4J_CYPHER_EXAMPLES_INDEX_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_INDEX_NAME")
NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY = os.getenv(
    "NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY"
)
NEO4J_CYPHER_EXAMPLES_NODE_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_NODE_NAME")
NEO4J_CYPHER_EXAMPLES_METADATA_NAME = os.getenv("NEO4J_CYPHER_EXAMPLES_METADATA_NAME")

print("NEO4J_URI : {}\nNEO4J_USERNAME : {} \nHOSPITAL_CYPHER_MODEL : {}".format(NEO4J_URI, NEO4J_USERNAME, HOSPITAL_CYPHER_MODEL))

graph = Neo4jGraph(url=NEO4J_URI,
                    username=NEO4J_USERNAME,
                    password=NEO4J_PASSWORD)

graph.refresh_schema()

cypher_example_index = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
    index_name=NEO4J_CYPHER_EXAMPLES_INDEX_NAME,
    node_label=NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY.capitalize(),
    text_node_properties=[
        NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY,
    ],
    text_node_property=NEO4J_CYPHER_EXAMPLES_TEXT_NODE_PROPERTY,
    embedding_node_property="embedding",
)

cypher_example_retriever = cypher_example_index.as_retriever(search_kwargs={"k": 8})

# cypher_generation_template = """
# Task:
# Generate Cypher query for a Neo4j graph database.

# Instructions:
# Use only the provided relationship types and properties in the schema.
# Do not use any other relationship types or properties that are not provided.

# Schema:
# {schema}

# Note:
# Do not include any explanations or apologies in your responses.
# Do not respond to any questions that might ask anything other than
# for you to construct a Cypher statement. Do not include any text except
# the generated Cypher statement. Make sure the direction of the relationship is
# correct in your queries. Make sure you alias both entities and relationships
# properly (e.g. [c:COVERED_BY] instead of [:COVERED_BY]). Do not run any
# queries that would add to or delete from
# the database. Make sure to alias all statements that follow as with
# statement (e.g. WITH v as visit, c.billing_amount as billing_amount)
# If you need to divide numbers, make sure to
# filter the denominator to be non zero.

# Example queries for this schema:
# {example_queries}

# Warning:
# - Never return a review node without explicitly returning all of the properties
# besides the embedding property
# - Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
# - You must never include the
# statement "GROUP BY" in your query.
# - Make sure to alias all statements that
# follow as with statement (e.g. WITH v as visit, c.billing_amount as
# billing_amount)
# - If you need to divide numbers, make sure to filter the denominator to be non
# zero.

# String category values:
# Test results are one of: 'Inconclusive', 'Normal', 'Abnormal'
# Visit statuses are one of: 'OPEN', 'DISCHARGED'
# Admission Types are one of: 'Elective', 'Emergency', 'Urgent'
# Payer names are one of: 'Cigna', 'Blue Cross', 'UnitedHealthcare', 'Medicare',
# 'Aetna'

# If you're filtering on a string, make sure to lowercase the property and filter
# value.

# A visit is considered open if its status is 'OPEN' and the discharge date is
# missing.

# Use state abbreviations instead of their full name. For example, you should
# change "Texas" to "TX", "Colorado" to "CO", "North Carolina" to "NC", and so on.

# The question is:
# {question}
# """

# cypher_generation_prompt = PromptTemplate(
#     input_variables=["schema", "example_queries", "question"],
#     template=cypher_generation_template,
# )


cypher_generation_template = """
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{schema}

Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly (e.g. [c:COVERED_BY] instead of [:COVERED_BY]). Do not run any
queries that would add to or delete from
the database. Make sure to alias all statements that follow as with
statement (e.g. WITH v as visit, c.billing_amount as billing_amount)
If you need to divide numbers, make sure to
filter the denominator to be non zero.

Example queries for this schema:
# Who is the oldest patient and how old are they?
MATCH (p:Patient)
RETURN p.name AS oldest_patient,
       duration.between(date(p.dob), date()).years AS age
ORDER BY age DESC
LIMIT 1

# Which physician has billed the least to Cigna
MATCH (p:Payer)<-[c:COVERED_BY]-(v:Visit)-[t:TREATS]-(phy:Physician)
WHERE p.name = 'Cigna'
RETURN phy.name AS physician_name, SUM(c.billing_amount) AS total_billed
ORDER BY total_billed
LIMIT 1

# Which state had the largest percent increase in Cigna visits
# from 2022 to 2023?
MATCH (h:Hospital)<-[:AT]-(v:Visit)-[:COVERED_BY]->(p:Payer)
WHERE p.name = 'Cigna' AND v.admission_date >= '2022-01-01' AND
v.admission_date < '2024-01-01'
WITH h.state_name AS state, COUNT(v) AS visit_count,
     SUM(CASE WHEN v.admission_date >= '2022-01-01' AND
     v.admission_date < '2023-01-01' THEN 1 ELSE 0 END) AS count_2022,
     SUM(CASE WHEN v.admission_date >= '2023-01-01' AND
     v.admission_date < '2024-01-01' THEN 1 ELSE 0 END) AS count_2023
WITH state, visit_count, count_2022, count_2023,
     (toFloat(count_2023) - toFloat(count_2022)) / toFloat(count_2022) * 100
     AS percent_increase
RETURN state, percent_increase
ORDER BY percent_increase DESC
LIMIT 1

# How many non-emergency patients in North Carolina have written reviews?
MATCH (r:Review)<-[:WRITES]-(v:Visit)-[:AT]->(h:Hospital)
WHERE h.state_name = 'NC' and v.admission_type <> 'Emergency'
RETURN count(*)

Warning:
- Never return a review node without explicitly returning all of the properties
besides the embedding property
- Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
- You must never include the
statement "GROUP BY" in your query.
- Make sure to alias all statements that
follow as with statement (e.g. WITH v as visit, c.billing_amount as
billing_amount)
- If you need to divide numbers, make sure to filter the denominator to be non
zero.

String category values:
Test results are one of: 'Inconclusive', 'Normal', 'Abnormal'
Visit statuses are one of: 'OPEN', 'DISCHARGED'
Admission Types are one of: 'Elective', 'Emergency', 'Urgent'
Payer names are one of: 'Cigna', 'Blue Cross', 'UnitedHealthcare', 'Medicare',
'Aetna'

If you're filtering on a string, make sure to lowercase the property and filter
value.

A visit is considered open if its status is 'OPEN' and the discharge date is
missing.

Use state abbreviations instead of their full name. For example, you should
change "Texas" to "TX", "Colorado" to "CO", "North Carolina" to "NC", and so on.

Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
Never return embedding properties in your queries. You must never include the
statement "GROUP BY" in your query. Make sure to alias all statements that
follow as with statement (e.g. WITH v as visit, c.billing_amount as
billing_amount)
If you need to divide numbers, make sure to filter the denominator to be non
zero.

The question is:
{question}
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema",  "question"],
    template=cypher_generation_template,
)

qa_generation_template = """You are an assistant that takes the results from
a Neo4j Cypher query and forms a human-readable response. The query results
section contains the results of a Cypher query that was generated based on a
user's natural language question. The provided information is authoritative;
you must always use it to construct your response without doubt or correction
using internal knowledge. Make the answer sound like a response to the question.

The user asked the following question:
{question}

A Cypher query was run a generated these results:
{context}

If the provided information is empty, say you don't know the answer.
Empty information looks like this: []

If the query results are not empty, you must provide an answer.
If the question involves a time duration, assume the query results
are in units of days unless otherwise specified.

When names are provided in the query results, such as hospital names,
beware of any names that have commas or other punctuation in them.
For instance, 'Jones, Brown and Murray' is a single hospital name,
not multiple hospitals. Make sure you return any list of names in a
way that isn't ambiguous and allows someone to tell what the full names are.

Never say you don't have the right information if there is data in the
query results. Make sure to show all the relevant query results if you're
asked. You must always assume any provided query results are relevant to
answer the question. Construct your response based solely on the provided
query results.

Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)

hospital_cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(model=HOSPITAL_CYPHER_MODEL, temperature=0),
    qa_llm=ChatOpenAI(model=HOSPITAL_QA_MODEL, temperature=0),
    cypher_example_retriever=cypher_example_retriever,
    node_properties_to_exclude=["embedding"],
    graph=graph,
    verbose=True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    top_k=100,
)
