import hmac
from openai import AzureOpenAI
import streamlit as st
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from chromadb.config import Settings
from llama_index.core import PromptTemplate

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


#st.title(':green[AgroGPT]')
#st.markdown("<h1 style='color: darkgreen;'>PlanteGPT</h1>", unsafe_allow_html=True)

# plant/flower unicodes
# U+1F33x   
st.markdown("<h1 style='color: darkgreen;'>SEGES-GPT \U0001F33B</h1>", unsafe_allow_html=True)

st.markdown("<p style='color: darkgreen;'>Velkommen til SEGES-GPT - en chatbot der kan besvare spørgsmål<br>om indholdet i artikler på Landsbrugsinfo.dk.</p>",
             unsafe_allow_html=True)

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


client = AzureOpenAI(api_key=st.secrets["OPENAI_API_KEY"], 
                api_version="2024-05-01-preview", 
                azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"])

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=st.secrets["OPENAI_API_KEY"],
    model_name="text-embedding-ada-002",
    api_type="azure",
    api_version="2024-05-01-preview"
)

chroma_client_load = chromadb.PersistentClient(
    path="./landsforsøg/chromadb",
    settings=Settings(allow_reset=True)
)

# Get the existing collection by name
collection_load = chroma_client_load.get_collection(name="landsforsoeg", embedding_function=openai_ef)


if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt4"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Define the default prompt template


default_prompt = """You are a helpful assistant that answers questions about the content of documents and provides detailed expert advice. 
    You must provide your answer in the Danish language.
    If the answer contains multiple steps or points, provide the answer in a bullet format. Below the answer ,y ou should add the source of the information (file name and page number) formatted as in the following example.
    Kilde: filnavn.pdf, side 2
    """

end_of_prompt= """\n    ---------------------\n    {context}\n    ---------------------\n    Given the context information and not prior knowledge, answer the query.\n    Query: {query}\n    Answer: \n"""

# Add a text input in the sidebar to configure the prompt template
prompt_template = st.sidebar.text_area("Prøv en anden prompt", default_prompt, height=350)


# add a button to reset the chat
if st.sidebar.button("Ny chatsession"):
    st.session_state.messages = []

if query := st.chat_input("Stil et spørgsmål"):
    
    #RAG
    result = collection_load.query(query_texts=[query], n_results=5)
    context = result["documents"][0]
    metadatas = result["metadatas"][0]
    file_names = [idx["file_name"] for idx in metadatas]   
    page_numbers = [idx["page_label"] for idx in metadatas]

    # append file namea and page numbers to list elements in context
    for i in range(len(context)):
        context[i] = context[i] + f" (filename: {file_names[i]}, page_number: {page_numbers[i]})"

    
    prompt = PromptTemplate(f"{prompt_template} {end_of_prompt}")

    
    message = prompt.format(query=query, context="\n\n".join(context))

    st.session_state.messages.append({"role": "user", "content": query}) #message
    
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in [{"role": "user", "content": message}]#st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.write("Kontekst:")
    st.json(context, expanded=False)

