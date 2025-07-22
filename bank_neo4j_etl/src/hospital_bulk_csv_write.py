import os
import logging
from retry import retry
from neo4j import GraphDatabase
import dotenv
dotenv.load_dotenv()

### Pending "EXAMPLE_CYPHER_CSV_PATH" examples

# Paths to CSV files containing hospital data
ACCTMAST_CSV_PATH = os.getenv("ACCTMAST_CSV_PATH")
CUSTMAST_CSV_PATH = os.getenv("CUSTMAST_CSV_PATH")
NOBOOK_CSV_PATH = os.getenv("NOBOOK_CSV_PATH")

EXAMPLE_CYPHER_CSV_PATH = os.getenv("EXAMPLE_CYPHER_CSV_PATH")

# Neo4j config
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

print("NEO4J_URI : ", NEO4J_URI)
print("NEO4J_USERNAME : ", NEO4J_USERNAME)
print("NEO4J_PASSWORD : ", NEO4J_PASSWORD)
print("ACCTMAST_CSV_PATH : ", ACCTMAST_CSV_PATH)
print("CUSTMAST_CSV_PATH : ", CUSTMAST_CSV_PATH)
print("NOBOOK_CSV_PATH : ", NOBOOK_CSV_PATH)
print("EXAMPLE_CYPHER_CSV_PATH : ", EXAMPLE_CYPHER_CSV_PATH)

# Configure the logging module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


LOGGER = logging.getLogger(__name__)
#NODES = ["Hospital", "Payer", "Physician", "Patient", "Visit", "Review", "Question"]
NODES = ["CustMast", "AccountMast", "Nobook"] ## "Review", "Question"


def _set_uniqueness_constraints(tx, node):
    query = f"""CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node})
        REQUIRE n.id IS UNIQUE;"""
    _ = tx.run(query, {})

@retry(tries=100, delay=10)
def load_hospital_graph_from_csv() -> None:
    """Load structured bank CSV data following
    a specific ontology into Neo4j"""

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session() as session:
        for node in NODES:
            session.write_transaction(_set_uniqueness_constraints, node)

    LOGGER.info("Loading CUSTMAST nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{CUSTMAST_CSV_PATH}' AS row
        CREATE (:CUSTOMERID {{
              CUST_ID: toInteger(row.CUST_ID),
              DAT_CUST_OPEN: date(row.DAT_CUST_OPEN),
              FLG_CUST_TYP: row.FLG_CUST_TYP,
              FLG_STAFF: row.FLG_STAFF,
              NAM_CUST_FULL: row.NAM_CUST_FULL,
              NAM_CUSTADR_STATE: row.NAM_CUSTADR_STATE,
              NAM_CUSTADR_CNTRY: row.NAM_CUSTADR_CNTRY,
              DAT_BIRTH_CUST: date(row.DAT_BIRTH_CUST),
              FLG_MNT_STATUS: row.FLG_MNT_STATUS,
              CUST_STATUS: toInteger(row.CUST_STATUS),
              AADHAAR_UPDATED_DAT: date(row.AADHAAR_UPDATED_DAT)
            }});
        
        """
              
        _ = session.run(query, {})
        
    
    LOGGER.info("Loading ACCTMAST nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        
        LOAD CSV WITH HEADERS FROM '{ACCTMAST_CSV_PATH}' AS row
        MERGE (acct:ACCOUNT_MAST {
          ACCT_NO: toInteger(row.ACCT_NO)
        })
        SET acct += {
          CC_BRN: toInteger(row.CC_BRN),
          DAT_ACCT_OPEN: date(row.DAT_ACCT_OPEN),
          ACCT_STAT: toInteger(row.ACCT_STAT),
          BAL_ACCT_MIN_REQD: toInteger(row.BAL_ACCT_MIN_REQD),
          BAL_AVAILABLE: toInteger(row.BAL_AVAILABLE),
          AMT_DR_TODAY: toInteger(row.AMT_DR_TODAY),
          AMT_CR_TODAY: toInteger(row.AMT_CR_TODAY),
          AMT_DR_MTD: toInteger(row.AMT_DR_MTD),
          AMT_CR_MTD: toInteger(row.AMT_CR_MTD)
        }
        WITH acct, row
        MATCH (cust:CUSTOMERID {CUST_ID: toInteger(row.CUST_ID)})
        MERGE (cust)-[:HAS]->(acct);
        
        """
        _ = session.run(query, {})


    LOGGER.info("Loading nobook nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{NOBOOK_CSV_PATH}' AS row
        MERGE (txn:NOBOOK {
          REF_TXN_NO: row.REF_TXN_NO
        })
        SET txn += {
          DAT_TXN: date(row.DAT_TXN),
          CC_BRN_TXN: toInteger(row.CC_BRN_TXN),
          ACCT_NO: toInteger(row.ACCT_NO),
          TXT_TXN_DESC: row.TXT_TXN_DESC,
          DAT_VALUE: date(row.DAT_VALUE),
          AMT_DRCR: row.AMT_DRCR,
          AMT_TXN: toInteger(row.AMT_TXN),
          REF_USR_NO: row.REF_USR_NO
        }
        WITH txn, row
        MATCH (acct:ACCOUNT_MAST {ACCT_NO: toInteger(row.ACCT_NO)})
        MERGE (acct)-[:Transaction_detail]->(txn);
        """
        _ = session.run(query, {})



    LOGGER.info("Loading question nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{EXAMPLE_CYPHER_CSV_PATH}' AS questions
        MERGE (Q:Question {{
                         question: questions.question,
                         cypher: questions.cypher
                        }});
        """
        _ = session.run(query, {})

"""
### Establishing the relationship between nodes

    LOGGER.info("Loading 'HAS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{CUSTMAST_CSV_PATH}' AS row
        MATCH (source: `CustMast` {{ `id`: toInteger(trim(row.`CUST_ID`)) }})
        MATCH (target: `AccountMast` {{ `id`: toInteger(trim(row.`CUST_ID`))}})
        MERGE (source)-[r: `HAS`]->(target)
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'TRANSACTION_DETAILS' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{ACCTMAST_CSV_PATH}' AS trans
            MATCH (v:AccountMast {{id: toInteger(trans.ACCT_NO)}})
            MATCH (r:Nobook {{id: toInteger(trans.ACCT_NO)}})
            MERGE (v)-[TRANSACTION:TRANSACTION_DETAILS]->(r)
        """
        _ = session.run(query, {})
"""

if __name__ == "__main__":
    load_hospital_graph_from_csv()

