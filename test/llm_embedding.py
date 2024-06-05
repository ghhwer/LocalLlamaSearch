from openai import OpenAI
import requests

# Pull llama 3 onto the GPU Server and PULL 
GPU_SERVER_URL = 'http://localhost:11434'
CPU_SERVER_URL = 'http://localhost:11435'

def main():
    client = OpenAI(
        base_url = f'{GPU_SERVER_URL}/v1',
        api_key='ollama', # required, but unused
    )

    response = client.chat.completions.create(
    model="llama3",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a joke."},
    ]
    )
    print("LLM Joke:")
    print(response.choices[0].message.content)

    response = requests.post(f'{CPU_SERVER_URL}/api/embeddings', json={
        "model": "jina/jina-embeddings-v2-small-en",
        "prompt": "Llamas are members of the camelid family"
    })

    print("\nLLM Embedding:")
    print(
        str(response.json()['embedding'][0:5])[:-1], '...', ']'
    )

if __name__ == '__main__':
    main()