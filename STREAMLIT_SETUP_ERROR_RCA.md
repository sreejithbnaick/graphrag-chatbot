# RCA: Streamlit Setup and Import Resolution

## 1. Setup Attempt
The goal was to run the Football Knowledge Graph Chatbot using Streamlit from the project's virtual environment.

### Commands Executed:
```bash
# Initial run attempt
./venv/bin/streamlit run football_kg_chatbot.py
```

---

## 2. Issues Encountered

### Issue A: Executable Not Found
**Error:** `bash: ./venv/bin/streamlit: No such file or directory`
- **Cause:** `streamlit` was not listed in the initial `requirements.txt` and thus not installed in the virtual environment.
- **Fix:** 
    1. Added `streamlit` to `requirements.txt`.
    2. Ran `./venv/bin/pip install -r requirements.txt`.

### Issue B: Onboarding Block
During the first run, Streamlit halted execution waiting for an email address for onboarding.
- **Fix:** Sent an empty input to the interactive prompt (`send_command_input`) to bypass and proceed to server startup.

### Issue C: Import Error (Runtime)
Once the server started, the application crashed with the following error visible in the logs:
**Error:** `ModuleNotFoundError: No module named 'langchain.prompts'`
- **Context:** The code was attempting `from langchain.prompts.prompt import PromptTemplate`.

---

## 3. Root Cause Analysis (Issue C)

The `langchain.prompts` namespace is considered legacy in newer versions of the LangChain ecosystem. With the migration to **LangChain 0.3+** and **Python 3.14**, the community has transitioned to more modular packages.

The virtual environment had `langchain-core` and `langchain` installed, but the older hierarchical import path used in `football_kg_chatbot.py` was no longer available or was conflicting with the strict module isolation in the newer Python environment.

---

## 4. Resolution

### The "Core" Import Fix
The import was updated to use the modern, stable path provided by the `langchain-core` package.

**Target File:** `football_kg_chatbot.py`

**Old Code:**
```python
from langchain.prompts.prompt import PromptTemplate
```

**New Code:**
```python
from langchain_core.prompts import PromptTemplate
```

### Verification
1.  Verified that `langchain-core` was present in the environment via `pip list`.
2.  Tested the import directly via Python CLI:
    ```bash
    ./venv/bin/python -c "from langchain_core.prompts import PromptTemplate; print('Success')"
    ```
3.  The Streamlit server automatically detected the file change and successfully reloaded the application.

---

## 5. Summary of Setup Commands
To reproduce a clean setup, the following sequence is used:
```bash
# 1. Update requirements
echo "streamlit" >> requirements.txt

# 2. Install dependencies
./venv/bin/pip install -r requirements.txt

# 3. Launch the app
./venv/bin/streamlit run football_kg_chatbot.py
```
