# Setting up HybridCypherRetriever

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path
import codecs

from neo4j_graphrag.retrievers import HybridCypherRetriever
from neo4j_graphrag.embeddings import OpenAIEmbeddings

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, encoding="utf-8-sig")

# Read environment variables

# 2. Retrieve and debug:
uri = os.getenv("NEO4J_URI", "")
print("Loaded URI (raw repr):", repr(uri))

user = os.getenv("NEO4J_USER")
pwd = os.getenv("NEO4J_PASS")

# 3. Sanitize and decode:
if "\\x3a" in uri:
    # Decode any \xNN escapes to actual chars
    uri = codecs.decode(uri, "unicode_escape")
elif "\\x" in uri:
    # Generic handler for any \xNN pattern:
    uri = uri.encode("utf-8").decode("unicode-escape")

# 4. Final URI:
print("Final URI:", uri)

# Create Neo4j driver
driver = GraphDatabase.driver(uri, auth=(user, pwd))

INDEX_NAME = "content_index"

embedder = OpenAIEmbeddings(model="text-embedding-ada-002")

cypher_traversal_query = """
WITH node, score
OPTIONAL MATCH (node)<-[:CAUSED_BY]-(sym_from_reason:FaultSymptom)
OPTIONAL MATCH (node)<-[:MITIGATED_BY]-(sym_from_measure:FaultSymptom)
OPTIONAL MATCH (node)-[:HAS_FAULT]->(sym_from_loc:FaultSymptom)
WITH node, score,
    CASE 
       WHEN sym_from_reason IS NOT NULL THEN sym_from_reason
       WHEN sym_from_measure IS NOT NULL THEN sym_from_measure
       WHEN sym_from_loc IS NOT NULL THEN sym_from_loc
       WHEN node:FaultSymptom THEN node
       ELSE NULL 
    END AS symptom,
    node:FaultLocation AS isLocation
OPTIONAL MATCH (location:FaultLocation)-[:HAS_FAULT]->(symptom)
OPTIONAL MATCH (symptom)-[:CAUSED_BY]->(reason:FaultReason)
OPTIONAL MATCH (symptom)-[:MITIGATED_BY]->(measure:FaultMeasure)
WITH coalesce(location, CASE WHEN isLocation THEN node END) AS location,
     symptom, reason, measure, node, score
RETURN 
  coalesce(location.name, '') + ": " + coalesce(symptom.description, '') 
    + CASE WHEN reason IS NOT NULL THEN " Cause: " + reason.name ELSE "" END 
    + CASE WHEN measure IS NOT NULL THEN " Measure: " + measure.description ELSE "" END 
  AS text,
  score,
  {
    location: location.name, 
    symptom: symptom.description, 
    reason: reason.name, 
    measure: measure.description,
    location_id: elementId(location),
    symptom_id: elementId(symptom),
    reason_id: elementId(reason),
    measure_id: elementId(measure)
  } AS metadata
"""

retriever = HybridCypherRetriever(
    driver,
    vector_index_name="content_index",
    fulltext_index_name="fulltext-index",
    retrieval_query=cypher_traversal_query,
    embedder=embedder
)
