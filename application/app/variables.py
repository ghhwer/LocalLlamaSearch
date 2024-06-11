import os

# Files and Directories
ROOT_FS_LOCATION = os.environ.get("APP_ROOT_FS_LOCATION", "data")
ROOT_RETENTION_LOCATION = os.environ.get("APP_ROOT_RETENTION_LOCATION", "storage")
VECTOR_STORE_LOCATION = f"{ROOT_RETENTION_LOCATION}/vector_store"
SYNC_INTERVAL_SECONDS = os.environ.get("APP_SYNC_INTERVAL_SECONDS", 10)

# AI Models
EMBEDDING_MODEL = os.environ.get("APP_EMBEDDING_MODEL", "jina/jina-embeddings-v2-small-en")
MAIN_LLM = os.environ.get("APP_MAIN_LLM", "llama3:8b-instruct-q8_0")
N_CTX = os.environ.get("APP_N_CTX", 8192)

# ENDPOINTS 
GPU_SERVER_URL = os.environ.get("APP_GPU_SERVER_URL", 'http://localhost:11434')
CPU_SERVER_URL = os.environ.get("APP_CPU_SERVER_URL", 'http://localhost:11435')

# Other Constants
PARAGRAPH_SEP = os.environ.get("APP_PARAGRAPH_SEP", "\n\n\n")
CHUNK_SIZE = os.environ.get("APP_CHUNK_SIZE", 1000)
OVERLAP = os.environ.get("APP_OVERLAP", 20)
MIN_CHUNK_SIZE = os.environ.get("APP_MIN_CHUNK_SIZE", 200)
CHUNKING_REGEX = os.environ.get("APP_CHUNKING_REGEX", '[^,\.;]+[,\.;]?')
WORD_SEP = os.environ.get("APP_WORD_SEP", ' ')
TOP_K_RESULTS = os.environ.get("APP_TOP_K_RESULTS", 2)
NEIGHBOORS = os.environ.get("APP_NEIGHBOORS", 1)
ASSISTANT_TEMPERATURE = os.environ.get("APP_ASSISTANT_TEMPERATURE", 0.2)
KEYWORDS_TEMPERATURE = os.environ.get("APP_KEYWORDS_TEMPERATURE", 0.2)
