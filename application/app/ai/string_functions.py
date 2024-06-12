import re

def approx_num_tokens_from_string(string: str) -> int:
    return len(string.split(" "))

def approx_sentense_split(text, chunk_target_size=1000, overlap=20, min_chunk_size=200, paragraph_sep='\n\n', chunking_regex='[^,\.;]+[,\.;]?', word_sep=' ') -> list[str]:
    # Step 1: Split by paragraph separator
    paragraphs = text.split(paragraph_sep)
    chunks = []
    
    for paragraph in paragraphs:
        # Step 2: Split by the second chunking regex
        matches = re.findall(chunking_regex, paragraph)
        
        # Group the matches into chunks
        current_chunk = []
        current_chunk_size = 0
        
        for match in matches:
            num_tokens = approx_num_tokens_from_string(match)
            if current_chunk_size + num_tokens <= chunk_target_size:
                current_chunk.append(match)
                current_chunk_size += num_tokens
            else:
                # Finalize the current chunk if it exceeds the target size
                if current_chunk:
                    chunks.append(word_sep.join(current_chunk))
                
                # Start a new chunk with overlap from the end of the previous chunk
                overlap_chunks = current_chunk[-overlap:] if len(current_chunk) >= overlap else current_chunk
                current_chunk = overlap_chunks + [match]
                current_chunk_size = sum(approx_num_tokens_from_string(c) for c in current_chunk)
        
        # Add the last chunk of the paragraph if not empty
        if current_chunk:
            chunks.append(word_sep.join(current_chunk))
    
    # Ensure no chunks are too small
    merged_chunks = []
    buffer_chunk = ''
    
    for chunk in chunks:
        if approx_num_tokens_from_string(chunk) < min_chunk_size:
            if buffer_chunk:
                buffer_chunk += word_sep + chunk
            else:
                buffer_chunk = chunk
            
            if approx_num_tokens_from_string(buffer_chunk) >= min_chunk_size:
                merged_chunks.append(buffer_chunk)
                buffer_chunk = ''
        else:
            if buffer_chunk:
                merged_chunks.append(buffer_chunk)
                buffer_chunk = ''
            merged_chunks.append(chunk)
    
    if buffer_chunk:
        if merged_chunks:
            merged_chunks[-1] += word_sep + buffer_chunk
        else:
            merged_chunks.append(buffer_chunk)
    
    return merged_chunks

def sentense_split_raw_text(text, chunk_target_size=1000, overlap=20, min_chunk_size=200, paragraph_sep='\n\n', chunking_regex='[^,\.;]+[,\.;]?', word_sep=' ') -> list[str]:
    # Clean the text a bit
    text = re.sub(r" +", " ", text) 
    text = re.sub(r"\n\n+", paragraph_sep, text)
    # Split the text into chunks
    return approx_sentense_split(text, chunk_target_size, overlap, min_chunk_size, paragraph_sep, chunking_regex, word_sep)