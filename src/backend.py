import os
import shutil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

from .knowledge_base import build_knowledge_base, get_retriever, get_html_content, FAISS_DB_PATH
from .agent_test_case import generate_test_cases
from .agent_script_gen import generate_selenium_script

app = Flask(__name__)
UPLOAD_DIR = "uploaded_files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.route("/build_kb", methods=["POST"])
def build_kb_endpoint():
    # 1. Clean up previous DB only (Keep upload dir for Phase 3)
    if os.path.exists(FAISS_DB_PATH):
        try:
            shutil.rmtree(FAISS_DB_PATH)
        except PermissionError as e:
             return jsonify({"status": "error", "message": f"DB deletion failed: {e}"}), 500
            
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    file_paths = []
    uploaded_files = request.files.getlist("files")
    
    for file in uploaded_files:
        filename = secure_filename(file.filename)
        file_location = os.path.join(UPLOAD_DIR, filename)
        file.save(file_location)
        file_paths.append(file_location)
    
    try:
        build_knowledge_base(file_paths)
        return jsonify({"status": "success", "message": "Knowledge Base Built Successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"KB Build Failed: {e}"}), 500

@app.route("/generate_test_cases", methods=["POST"])
def generate_test_cases_endpoint():
    data = request.get_json()
    user_prompt = data.get("prompt")
    retriever = get_retriever()
    if retriever is None:
        return jsonify({"status": "error", "message": "Knowledge base not found."}), 400

    try:
        test_cases_json = generate_test_cases(user_prompt, retriever)
        return jsonify({"status": "success", "message": "Test cases generated.", "test_cases": test_cases_json}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/generate_script", methods=["POST"])
def generate_script_endpoint():
    data = request.get_json()
    test_case_scenario = data.get("test_case_scenario")
    grounding_doc = data.get("grounded_in")
    retriever = get_retriever()
    html_content = get_html_content()

    if not retriever or not html_content:
        return jsonify({"status": "error", "message": "KB or HTML missing."}), 400

    try:
        script = generate_selenium_script(test_case_scenario, grounding_doc, html_content, retriever)
        return jsonify({"status": "success", "message": "Script generated.", "script": script}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500