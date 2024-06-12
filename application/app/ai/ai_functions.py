import requests
import variables
from ai.string_functions import sentense_split_raw_text
from ai.vector_search import query_vector_emb

# Define functions to interact with the models
def get_embeddings(text):
    response = requests.post(f'{variables.CPU_SERVER_URL}/api/embeddings', json={
        "model": variables.EMBEDDING_MODEL,
        "prompt": text
    })
    return response.json()['embedding']

def get_model_response(history, temperature=0.1):
    response = requests.post(f'{variables.GPU_SERVER_URL}/api/chat', json={
        "model": "llama3",
        "messages": history,
        "options":{
            "temperature": temperature,
            "num_ctx": variables.N_CTX,
        },
        "stream": False
    })
    response_json = response.json()
    llm_token_count = response_json.get('eval_count')
    prompt_token_count = response_json.get('prompt_eval_count')
    return response.json().get('message').get('content'), llm_token_count, prompt_token_count

def build_vectors_for_text(text, uri):
    vector_data = []
    chunks = sentense_split_raw_text(
        text,
        chunk_target_size=variables.CHUNK_SIZE,
        overlap=variables.OVERLAP,
        min_chunk_size=variables.MIN_CHUNK_SIZE,
        paragraph_sep=variables.PARAGRAPH_SEP,
        chunking_regex=variables.CHUNKING_REGEX,
        word_sep=variables.WORD_SEP
    )
    for i, chunk in enumerate(chunks):
        # Get the embeddings for the chunk
        vector = get_embeddings(chunk) 
        # The vector fetch could by improved to be done in parallel and using batching
        vector_data.append({'uri': uri, 'text': chunk, 'vector': vector, 'chunk_id': i})
    return vector_data

def make_keywords(query):
  SYSTEM_PROMPT = f"""You are a helpful assistant that has access to pre-fetched query results.
  Your job is to transform the user query into keywords separated by commas.

  To ensure a good job follow the instructions:
      1. Do not include any stopwords in the keywords.
      2. Make sure to include the most important keywords first.
      3. Do not explain the keywords, just list them.
  """
  history = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Why is the sky blue?"},
    {"role": "assistant", "content": "sky color explanation"},
    {"role": "user", "content": f"How does GPU and CPU differ?"},
    {"role": "assistant", "content": "GPU, CPU, difference"},
    {"role": "user", "content":query}
  ]
  text, _, _ = get_model_response(history, variables.KEYWORDS_TEMPERATURE)
  return [x.strip() for x in text.split(",")]

def ai_query(query):
    keywords = make_keywords(query)
    embeddings = get_embeddings(', '.join(keywords))
    emb_similarity, detail = query_vector_emb(
        embeddings,
        variables.VECTOR_STORE_LOCATION,
        top_k=variables.TOP_K_RESULTS,
        n_neighboors=variables.NEIGHBOORS,
        min_similarity=variables.MIN_SIMILARITY
    )
    
    SYSTEM_PROMPT = """You are an expert Q&A system that is trusted around the world.
    Always answer the query using the provided context information, and not prior knowledge.
    Some rules to follow:
    1. Never directly reference the given context in your answer.
    2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.
    3. When answering based on the context, always provide references from the context information.
    4. Please format your answer in markdown."""
    USER_PROMPT = """Context information is below.
    ---------------------
    [CONTEXT]
    ---------------------
    Given the context information and NOT prior knowledge, answer the query.
    Query: [QUERY]
    """

    # Fetch the context information
    
    final_context = ""
    for sub_context in emb_similarity:
        final_context += f"URI: {sub_context['uri']}\nText: {sub_context['text']}\n\n"
    USER_PROMPT = USER_PROMPT.replace("[CONTEXT]", final_context)
    USER_PROMPT = USER_PROMPT.replace("[QUERY]", query)
    history = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ]
    response, llm_token_count, prompt_token_count = get_model_response(history, variables.ASSISTANT_TEMPERATURE)
    return {
      'llm_response':response,
      'keywords_used': keywords, 
      'search_details':detail, 
      'llm_token_count':llm_token_count,
      'prompt_token_count':prompt_token_count,
      'warn': prompt_token_count > variables.N_CTX,
      'prompt_history': history
    }

def ai_follow_up_query(query, prompt_history):
    prompt_history.append({"role": "user", "content": query})
    response, llm_token_count, prompt_token_count = get_model_response(prompt_history, variables.ASSISTANT_TEMPERATURE)
    return {
      'llm_response':response,
      'llm_token_count':llm_token_count,
      'prompt_token_count':prompt_token_count,
      'warn': prompt_token_count > variables.N_CTX,
      'prompt_history': prompt_history
    }