GraphRAG Football Chatbot

Forked from:
https://github.com/SridharSampath/graphrag-football-chatbot#

GraphRAG Football Chatbot is an chatbot that integrates Neo4j, OpenAI embeddings, and LLMs to provide structured football knowledge retrieval using GraphRAG (Graph + Retrieval-Augmented Generation).


✅ Neo4j Knowledge Graph: Stores players, clubs, leagues, and performance stats.

✅ Graph-Based Retrieval: Converts queries into Cypher for structured retrieval.

✅ OpenAI Embeddings: Enables similarity search for player comparisons.

✅ Streamlit Chatbot UI: User-friendly interface for football-related queries.


Updated Code:
* Neo4j podmain setup documentation
* Use Local LLM (LM Studio) instead of OpenAI for embeddings and chat
* OpenAI to LM Studio Migration issues & fixes
* Streamlit Chatbot Error & fixes
* Debug proxy to diagnose podman & LM Studio connection issues


Steps to run:
1. Pip install requirements
2. Setup Neo4j container, refer to neovj podmain setup documentation
3. Run python football_kg_loader.py to load the data into the knowledge graph
4. Run python football_kg_embeddings.py to generate embeddings for the players
5. Start the chatbot using ./start_app.sh
6. Stop the chatbot using ./stop_app.sh
