from google.adk.agents import Agent
import base64

import os
import random
import sys
from neo4j import GraphDatabase
from typing import Any
import re
from dotenv import load_dotenv

def serialize_neo4j_value(value: Any) -> Any:
    """Convert Neo4j types to JSON-serializable Python types"""
    from neo4j.time import DateTime, Date, Time, Duration
    
    if isinstance(value, DateTime):
        return value.isoformat()
    elif isinstance(value, Date):
        return value.isoformat()
    elif isinstance(value, Time):
        return value.isoformat()
    elif isinstance(value, Duration):
        return str(value)
    elif isinstance(value, dict):
        return {k: serialize_neo4j_value(v) for k, v in value.items()}
    elif isinstance(value, (list, tuple)):
        return [serialize_neo4j_value(item) for item in value]
    else:
        return value


class neo4jDatabase:
    def __init__(self,  neo4j_uri: str, neo4j_username: str, neo4j_password: str):
        d = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))
        d.verify_connectivity()
        self.driver = d

    def is_write_query(self, query: str) -> bool:
        return re.search(r"\b(MERGE|CREATE|SET|DELETE|REMOVE|ADD)\b", query, re.IGNORECASE) is not None

    def _execute_query(self, query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        if self.is_write_query(query):
            raise "Write Queries are not supported in this agent"
        else:
            result = self.driver.execute_query(query, params)
            return [serialize_neo4j_value(dict(r)) for r in result.records]

# Load environment variables
load_dotenv()

db = neo4jDatabase(
    os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com"),
    os.getenv("NEO4J_USERNAME", "companies"),
    os.getenv("NEO4J_PASSWORD", "companies")
)

# Nodes in the database
db._execute_query("MATCH () RETURN count(*) as nodes")

# {'nodes': 237358 }

def get_schema() -> list[dict[str,Any]]:
  """Get the schema of the database, returns node-types(labels) with their types and attributes and relationships between node-labels
  Args: None
  Returns:
    list[dict[str,Any]]: A list of dictionaries representing the schema of the database
    For example
    ```
    [{'label': 'Person','attributes': {'summary': 'STRING','id': 'STRING unique indexed', 'name': 'STRING indexed'},
      'relationships': {'HAS_PARENT': 'Person', 'HAS_CHILD': 'Person'}}]
    ```
  """
  try:
      results = db._execute_query(
              """
              call apoc.meta.data() yield label, property, type, other, unique, index, elementType
              where elementType = 'node' and not label starts with '_'
              with label,
              collect(case when type = 'RELATIONSHIP' then [property, head(other)] end) as relationships,
              collect(case when type <> 'RELATIONSHIP' then [property, type + case when unique 
                      then " unique" else "" end + case when index then " indexed" else "" end] end) 
              as attributes,

              RETURN label, apoc.map.fromPairs(attributes) as attributes, apoc.map.fromPairs(relationships) as relationships
              """
          )
      return results
  except Exception as e:
      return [{"error":str(e)}]

def execute_read_query(query: str, params: dict[str, Any] = {}) -> list[dict[str, Any]]:
    """
    Execute a Neo4j Cypher query and return results as a list of dictionaries
    Args:
        query (str): The Cypher query to execute
        params (dict[str, Any], optional): The parameters to pass to the query or None.
    Raises:
        Exception: If there is an error executing the query
    Returns:
        list[dict[str, Any]]: A list of dictionaries representing the query results
    """
    try:
        if params is None:
            params = {}
        results = db._execute_query(query, params)
        return results
    except Exception as e:
        return [{"error":str(e)}]

# get_schema()
# execute_read_query("RETURN 1", None)

MODEL = os.getenv("GOOGLE_ADK_MODEL", "gemini-3-pro-preview")


graph_database_agent = Agent(
    model=MODEL,
    name='graph_database_agent',
    description="""
    The graph_database_agent is able to fetch the schema of a neo4j graph database and execute read queries.
    It will generate Cypher queries using the schema to fulfill the information requests and repeatedly
    try to re-create and fix queries that error or don't return the expected results.
    When passing requests to this agent, make sure to have clear specific instructions what data should be retrieved, how,
    if aggregation is required or path expansion.
    Don't use this generic query agent if other, more specific agents are available that can provide the requested information.
    This is meant to be a fallback for structural questions (e.g. number of entities, or aggregation of values or very specific sorting/filtering)
    Or when no other agent provides access to the data (inputs, results and shape) that is needed.
    """,
    instruction="""
      You are an Neo4j graph database and Cypher query expert, that must use the database schema with a user question and repeatedly generate valid cypher statements
      to execute on the database and answer the user's questions in a friendly manner in natural language.
      If in doubt the database schema is always prioritized when it comes to nodes-types (labels) or relationship-types or property names, never take the user's input at face value.
      If the user requests also render tables, charts or other artifacts with the query results.
      Always validate the correct node-labels at the end of a relationship based on the schema.

      If a query fails or doesn't return data, use the error response 3 times to try to fix the generated query and re-run it, don't return the error to the user.
      If you cannot fix the query, explain the issue to the user and apologize.
      *You are prohibited* from using directional arrows (like -> or <-) in the graph patterns, always use undirected patterns like `(:Label)-[:TYPE]-(:Label)`.
      You get negative points for using directional arrays in patterns.

      Fetch the graph database schema first and keep it in session memory to access later for query generation.
      Keep results of previous executions in session memory and access if needed, for instance ids or other attributes of nodes to find them again
      removing the need to ask the user. This also allows for generating shorter, more focused and less error-prone queries
      to for drill downs, sequences and loops.
      If possible resolve names to primary keys or ids and use those for looking up entities.
      The schema always indicates *outgoing* relationship-types from an entity to another entity, the graph patterns read like english language.
      `company has supplier` would be the pattern `(o:Organization)-[:HAS_SUPPLIER]-(s:Organization)`

      To get the schema of a database use the `get_schema` tool without parameters. Store the response of the schema tool in session context
      to access later for query generation.

      To answer a user question generate one or more Cypher statements based on the database schema and the parts of the user question.
      If necessary resolve categorical attributes (like names, countries, industries, publications) first by retrieving them for a set of entities to translate from the user's request.
      Use the `execute_query` tool repeatedly with the Cypher statements, you MUST generate statements that use named query parameters with `$parameter` style names
      and MUST pass them as a second dictionary parameter to the tool, even if empty.
      Parameter data can come from the users requests, prior query results or additional lookup queries.
      After the data for the question has been sufficiently retrieved, pass the data and control back to the parent agent.
    """,
    tools=[
        get_schema, execute_read_query
    ]
)


def get_investors(company: str) -> list[dict[str, Any]]:
    """
    Returns the investor in the company with this name or id.
    Args:
        company (str): name of the company to find investors in
    Returns:
        list[dict[str, Any]]: A list of investor ids, names (and their types Organization or Person)
    """
    try:
        results = db._execute_query("""
        MATCH p=(o:Organization)<-[r:HAS_INVESTOR]-(i)
        WHERE o.name=$company OR o.id=$company
          AND NOT exists { (o)<-[:SUBSIDARY_OF]-() } 
        RETURN i.id as id, i.name as name, head(labels(i)) as type
        """, {"company":company})
        return results
    except Exception as e:
        return [{"error":str(e)}]
    

investor_research_agent = Agent(
    model=MODEL,
    name='investor_research_agent',
    description="""
    This investment research agent has the sole purpose of finding investors in
    an company or organization which id identified by a single EXACT name or id,
    which should have been retrieved before from the database.
    """,
    instruction="""
    You are an agent that has access to a database of investment relationships between companies and indivduals.
    Use the get_investors tool when asked to find the investors of a company by id and name.
    If you do so, try to always return not just the factual attribute data but also
    investor ids to allow the other agents to investigate them more.
    """,
    tools=[
        get_schema, get_investors
    ]
)

        
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseConnectionParams

# Get MCP Toolbox URL from environment
MCP_TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL", "https://toolbox-990868019953.us-central1.run.app/mcp/sse")

async def load_tools(mcp_url):
    async with MCPToolset(connection_params=SseConnectionParams(url=mcp_url)) as toolset:
      tools = await toolset.load_tools()
      tools.extend([get_schema])
      return tools

# Initialize tools with get_schema
# Note: MCP Toolbox tools from load_tools(MCP_TOOLBOX_URL) are loaded asynchronously at runtime
# The investment_research_agent uses the base tools list here; additional MCP tools can be loaded
# when the agent is invoked through the ADK runtime
tools = [get_schema]


investment_research_agent = Agent(
    model=MODEL,
    name='investment_research_agent',
    description="""
    This investment research agent has access to a number of tools on a companies and news database.
    It can find industries, companies in industries, articles in a certain month, article details,
    organizations mentioned in articles and people working there.
    """,
    instruction="""
    You are an agent that has access to a knowledge graph of companies (organizations), people involved with them, articles about companies,
    and industry categories and technologies.
    You have a set of tools to access different aspects of the investment database.
    You will be tasked by other agents to fetch certain information from that knowledge graph.
    If you do so, try to always return not just the factual attribute data but also
    ids of companies, articles, people to allow the other tools to investigate them more.
    """,
    tools=tools
)

root_agent = Agent(
    model=MODEL,
    name='investment_agent',
    global_instruction = "",
    instruction="""
    You are an agent that has access to a knowledge graph of companies (organizations), people involved with them, articles about companies,
    and industry categories and technologies.
    You have a set of agents to retrieve information from that knowledge graph, if possible prefer the research agents over the database agent.
    If the user requests it, do render tables, charts or other artifacts with the research results.
    """,

    sub_agents=[investor_research_agent, investment_research_agent, graph_database_agent]
)