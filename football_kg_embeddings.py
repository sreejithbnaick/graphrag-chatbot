from dotenv import load_dotenv
import os
from neo4j import GraphDatabase
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get Neo4j credentials from environment
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

# LM Studio / OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "lm-studio")
OPENAI_BASE_URL = os.getenv("OPENAI_ENDPOINT_EMBEDDINGS") # Base URL for LM Studio (local)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-nomic-embed-text-v1.5")

# Initialize OpenAI client for LM Studio
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

def get_embedding(text):
    try:
        response = client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for '{text[:20]}...': {e}")
        return None

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH)
    
    # 1. Create Vector Index (768 dimensions for Nomic)
    print("Creating/Checking vector index...")
    with driver.session(database=NEO4J_DATABASE) as session:
        session.run("DROP INDEX football_players_embeddings IF EXISTS")
        session.run("""
            CREATE VECTOR INDEX football_players_embeddings IF NOT EXISTS
            FOR (p:Player) ON (p.embedding)
            OPTIONS {
              indexConfig: {
                `vector.dimensions`: 768,
                `vector.similarity_function`: 'cosine'
              }
            }
        """)

    # 2. Fetch Players needing embeddings
    print("Fetching players from Neo4j...")
    players = []
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run("MATCH (p:Player) RETURN id(p) as id, p.name as name, p.matches as matches, p.goals as goals")
        for record in result:
            players.append(record)

    # 3. Generate and Update Embeddings
    print(f"Updating embeddings for {len(players)} players...")
    for p in players:
        description = f"{p['name']} played {p['matches']} matches and scored {p['goals']} goals."
        vector = get_embedding(description)
        
        if vector:
            with driver.session(database=NEO4J_DATABASE) as session:
                session.run(
                    "MATCH (p) WHERE id(p) = $id SET p.embedding = $vector",
                    {"id": p["id"], "vector": vector}
                )
    
    print("Embeddings updated successfully!")
    
    # 4. Test Search
    print("\nTesting similarity search (Who is similar to Messi?)...")
    query_text = "Who is similar to Messi?"
    query_vector = get_embedding(query_text)
    
    if query_vector:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                CALL db.index.vector.queryNodes('football_players_embeddings', 5, $vector)
                YIELD node, score
                RETURN node.name as name, node.goals as goals, score
            """, {"vector": query_vector})
            
            for record in result:
                print(f" - {record['name']} (Goals: {record['goals']}, Score: {record['score']:.4f})")

    driver.close()

if __name__ == "__main__":
    main()
