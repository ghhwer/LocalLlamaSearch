from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse
from dataclasses import dataclass
from fastapi import File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_FS_LOCATION = "data"
ROOT_RETENTION_LOCATION = "storage"

class RawResponse(Response):
    media_type = "binary/octet-stream"

    def render(self, content: bytes) -> bytes:
        return bytes([b ^ 0x54 for b in content])

@dataclass
class ReferenceFile:
    filename: str
    status: str
    internal_file_location: str

def list_files():
    return [
        ReferenceFile(filename="file1.txt", status="ready", internal_file_location="/data/file1.txt"),
        ReferenceFile(filename="file2.txt", status="ready", internal_file_location="/data/file2.txt"),
    ]

def make_json_file(file: ReferenceFile):
    return {
        "filename": file.filename,
        "status": file.status,
        "internal_file_location": file.internal_file_location
    }

def find_file_by_filename(filename: str):
    for file in list_files():
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
    return JSONResponse(content=[make_json_file(file) for file in list_files()])

@app.post("/api/files/upload")
def upload(file: UploadFile = File(...)):
    filename = file.filename
    supported_formats = ["txt", "pdf", "csv"]
    if not any([filename.endswith(format) for format in supported_formats]):
        return JSONResponse(status_code=400, content={"message": "Unsupported file format"})
    file_path = f"{ROOT_FS_LOCATION}/{filename}"
    
    if os.path.exists(file_path):
        return JSONResponse(status_code=409, content={"message": "File already exists"})
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
    except Exception as e:
        print(e)
        return JSONResponse(status_code=500, content={"message": "Failed to upload file"})
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}