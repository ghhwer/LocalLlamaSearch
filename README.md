# LocalLamaSearch

This is a simple implementation of a local search server that uses LLMs to search for local documents.

## Installation
Currently there is no installation script also there is no CPU only version. 
The only way to run this is to have a GPU with CUDA capabilities.

Make sure to tune `docker-compose.hardware.yml` to your needs. 
After starting docker, please run /scripts/bootstrap_models.py to download the models.
You may want to run /scripts/llm_embedding.py to test both the LLM and the embeddings endpoints.