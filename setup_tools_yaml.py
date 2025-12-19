#!/usr/bin/env python3
"""
Setup script to generate tools.yaml from environment variables.

This script creates the investment_agent/.adk/tools.yaml file using
Neo4j credentials from the .env file, ensuring sensitive credentials
are not hardcoded in version control.

Usage:
    python setup_tools_yaml.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Neo4j configuration from environment
neo4j_uri = os.getenv("NEO4J_URI", "neo4j+s://demo.neo4jlabs.com")
neo4j_username = os.getenv("NEO4J_USERNAME", "companies")
neo4j_password = os.getenv("NEO4J_PASSWORD", "companies")
neo4j_database = os.getenv("NEO4J_DATABASE", "companies")

# Validate required environment variables
if not neo4j_uri:
    raise ValueError("NEO4J_URI environment variable is required")
if not neo4j_username:
    raise ValueError("NEO4J_USERNAME environment variable is required")
if not neo4j_password:
    raise ValueError("NEO4J_PASSWORD environment variable is required")

# YAML content template
tools_yaml_content = f'''sources:
  companies-graph:
    kind: "neo4j"
    uri: "{neo4j_uri}"
    user: "{neo4j_username}"
    password: "{neo4j_password}"
    database: "{neo4j_database}"

tools:
  companies_in_industry:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (:IndustryCategory {{name:$industry}})<-[:HAS_CATEGORY]-(c) 
      WHERE NOT EXISTS {{ (c)<-[:HAS_SUBSIDARY]-() }}
      RETURN c.id as company_id, c.name as name, c.summary as summary
    description: Companies (company_id, name, summary) in a given industry by industry
    parameters:
      - name: industry
        type: string
        description: Industry name to filter companies by

  companies:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      CALL db.index.fulltext.queryNodes("companies_fulltext", $search)
      YIELD node AS c, score
      RETURN c.id as company_id, c.name as name, c.summary as summary
      LIMIT 10
    description: List of Companies (id, name, summary) matching search text
    parameters:
      - name: search
        type: string
        description: Full-text search query for company names

  industries:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (i:IndustryCategory)
      RETURN DISTINCT i.name as industry_name
      ORDER BY i.name
    description: List of Industry names
    parameters: []

  articles_in_month:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (a:Article)
      WHERE date($date) <= date(a.date) < date($date) + duration('P1M')
      RETURN a.id as article_id, a.author as author, a.title as title, toString(a.date) as date, a.sentiment as sentiment
      LIMIT 25
    description: List of Articles (id, author, title, date, sentiment) in a month timeframe from the given date
    parameters:
      - name: date
        type: string
        description: Start date in yyyy-mm-dd format

  article:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (a:Article {{id: $article_id}})
      RETURN a.id as article_id, a.author as author, a.title as title, 
             toString(a.date) as date, a.sentiment as sentiment, 
             a.site as site, a.summary as summary, a.content as content
    description: Single Article details by article ID
    parameters:
      - name: article_id
        type: string
        description: Article ID to fetch

  companies_in_articles:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (o:Organization)<-[:MENTIONS]-(a:Article)
      WHERE a.id IN $article_ids
      RETURN DISTINCT o.id as company_id, o.name as name, o.summary as summary
    description: Companies mentioned in articles by article IDs
    parameters:
      - name: article_ids
        type: array
        description: List of article IDs

  people_at_company:
    kind: neo4j-cypher
    source: companies-graph
    statement: |
      MATCH (p:Person)-[r]-(o:Organization {{id: $company_id}})
      WHERE type(r) IN ["HAS_CEO", "HAS_BOARD_MEMBER"]
      RETURN p.name as name, type(r) as role
    description: People (name, role) associated with a company by company ID
    parameters:
      - name: company_id
        type: string
        description: Company ID to find people for
'''

# Create the output directory if it doesn't exist
output_dir = Path("investment_agent/.adk")
output_dir.mkdir(parents=True, exist_ok=True)

# Write the file
output_file = output_dir / "tools.yaml"
output_file.write_text(tools_yaml_content)

print(f"✅ Generated {output_file} from environment variables")
print(f"   Neo4j URI: {neo4j_uri}")
print(f"   Neo4j Username: {neo4j_username}")
print(f"   Neo4j Database: {neo4j_database}")
