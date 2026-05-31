# News -> People Knowledge Graph API

This is a Python service that reads news articles from TechCrunch, extracts the people mentioned and the relationships between them using LLMs, stores them as a knowledge graph, and exposes it over an HTTP API.

## Requirements
- Python 3.9+
- A Google Gemini API Key (`GEMINI_API_KEY`)

## Setup & Installation

1. **Clone the repository and navigate to the directory:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your API Key:**
   Export your Gemini API Key as an environment variable so the extraction engine can use it.
   - On Mac/Linux:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```
   - On Windows (PowerShell):
     ```powershell
     $env:GEMINI_API_KEY="your_api_key_here"
     ```

## Running the Application

Start the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```

Once the server is running, open your browser and navigate to the interactive API documentation (Swagger UI):
👉 **http://127.0.0.1:8000/docs**

## Using the API

You can test all endpoints directly from the `/docs` UI:

1. **`POST /articles`**: Submit a specific TechCrunch article URL to scrape it, extract relationships, and merge them into the graph.
2. **`POST /rescan`**: Scrape the latest pages of the TechCrunch OpenAI topic list (configurable number of pages) and process all found articles.
3. **`GET /people`**: Retrieve a paginated list of all canonical people currently in the knowledge graph.
4. **`GET /people/{id}`**: Retrieve detailed relationships and provenance quotes for a specific person.

## Architecture Notes
- **Entity Extraction**: Utilizes Gemini's Structured JSON outputs to ensure robust, strict schema extraction of entities and relationships directly from the messy article text.
- **Data Storage**: To avoid over-engineering and prioritize simplicity, the knowledge graph is stored entirely in-memory using Python dictionaries, backed by a persistent `graph_data.json` file.
- **Entity Resolution**: Simple ID normalization (lowercase, stripped spacing) is used to establish canonical nodes.
