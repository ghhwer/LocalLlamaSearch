import requests

# Pull llama 3 onto the GPU Server and PULL 
GPU_SERVER_URL = 'http://localhost:11434'
CPU_SERVER_URL = 'http://localhost:11435'

def main():
   print("Pulling models onto the servers")
   requests.post(f'{GPU_SERVER_URL}/api/pull', json={
      "name": "llama3"
   })
   requests.post(f'{CPU_SERVER_URL}/api/pull', json={
      "name": "jina/jina-embeddings-v2-small-en"
   })
   print("Models pulled successfully")

if __name__ == '__main__':
   main()