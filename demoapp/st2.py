import os
import requests
import json

import hmac
import streamlit as st


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password er forkert, prøv igen.")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


def create_tf_serving_json(data):
    return {'inputs': {name: data[name].tolist() for name in data.keys()} if isinstance(data, dict) else data.tolist()}

def ask_model(query):
    url = 'https://adb-3134335201692067.7.azuredatabricks.net/serving-endpoints/agents_raw_dev-segesgpt-SEGESGPTdev/invocations'
    headers = {'Authorization': f'Bearer {st.secrets["DATABRICKS_TOKEN"]}', 'Content-Type': 'application/json'}
    data_json = json.dumps({'messages': [{'role': 'user', 'content': query}]})
    response = requests.request(method='POST', headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(f'Request failed with status {response.status_code}, {response.text}')
    return response.json()


# Title and description
st.markdown("<h1 style='color: darkgreen;'>SEGES-GPT</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: darkgreen;'>Velkommen til SEGES-GPT - en chatbot der kan besvare spørgsmål<br>om indholdet i artikler på Landsbrugsinfo.dk.</p>",
             unsafe_allow_html=True)

# style
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# add a button to reset the chat
if st.sidebar.button("Ny chatsession"):
    st.session_state.messages = []

if query := st.chat_input("Stil et spørgsmål"):
    
    st.session_state.messages.append({"role": "user", "content": query}) #message
    
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        stream = ask_model(query)
        stream = stream['choices'][0]['message']['content']

        response = st.write(stream)
    st.session_state.messages.append({"role": "assistant", "content": stream})