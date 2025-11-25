import os
import textwrap
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import FAISS

def generate_selenium_script(test_scenario: str, grounding_doc: str, html_content: str, retriever: FAISS) -> str:
    try:
        model_name = os.environ.get("OLLAMA_MODEL", "llama3")
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.0)
        
        retrieval_query = f"Rules for: {test_scenario}"
        retrieved_docs = retriever.as_retriever(k=3).invoke(retrieval_query)
        rules_context = "\n---\n".join([d.page_content for d in retrieved_docs])

        prompt = textwrap.dedent(f"""
            You are a Selenium Python Expert. Write a runnable script.
            SCENARIO: {test_scenario}
            RULES: {rules_context}
            HTML: {html_content[:4000]}
            Output ONLY Python code. No markdown.
        """)
        
        response = llm.invoke(prompt)
        return response.content.replace("```python", "").replace("```", "").strip()
    except Exception as e:
        return f"# ERROR: {str(e)}"