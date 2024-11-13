
# RAG Considerations

## Indexing / Vector stores
A local vector store requires too much disk space.

Azure AI Search offers all features including hybrid search. CosmosDB is a more limited option.
https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores/

## Embedding
The default model is OpenAI's `text-embedding-ada-002` model. There are better performing options. It is maybe unclear which of these models will perform best in a Danish context.

Leaderboard:
https://huggingface.co/spaces/mteb/leaderboard

Different **Chunking strategies** may also be considered.

*We need to consider how or whether to extract information from images, tables and charts*

## Retrieval
The number of chunks to retrieve can be set. The default is 5, with similarity measured as **cosine** distance.

Consider a similarity cut-off, e.g. .7.

Embedding-based search is most common, whereas hybrid search (adding key words) may be better.

## Queries and answers

### LLM
ChatGPT4 seems to do the job well.

### Postprocessing / reranking
Time weighted reranking may be ideal, given that more recent information about a topic is usually more relevant.

### Synthesizing answers
Compact vs default (more detailed)?

### Text-to-sql

To avoid unfortunate queries that could make changes to the DB, A copy of the DB should be provisioned with a read-only user.

## Deployment

docker login peermslearncr.azurecr.io

docker tag streamlit peermslearncr.azurecr.io/streamlit

docker push peermslearncr.azurecr.io/streamlit

## Switching to query engine

```
# try this

#from llama_index.core import VectorStoreIndex
#from llama_index.vector_stores.chroma import ChromaVectorStore
#from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding


embedding = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key=os.getenv("OPENAI_API_KEY"),  
    api_version=os.getenv("OPENAI_API_VERSION"), # https://learn.microsoft.com/en-us/azure/ai-services/openai/reference?WT.mc_id=AZ-MVP-5004796
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
vector_store = ChromaVectorStore(chroma_collection=collection_load)
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=openai_ef,
)
query_engine = index.as_query_engine()
response = query_engine.query("hvordan bekæmpes væselhale?")
```
