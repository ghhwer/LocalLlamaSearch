# External imports
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from dataclasses import dataclass
from fastapi import File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha256
import uvicorn
import logging
import json
import os
# Application specific imports
import metadata_sync
import variables
import threading
import time

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])


def make_json_file(file: metadata_sync.ReferenceFile):
    return {
        "filename": file.filename,
        "status": file.status,
        "internal_file_location": file.internal_file_location
    }

def find_file_by_filename(filename: str):
    for file in metadata_sync.fetch_files():
        if file.filename == filename:
            return file
    return None

@app.get("/")
def read_root():
    return "Application is running!"

@app.get("/api/files/{filename}")
def download_file(filename: str):
    file = find_file_by_filename(filename)
    if file is None:
        return JSONResponse(status_code=404, content={"message": "File not found"})
    file_binary = open(file.internal_file_location, "rb").read()
    return RawResponse(content=file_binary)

@app.get("/api/files/")
def get_files():
    return JSONResponse(content=[make_json_file(file) for file in metadata_sync.fetch_files()])

@app.post("/api/files/upload")
def upload(file: UploadFile = File(...)):
    filename = file.filename
    supported_formats = ["txt", "pdf", "csv"]
    if not any([filename.endswith(format) for format in supported_formats]):
        return JSONResponse(status_code=400, content={"message": "Unsupported file format"})
    file_path = f"{variables.ROOT_FS_LOCATION}/{filename}"
    
    if os.path.exists(file_path):
        return JSONResponse(status_code=409, content={"message": "File already exists"})
    try:
        with open(file_path, 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Failed to upload file"})
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

class ApplicationServer:
    def __init__(self, app):
        self.server_exit = False
        self.app = app
        self.files_checksum = ""

    def sync_thread(self):
        while not self.server_exit:
            logging.info("Syncing files")
            files = metadata_sync.fetch_files()
            files_json = [make_json_file(file) for file in files]
            files_checksum = sha256(json.dumps(files_json, sort_keys=True).encode()).hexdigest()
            if files_checksum != self.files_checksum:
                # The files have changed we need to update the delta table
                to_sync = [file for file in files if file.status == "processing"]
                to_delete = [file for file in files if file.status == "deleting"]
                # We need to now sync the files
                # TODO: Implement the syncing logic in such a way to use the least amount of version changes possible
            else:
                pass
            time.sleep(variables.SYNC_INTERVAL)  # Sleep for a while

    def run(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        # Add some color to the logging:
        #    [INFO] IS BLUE
        #    [ERROR] IS RED
        #    [WARNING] IS YELLOW
        logging.addLevelName(logging.INFO, "\033[1;34m%s\033[1;0m" % logging.getLevelName(logging.INFO))
        logging.addLevelName(logging.ERROR, "\033[1;31m%s\033[1;0m" % logging.getLevelName(logging.ERROR))
        logging.addLevelName(logging.WARNING, "\033[1;33m%s\033[1;0m" % logging.getLevelName(logging.WARNING))
        # Check if folders exist
        if not os.path.exists(variables.ROOT_FS_LOCATION):
            os.makedirs(variables.ROOT_FS_LOCATION)
        if not os.path.exists(variables.ROOT_RETENTION_LOCATION):
            os.makedirs(variables.ROOT_RETENTION_LOCATION)

        # Check if delta table exists
        if not os.path.exists(variables.VECTOR_STORE_LOCATION):
            os.makedirs(variables.VECTOR_STORE_LOCATION)
            metadata_sync.create_empty_table()
        else:
            df = metadata_sync.check_delta()

        # Start the parallel process
        t = threading.Thread(target=self.sync_thread)
        t.start()

        try:
            host = os.getenv("HOST", "0.0.0.0")
            port = os.getenv("PORT", 8080)
            uvicorn.run(self.app, host=host, port=port)
        except KeyboardInterrupt:
            pass
        finally:
            self.server_exit = True
            # Terminate the parallel process when the main server is shutting down
            t.join()

if __name__ == "__main__":
    server = ApplicationServer(app)
    server.run()