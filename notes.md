
# RAG Considerations

## Indexing / Vector store
Azure AI Search offers all features including hybrid search. CosmosDB is a more limited option.
https://docs.llamaindex.ai/en/stable/module_guides/storing/vector_stores/

## Embedding
The default model is OpenAI's `text-embedding-ada-002` model. There are better performing options. It is unclear which of these models will perform best in a Danish context.

Leaderboard:
https://huggingface.co/spaces/mteb/leaderboard

Different **Chunking strategies** may also be considered.

*We need to consider how or whether to extract information from images, tables and charts*

## Retrieval
The number of chunks to retrieve can be set. The default is 5, with similarity measured in **cosine** distance.

Embedding-based search is most common, whereas hybrid search (adding key words) may be better.

## Queries and answers

### LLM
ChatGPT4 seems to do the job well.

### Postprocessing / reranking
Time weighted reranking may be ideal, given that more recent information abut a topic is usually more relevant.

### Synthesizing answers
Compact vs default (more detailed)?