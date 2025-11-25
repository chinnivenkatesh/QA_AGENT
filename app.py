import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
FASTAPI_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="Autonomous QA Agent (Local)", layout="wide")

if 'uploaded_files' not in st.session_state: st.session_state['uploaded_files'] = []
if 'test_cases_json' not in st.session_state: st.session_state['test_cases_json'] = None
if 'generated_script' not in st.session_state: st.session_state['generated_script'] = None

st.title("🤖 Autonomous QA Agent (Local Ollama)")

# --- PHASE 1: Knowledge Base Ingestion ---
st.header("1. 🧠 Knowledge Base Ingestion")
col1, col2 = st.columns(2)
with col1:
    support_docs = st.file_uploader("Support Docs", accept_multiple_files=True, type=['md', 'txt', 'json', 'pdf'])
with col2:
    html_file = st.file_uploader("Target HTML", accept_multiple_files=False, type=['html'])

if support_docs or html_file:
    all_files = support_docs
    if html_file: all_files.append(html_file)
    st.session_state['uploaded_files'] = all_files
    st.info(f"Ready: {len(all_files)} files")

if st.button("Build Knowledge Base", type="primary"):
    if not st.session_state.get('uploaded_files'):
        st.error("Upload files first.")
    else:
        with st.spinner("Building..."):
            try:
                files = [("files", (f.name, f.getvalue(), f.type)) for f in st.session_state['uploaded_files']]
                res = requests.post(f"{FASTAPI_URL}/build_kb", files=files)
                if res.status_code == 200:
                    st.success("✅ Knowledge Base Built!")
                else:
                    st.error(f"Failed: {res.text}")
            except Exception as e:
                st.error(f"Error: {e}")

# --- PHASE 2: Test Case Generation ---
st.divider()
st.header("2. 💡 Test Case Generation")
prompt = st.text_area("Prompt:", value="Generate positive and negative test cases for discount code.")

if st.button("Generate Test Cases", type="primary"):
    with st.spinner("Generating..."):
        try:
            res = requests.post(f"{FASTAPI_URL}/generate_test_cases", json={"prompt": prompt})
            if res.status_code == 200:
                st.session_state['test_cases_json'] = res.json().get('test_cases', "{}")
                st.success("✅ Generated!")
            else:
                st.error(f"Failed: {res.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# Debug View & Table
if st.session_state['test_cases_json']:
    with st.expander("🔍 Debug: View Raw JSON Response"):
        st.code(st.session_state['test_cases_json'], language='json')

    try:
        raw_data = st.session_state['test_cases_json']
        if isinstance(raw_data, str):
            tc_data = json.loads(raw_data)
        else:
            tc_data = raw_data
            
        tc_list = tc_data.get("test_cases", [])
        
        if tc_list:
            st.dataframe(tc_list, use_container_width=True)
            
            # --- PHASE 3: Script Generation ---
            st.divider()
            st.header("3. ✍️ Script Generation")
            opts = {f"{t.get('Test_ID')}: {t.get('Test_Scenario')}": t for t in tc_list}
            sel = st.selectbox("Select Case:", list(opts.keys()))
            
            if st.button("Generate Script"):
                with st.spinner("Writing code..."):
                    t = opts[sel]
                    res = requests.post(f"{FASTAPI_URL}/generate_script", json={
                        "test_case_scenario": t.get('Test_Scenario'),
                        "grounded_in": t.get('Grounded_In')
                    })
                    if res.status_code == 200:
                        script = res.json().get('script', '# No script returned')
                        st.session_state['generated_script'] = script
                        st.code(script, language='python')
                    else:
                        st.error(f"Failed: {res.text}")
        else:
            st.warning("JSON was valid but contained no 'test_cases' list.")
    except json.JSONDecodeError:
        st.error("Failed to parse JSON for display. Check 'Debug' above.")