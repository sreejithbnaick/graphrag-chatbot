# Neo4j Setup with Podman

This guide explains how to set up and run a Neo4j database instance using Podman on macOS.

## Prerequisites

- [Podman](https://podman.io/) installed on your system.
- Podman machine initialized and running.

## Setup Steps

### 1. Initialize and Start Podman Machine

If you haven't already set up a Podman machine, run the following commands:

```bash
# Initialize a new Podman machine (adjust resources as needed)
podman machine init --cpus 2 --memory 2048 --disk-size 20

# Start the Podman machine
podman machine start
```

### 2. Run Neo4j Container

Run the Neo4j container with the required plugins (**APOC** and **GenAI**) for GraphRAG and vector search functionality.

```bash
podman run -d \
  --name neo4j-football \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -e NEO4J_PLUGINS='["apoc", "genai"]' \
  -e NEO4J_dbms_security_procedures_unrestricted=apoc.*,genai.* \
  -e NEO4J_dbms_security_procedures_allowlist=apoc.*,genai.* \
  neo4j:5
```

**Parameters Explained:**
- `-d`: Runs the container in detached mode (background).
- `--name neo4j-football`: Assigns a readable name to the container.
- `-p 7474:7474`: Maps the HTTP port for the Neo4j Browser.
- `-p 7687:7687`: Maps the Bolt port for database connections.
- `-e NEO4J_AUTH=neo4j/password123`: Sets the initial username (`neo4j`) and password (`password123`).
- `-e NEO4J_PLUGINS='["apoc", "genai"]'`: Enables the APOC (Awesome Procedures on Cypher) and GenAI plugins.
- `-e NEO4J_dbms_security_procedures_unrestricted=apoc.*,genai.*`: Allows unrestricted access to these procedures, which is necessary for advanced graph operations and integration with LLMs.

### 3. Verify the Setup

Check if the container is running:

```bash
podman ps
```

You can also check the logs to ensure Neo4j has started successfully:

```bash
podman logs neo4j-football
```

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password123
NEO4J_DATABASE=neo4j

# Local LM Studio Setup
OPENAI_API_KEY=lm-studio
OPENAI_ENDPOINT=http://localhost:1234/v1
OPENAI_ENDPOINT_EMBEDDINGS=http://localhost:1234/v1
OPENAI_MODEL=local-model
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5
```

## Note on Embeddings
Since the Neo4j GenAI plugin has limitations with local HTTP endpoints in some environments, this project uses **Python-side embedding generation**.
- Use `football_kg_embeddings.py` to generate and upload vectors to the database.
- The chatbot automatically handles query vectorization in Python before querying Neo4j.

## Accessing the Neo4j Browser

Once the container is running, you can access the graphical interface at:
[http://localhost:7474](http://localhost:7474)

Log in with:
- **Username:** `neo4j`
- **Password:** `password123`

## Management Commands

- **Stop the container:** `podman stop neo4j-football`
- **Start the container:** `podman start neo4j-football`
- **Remove the container:** `podman rm -f neo4j-football`
