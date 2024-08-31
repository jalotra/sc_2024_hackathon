import json
from typing import List
import streamlit as st
import requests

st.title("RAG application Using RAPTOR") 
st.divider()

BACKEND_HOST = "localhost"
BACKEND_PORT = "5000"


def get_session_state():
    if "session_state" not in st.session_state:
        st.session_state.session_state = {}
    else:
        return st.session_state.session_state
    return st.session_state.session_state


def add_document_to_datastore(user_id, files):
    print(files)
    url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/rag/add_document?user_id={user_id}"
    files_to_upload = [("files", file) for file in files]
    response = requests.post(
        url, headers={"accept": "application/json"}, data={}, files=files_to_upload
    )

    if response.status_code != 200:
        raise Exception(response.text)
    else:
        return response.json()


def build_rag_and_save(document_ids: List[int], user_id: int):
    url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/rag/build_save_tree?user_id={user_id}"
    print(document_ids)
    response = requests.post(
        url, headers={"accept": "application/json"}, json={"ids": document_ids}
    )

    if response.status_code != 200:
        raise Exception(response.text)
    else:
        rag_id = response.json().get("rag_id")
        return rag_id


def ask_questions(question: str, tree_id: str):
    print(tree_id)
    url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/rag/load_tree_and_QA?tree_id={tree_id}&question={question}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


session_state = get_session_state()
st.header("Enter Tree Id")
with st.form("upload-form", clear_on_submit=False):
    tree_id = st.text_input("")
    button = st.form_submit_button("Submit ?")
    if button and tree_id:
        session_state["tree_id"] = tree_id

if "tree_id" in session_state.keys():
    st.header("Chat on top of uploaded files here")
    messages = st.container(height=300)
    if prompt := st.chat_input("Enter Question :"):
        messages.chat_message("user").write(prompt)
        messages.chat_message("assistant").write(
            ask_questions(prompt, tree_id=session_state["tree_id"])
        )
