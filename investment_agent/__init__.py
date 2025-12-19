# chat_agent/__init__.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google API based on environment settings
# Use GOOGLE_GENAI_USE_VERTEXAI environment variable to switch between APIs
use_vertex_ai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "0") == "1"

if use_vertex_ai:
    # Vertex AI API configuration - requires explicit project and location
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "1"
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError(
            "GOOGLE_CLOUD_PROJECT environment variable not set. "
            "Please add it to your .env file: GOOGLE_CLOUD_PROJECT=your-gcp-project-id"
        )
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not location:
        raise ValueError(
            "GOOGLE_CLOUD_LOCATION environment variable not set. "
            "Please add it to your .env file: GOOGLE_CLOUD_LOCATION=us-central1"
        )
    os.environ["GOOGLE_CLOUD_LOCATION"] = location
else:
    # Google AI API configuration
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "0"
    # Get API key from environment - DO NOT hardcode
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable not set. "
            "Please add it to your .env file: GOOGLE_API_KEY=your_api_key_here"
        )
    os.environ["GOOGLE_API_KEY"] = api_key

# important to make ADK work
from . import agent