# Multi-Agent Investment Research System: Google ADK, MCP Toolbox & Neo4j

Build your own AI-powered multi-agent investment research system using [Google's Agent Development Kit (ADK)](https://github.com/google/adk-python), [Model Context Protocol (MCP) Toolbox](https://github.com/googleapis/genai-toolbox), and [Neo4j](https://neo4j.com/) graph database. This project demonstrates how to combine intelligent multi-agent orchestration with pre-validated database queries and knowledge graph analysis for sophisticated enterprise AI applications.

Based on the [Google Cloud Community Article: "Using Google's Agent Development Kit (ADK) with MCP Toolbox and Neo4j"](https://discuss.google.dev/t/using-googles-agent-development-kit-adk-with-mcp-toolbox-and-neo4j/187356).

## About This Project

This is an implementation of a sophisticated multi-agent investment research system that demonstrates the power of combining three key technologies:

### Core Technologies:

- **[Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)**: Provides the framework for building and orchestrating multi-agent systems with advanced reasoning capabilities using Gemini models
- **[Model Context Protocol (MCP) Toolbox](https://googleapis.github.io/genai-toolbox/)**: Enables declarative definition and deployment of pre-validated, domain-specific database queries as reusable tools
- **[Neo4j Graph Database](https://neo4j.com/)**: Stores and queries the Company News Knowledge Graph with relationships and entities

### System Features:

- **Multi-Agent Architecture**: Specialized agents handle different research domains
- **Graph Database Integration**: Queries comprehensive knowledge graphs for relationship analysis
- **MCP Tools Integration**: Leverages Model Context Protocol for extensible, pre-validated tool definitions
- **Data-Grounded AI**: Uses custom Python functions and database queries as agent tools
- **Intelligent Query Generation**: Automatically generates Cypher queries from natural language
- **Type Serialization**: Handles Neo4j data types (DateTime, Duration, etc.) for seamless Pydantic integration

## Features

### Multi-Agent System

The project implements specialized agents orchestrated by a root agent:

1. **Graph Database Agent**: Fetches the Neo4j graph database schema and executes read queries. Generates Cypher queries to fulfill information requests with a focus on structural questions, aggregations, sorting, and filtering. Falls back for complex queries when specialized agents aren't applicable.

2. **Investor Research Agent**: Discovers investors in companies or organizations by exact name or ID. Provides investment relationship data including investor names, IDs, and types (Organization or Person).

3. **Investment Research Agent**: Accesses a comprehensive knowledge graph of companies, people, articles, industries, and technologies. Uses MCP Toolbox tools to fetch industries, companies in industries, articles, organization mentions, and people involvement data.

4. **Root Agent**: Orchestrates all sub-agents, routes requests intelligently, and handles the overall workflow. Prefers specialized research agents over the database agent and renders results as tables, charts, or artifacts when requested.

### Model Context Protocol (MCP) Integration

**MCP Toolbox** provides declarative database query definitions deployed on Google Cloud Run:
- Pre-validated, expert-authored queries for correctness and performance
- Supports Neo4j, PostgreSQL, MySQL, and Google Cloud Spanner
- Enables safe, centralized query management without exposing database directly to LLMs
- Tools are dynamically loaded at runtime for extensibility

### Data Sources

The system connects to a demo Neo4j database containing a subset of [Diffbot's](https://diffbot.com/) global Knowledge Graph with:

- 237,358 nodes representing organizations, people, articles, industries, and technologies
- Investment relationships between companies and investors
- Articles with sentiment analysis
- Industry categorizations and competitive intelligence

## Prerequisites

- Python 3.11+
- [Google ADK](https://google.github.io/adk-docs/): For multi-agent orchestration
- [Neo4j Database](https://neo4j.com/): Graph database (demo instance provided)
- [MCP Toolbox](https://googleapis.github.io/genai-toolbox/): For database query management (optional for development)
- Google API credentials (Google AI API or Vertex AI)
- uv package manager

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sidagarwal04/neo4j-adk-multiagents.git
cd neo4j-adk-multiagents
```

2. Create a virtual environment using uv:
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
uv pip install -r requirements.txt
```

4. Generate MCP Toolbox configuration from environment variables:
```bash
python setup_tools_yaml.py
```

This generates `investment_agent/.adk/tools.yaml` from your `.env` file settings.

## Configuration

### Neo4j Database

The project connects to a demo Neo4j database containing the **Company News Knowledge Graph** - a small subset (250k entities) of [Diffbot's](https://diffbot.com/) global Knowledge Graph (50 billion entities).

**Dataset Contents:**
- Organizations and company information
- People in leadership positions
- Locations and industries
- Articles mentioning companies (chunked and indexed as vector embeddings)

**Demo Database Credentials:**

This is a **read-only** version of the knowledge graph:

| Setting | Value |
|---------|-------|
| **URL** | `https://demo.neo4jlabs.com:7473` |
| **Username** | `companies` |
| **Password** | `companies` |
| **Database** | `companies` |

In your `.env` file, configure:

```env
NEO4J_URI=neo4j+s://demo.neo4jlabs.com
NEO4J_USERNAME=companies
NEO4J_PASSWORD=companies
```

### Google API Configuration

Choose **one** of the two authentication methods in your `.env` file:

**Option 1: Google AI API (Recommended for quick setup)**

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey):

```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_api_key_here
```

**Option 2: Vertex AI API (GCP Projects)**

For Google Cloud Platform projects with Vertex AI:

```env
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### ADK Configuration

The Agent Development Kit (ADK) uses a specified Gemini model for agent reasoning:

```env
GOOGLE_ADK_MODEL=your_model_here
```

Available models: See the [ADK Documentation](https://google.github.io/adk-docs/) for the latest available Gemini models.

### MCP Toolbox Configuration

Configure the Model Context Protocol (MCP) Toolbox endpoint:

```env
MCP_TOOLBOX_URL=your_mcp_tools_url_here
```

For more information on deploying MCP Toolbox, see the [MCP Toolbox Documentation](https://googleapis.github.io/genai-toolbox/).

**⚠️ Security Note:** Never commit your `.env` file to version control. The `.gitignore` is configured to exclude it. Use `example.env` as a template.

### Default Configuration Values

The application provides sensible defaults for some configuration values to enable quick setup with the demo dataset. However, **Google API credentials are required** and have no defaults for security reasons.

**Configuration with defaults:**
- `NEO4J_URI`: Defaults to demo database `neo4j+s://demo.neo4jlabs.com`
- `NEO4J_USERNAME`: Defaults to `companies`
- `NEO4J_PASSWORD`: Defaults to `companies`
- `GOOGLE_ADK_MODEL`: Defaults to `gemini-3-pro-preview`
- `MCP_TOOLBOX_URL`: Defaults to public MCP Toolbox endpoint

**Configuration without defaults (required):**
- `GOOGLE_API_KEY` (for Google AI API): Must be explicitly set
- `GOOGLE_CLOUD_PROJECT` (for Vertex AI): Must be explicitly set
- `GOOGLE_CLOUD_LOCATION` (for Vertex AI): Must be explicitly set

The application will raise a clear error if required variables are missing.

## Usage

### Running the Web Interface

The ADK provides a rich web UI for interactive agent testing with debug information including tool invocations, parameters, and errors:

```bash
uv run adk web
```

This launches the ADK web interface where you can:
- Select agents from the top-left menu
- Chat interactively with the investment research system
- Inspect tool invocations and debug information
- See the agent's reasoning and multi-step execution flow

### Running the API Server

For backend API access via REST:

```bash
uv run adk api_server
```

Then access the API directly via curl or postman.

### Example Queries

The system can answer complex multi-step questions:

**Finding Competitors:**
```
"What are the main competitors of YouTube?"
```
The agent queries the database to find competitor relationships.

**Market Analysis:**
```
"What are 5 companies mentioned in articles from January 2023 with good sentiment and who are the people working there?"
```
The agent finds relevant articles, identifies companies, and looks up leadership.

**Investment Tracking:**
```
"Who has invested in BYTEDANCE and where else have they invested?"
```
The agent finds investors and tracks their portfolio across companies.

## Key Components

### Agents and Tools Architecture

In the ADK, agents take actions by selecting and executing tools from a set of available functions, integrating their output with reasoning and generation until the user's task is fulfilled. Tools can be:

- **Python Functions**: Custom-defined tools with type hints and docstrings
- **MCP Tools**: Model Context Protocol tools deployed on Cloud Run
- **Vertex AI Extensions**: Google Cloud-managed tools

### Neo4j Database Integration

The `neo4jDatabase` class handles all database operations:
- Executes read-only Cypher queries (write queries are blocked for safety)
- Automatically serializes Neo4j types (DateTime, Duration, etc.) to JSON-compatible formats using the `serialize_neo4j_value()` function
- Provides error handling and connection management

### Agent Tools

**Graph Database Agent Tools:**
- `get_schema()`: Retrieves the database schema with node labels, properties, and relationships
- `execute_read_query()`: Executes arbitrary read-only Cypher queries

**Investor Research Agent Tools:**
- `get_investors()`: Finds investors in a company by name or ID, returning investor details and IDs for further investigation

**Investment Research Agent Tools:**
- Dynamically loads tools from MCP Toolbox deployed on Cloud Run, including:
  - Industry search and filtering
  - Company search and details
  - Article analysis and sentiment scoring
  - Cross-reference of companies in articles
  - Leadership information lookup

### Multi-Agent Orchestration

The root agent manages three specialized sub-agents:

1. **Query Generation**: The root agent understands user intent and routes queries to the appropriate specialized agent
2. **Hierarchical Processing**: Sub-agents perform focused tasks (database queries, investor research, article analysis)
3. **Result Validation**: The root agent ensures results satisfy the user's requirements before returning

## Model Context Protocol (MCP) Toolbox

**MCP Toolbox** is a declarative framework for defining and deploying database-backed tools for AI agents:

- **Declarative Configuration**: Define queries once in YAML, deploy everywhere
- **Query Safety**: Pre-validate queries before agents access them, preventing injection attacks
- **Cloud-Native**: Deploy on Google Cloud Run with automatic scaling
- **Multi-Database Support**: Works with Neo4j, PostgreSQL, MySQL, Google Cloud Spanner
- **Session Management**: Built-in session handling and authentication
- **Performance Optimized**: Centralized query tuning and indexing management

In this project, MCP Toolbox serves as the `investment_research_agent`'s backend, providing industry searches, company lookups, article analysis, and leadership information through pre-defined queries managed in `setup_tools_yaml.py`.

### Integration Pattern

The system integrates with [MCP Toolbox](https://github.com/googleapis/genai-toolbox) by:

- **Pre-validated Queries**: Subject matter expert-authored database queries vetted for correctness and performance
- **Cloud Deployment**: Toolbox deployed on Google Cloud Run with HTTPS/SSE transport
- **Dynamic Loading**: Investment research agent loads tools asynchronously at runtime via `load_tools(MCP_TOOLBOX_URL)`
- **Database Support**: Neo4j graph queries optimized for relationship analysis

The investment research agent accesses domain-specific database tools without hardcoding queries, providing access to domain-specific database tools without hardcoding queries.

## Development

### Modifying Agents

Edit `investment_agent/agent.py` to:
- Add new tools or agents
- Modify agent instructions and capabilities
- Update model selection

### Adding New Tools

1. Create a new function with proper type hints and docstring
2. Add the function to an agent's `tools` list

```python
def my_tool(param: str) -> str:
    """Tool description"""
    return result
```

## Troubleshooting

### Neo4j Serialization Error

If you encounter `Unable to serialize unknown type: <class 'neo4j.time.DateTime'>`:
- The serialization is handled automatically via the `serialize_neo4j_value()` function
- This converts Neo4j types to ISO format strings

### Import Errors

Ensure all dependencies are installed:
```bash
uv pip install google-adk neo4j
```

## Dependencies

- `google-adk>=1.21.0`: Google ADK framework
- `neo4j>=6.0.3`: Neo4j Python driver

See `pyproject.toml` for complete dependency list.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please follow these steps:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Support

For issues or questions:
- Check the [Google ADK documentation](https://google.github.io/adk-docs/)
- Review [Neo4j Python Driver docs](https://neo4j.com/docs/api/python/current/)
- Consult the [MCP Toolbox documentation](https://googleapis.github.io/genai-toolbox/)

## Reference & Attribution

This project is based on the Google Cloud Community article:

📖 **"Using Google's Agent Development Kit (ADK) with MCP Toolbox and Neo4j"**  
by [Google Cloud Community](https://discuss.google.dev/t/using-googles-agent-development-kit-adk-with-mcp-toolbox-and-neo4j/187356)

The article provides comprehensive guidance on:
- Agent Development Kit (ADK) setup and fundamentals
- Building custom agents with Python functions as tools
- Integrating Neo4j graph databases for data-grounded agents
- Deploying MCP Toolbox on Google Cloud Run
- Creating multi-agent systems with hierarchical orchestration

### Related Resources

**Google ADK:**
- [Official GitHub Repository](https://github.com/google/adk-python)
- [Comprehensive Documentation](https://google.github.io/adk-docs/)
- [Example Repository](https://github.com/google/adk-samples/)
- [Launch Blog](https://cloud.google.com/blog/products/ai-machine-learning/build-and-manage-multi-system-agents-with-vertex-ai)

**Neo4j:**
- [Neo4j GenAI Hub](https://neo4j.com/genai)
- [Neo4j Developer](https://neo4j.com/developer)
- [GraphRAG](https://graphrag.com/)
- [Neo4j GenAI Ecosystem](https://neo4j.com/labs/genai-ecosystem)
- [AI Agents with Neo4j and MCP Toolbox](https://neo4j.com/blog/developer/ai-agents-gen-ai-toolbox/)

**Demo Dataset:**
- [Colab Notebook](https://colab.sandbox.google.com/drive/1f0GYXrO8pZsoJnyKDDxzFZVaYgXhx3ME#scrollTo=FSlyylN9HBJh) with full implementation
- [Diffbot Knowledge Graph](https://diffbot.com/) (50 billion entities)
- Demo Database: `neo4j+s://demo.neo4jlabs.com` (Read-only companies graph)
