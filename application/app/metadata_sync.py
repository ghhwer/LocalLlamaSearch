from dataclasses import dataclass
from file_parsing.pdf import ingest_pdf_data
from glob import glob
import polars as pl
import logging
import time
import json
from ai.ai_functions import build_vectors_for_text
from hashlib import sha256

import variables

@dataclass
class ReferenceFile:
    filename: str
    status: str
    internal_file_location: str

    def as_dict(self):
        return {
            "filename": self.filename,
            "status": self.status,
            "internal_file_location": self.internal_file_location
        }

def fetch_delta_table():
    # Fetch Delta Table
    df = pl.read_delta(variables.VECTOR_STORE_LOCATION)
    return df

def check_delta():
    df = pl.scan_delta(variables.VECTOR_STORE_LOCATION)
    if dict(df.schema) == {'uri': pl.String, 'text': pl.String, 'vector': pl.List(pl.Float64), 'chunk_id': pl.Int64}:
        logging.info("Schema is correct")
    else:
        raise ValueError("Schema is incorrect")
    return df

def create_empty_table():
    # Create empty Delta Table with schema
    # schema = uri: str, text: str, vector: list[float], chunk_id: int
    df = pl.DataFrame( {
        "uri": ['string'],
        "text": ['string'],
        "vector": [[1.2,2.3]],
        "chunk_id": [-1]
    })
    ctx = pl.SQLContext(my_table=df, eager=True)
    result = ctx.execute("""
        CREATE TABLE delta_table AS SELECT * FROM my_table WHERE chunk_id > 0
    """)
    result = ctx.execute("SELECT * FROM delta_table")
    result.write_delta(variables.VECTOR_STORE_LOCATION)

def fetch_files():
    # Fetch all files in vector store
    files_on_disk = glob(f"{variables.ROOT_FS_LOCATION}/*")
    # Fetch files in vector store
    df = fetch_delta_table()
    files_in_vector_store = df.select('uri').unique().to_dict(as_series=False)['uri']
    files_total = set(files_on_disk + files_in_vector_store)
    files_return = []
    for f in files_total:
        filename = f.split("/")[-1].split("\\")[-1]
        if f in files_on_disk and f in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "indexed", f))
        elif f in files_on_disk and f not in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "processing", f))
        elif f not in files_on_disk and f in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "deleting", f))
    return files_return

def get_text_content(file_path: str):
    if file_path.endswith(".txt"):
        with open(file_path, 'r') as f:
            return f.read()
    elif file_path.endswith(".pdf"):
        return ingest_pdf_data(file_path)

def sync_tick(latest_checksum: str):
    logging.info("Syncing files")
    files = fetch_files()
    files_json = [file.as_dict() for file in files]
    files_checksum = sha256(json.dumps(files_json, sort_keys=True).encode()).hexdigest()
    if files_checksum != latest_checksum:
        # The files have changed we need to update the delta table
        to_sync = [file for file in files if file.status == "processing"]
        to_delete = [file for file in files if file.status == "deleting"]
        for file in to_sync:
            text = get_text_content(file.internal_file_location)
            vector_data = build_vectors_for_text(text, file.internal_file_location)
            df = pl.DataFrame(vector_data)
            df.write_delta(variables.VECTOR_STORE_LOCATION, mode="append")
        for file in to_delete:
            df = fetch_delta_table()
            df = df.filter(pl.col("uri") != file.internal_file_location)
            df.write_delta(variables.VECTOR_STORE_LOCATION, mode="overwrite")
    else:
        pass
    time.sleep(int(variables.SYNC_INTERVAL_SECONDS))  # Sleep for a while