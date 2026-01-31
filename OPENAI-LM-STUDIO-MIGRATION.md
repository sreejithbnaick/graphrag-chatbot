# Root Cause Analysis: OpenAI to LM Studio Migration

## Executive Summary
During the migration from OpenAI's cloud API to a local LM Studio instance for GraphRAG, we encountered persistent authentication and connection errors when using Neo4j's internal `genai` plugin. Despite successful network connectivity between the Podman container and the host machine, the Neo4j `genai.vector.encode` function failed to utilize the local endpoint. The resolution involved decoupling the embedding generation from the database plugin and moving it to the Python application layer.

---

## 1. Problem Statement
The application failed to generate or query vector embeddings when switching from `api.openai.com` to `localhost:1234` (LM Studio).
**Error received:**
```
neo4j.exceptions.ClientError: {neo4j_code: Neo.ClientError.Procedure.ProcedureCallFailed} 
{message: Failed to invoke function `genai.vector.encode`: Caused by: 
org.neo4j.genai.util.GenAIProcedureException: Not authorized to make API request; check your credentials.}
```

---

## 2. Investigation & Debugging Steps

### Hypothesis 1: Network Isolation
**Test:** Ran `curl` from within the Podman machine to the host.
**Command:** `podman machine ssh "curl -v http://host.containers.internal:1234/v1/models"`
**Result:** **Success.** The Podman VM could reach the host's LM Studio instance.

### Hypothesis 2: Incorrect Endpoint/Port
**Test:** Modified the endpoint to an invalid port (9999) to see if the error message changed.
**Command:** 
```cypher
RETURN genai.vector.encode('test', 'OpenAI', {
  token: 'none', 
  endpoint: 'http://192.168.127.254:9999/v1'
})
```
**Result:** **Fail.** The error remained exactly same ("Not authorized"), suggesting the plugin was not even attempting a network connection to the provided endpoint.

### Hypothesis 3: Protocol Restriction (HTTP vs HTTPS)
**Test:** Created a custom **Python Debug Proxy** (supporting both HTTP and HTTPS) to intercept traffic.
**Commands:** 
- `python3 debug_proxy.py` (Listening on port 1235)
- `podman exec ... "CALL apoc.load.json('http://192.168.127.254:1235/v1/models')"`
**Results:**
- `apoc.load.json` **reached the proxy**.
- `genai.vector.encode` **did NOT reach the proxy**.

---

## 3. Root Cause Discovery
The **Neo4j GenAI Plugin (v5.x)** appears to have built-in restrictions or bugs regarding the `endpoint` parameter for the "OpenAI" provider:
1.  **Hardcoded Behavior**: The plugin likely ignores the `endpoint` parameter and defaults to `https://api.openai.com` regardless of configuration.
2.  **Strict Token Validation**: It may perform pre-flight validation on the token format, rejecting "lm-studio" as an unauthorized/malformed credential before a request is even sent.
3.  **Encrypted Protocol Requirement**: The plugin might enforce `https://`, making it incompatible with local `http://` developers setups.

---

## 4. Final Solution (The "Python-Side" Approach)

To bypass the plugin limitations, the architecture was changed from **In-Database Vectorization** to **Application-Side Vectorization**.

### Key Changes Made:

1.  **Decoupled Embeddings**: 
    - Created a standalone script `football_kg_embeddings.py` that uses the standard `openai` Python library to generate vectors on the host Mac.
    - The script then pushes the raw `List[float]` vectors into Neo4j via a standard `SET p.embedding = $vector` Cypher command.

2.  **Manual Vector Indexing**:
    - Created the vector index manually with the specific dimensions for the local model (e.g., **768** dimensions for `nomic-embed-text` vs 1536 for OpenAI).

3.  **Chatbot Logic Update**:
    - Updated `football_kg_chatbot.py` to vectorize the user’s query in Python **before** calling Neo4j.
    - Updated the Cypher prompt template to accept a `$query_vector` parameter instead of trying to generate it inside the graph.

---

## 5. Lessons Learned
- **Plugin Opacity**: Database plugins are often "black boxes" that don't provide granular logs for network failures.
- **Application Control**: Performing feature engineering (like embeddings) in the application layer is more portable and easier to debug than relying on database-side plugins for external API calls.
- **Mocking for Debugging**: Using a simple HTTP proxy is the fastest way to verify if a database-side process is truly making outbound requests.
