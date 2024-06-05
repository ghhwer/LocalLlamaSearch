# LocalLamaSearch

This is a simple implementation of a local search server that uses LLMs to search for local documents.

## Installation
Currently there is no installation script also there is no CPU only version. 
The only way to run this is to have a GPU with CUDA capabilities.

Make sure that you have a model in the `models` directory. You can download llama.cpp compatible model from the [Hugging Face Model Hub](https://huggingface.co/models). Don't forget to update the `docker-compose.yml` file with the model name.

This project is just for educational purposes and is not intended to be used in production. This is the reason why there is no installation script hehe.