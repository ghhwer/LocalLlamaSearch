from dataclasses import dataclass
from threading import Thread
from glob import glob
import polars as pl
import logging
import time
import json
import os

import variables

@dataclass
class ReferenceFile:
    filename: str
    status: str
    internal_file_location: str

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
    print(files_on_disk)
    print(files_in_vector_store)
    files_total = files_on_disk + files_in_vector_store
    files_return = []
    for f in files_total:
        filename = f.split("/")[-1]
        if f in files_on_disk and f in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "indexed", f))
        elif f in files_on_disk and f not in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "processing", f))
        elif f not in files_on_disk and f in files_in_vector_store:
            files_return.append(ReferenceFile(filename, "deleting", f))
    return files_return

class MetadataSync():
    def __init__(self):
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        while True:
            time.sleep(5)
            files = fetch_files()

            logging.info(f"Files: {files}")