# LocalLamaSearch

This is a simple implementation of a local search server that uses LLMs to search for local documents.

## Installation
Make sure to tune `docker-compose.hardware.yml` to your needs. 

After starting running docker compose, you can run the following commands to bootstrap the models and test the servers:
```sh
pip3 install -r requirements.txt
python3 scripts/bootstrap_models.py
python3 scripts/llm_embedding.py
```