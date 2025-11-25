import json
import os
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from typing import List
from langchain_community.vectorstores import FAISS

class TestCase(BaseModel):
    Test_ID: str = Field(description="Unique ID")
    Feature: str = Field(description="Feature")
    Test_Scenario: str = Field(description="Scenario")
    Expected_Result: str = Field(description="Result")
    Grounded_In: str = Field(description="Source")

class TestPlan(BaseModel):
    test_cases: List[TestCase]

def clean_and_repair_json(text: str) -> List[dict]:
    print(f"DEBUG RAW OUTPUT: {text}")
    try:
        text = re.sub(r'^```json\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
        text = text.strip()
        
        data = json.loads(text)
        if isinstance(data, list): return data
        if isinstance(data, dict) and "test_cases" in data: return data["test_cases"]
        
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match: return json.loads(match.group(0))
    except: pass
    
    return [{"Test_ID": "TC-GEN", "Feature": "Gen", "Test_Scenario": text[:200], "Expected_Result": "See desc", "Grounded_In": "Model"}]

def generate_test_cases(user_prompt: str, retriever: FAISS) -> str:
    model_name = os.environ.get("OLLAMA_MODEL", "llama3")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.1)
    parser = StrOutputParser()
    
    retrieved_docs = retriever.as_retriever(k=4).invoke(user_prompt)
    context = "\n---\n".join([f"Doc: {d.metadata.get('source_document', 'Unk')}\n{d.page_content}" for d in retrieved_docs])
    
    # Using {{ }} to escape JSON example for LangChain
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a QA Engineer. Return a raw JSON LIST of test cases. Example: [{{ \"Test_ID\": \"TC01\", \"Feature\": \"Login\", \"Test_Scenario\": \"...\", \"Expected_Result\": \"...\", \"Grounded_In\": \"...\" }}]. Do not use Markdown."),
        ("human", "Context: {context}\n\nTask: {request}")
    ])
    
    rag_chain = prompt_template | llm | parser
    try:
        raw_result = rag_chain.invoke({"context": context, "request": user_prompt})
        test_case_list = clean_and_repair_json(raw_result)
        return json.dumps({"test_cases": test_case_list}, indent=2)
    except Exception as e:
        return json.dumps({"test_cases": [{"Test_ID": "ERR", "Feature": "Error", "Test_Scenario": str(e), "Expected_Result": "Check Ollama", "Grounded_In": "System"}]})