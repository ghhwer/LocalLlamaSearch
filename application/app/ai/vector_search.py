import polars as pl

def cosine_similarity(v1, v2):
    "Cossine similarity between two vectors"
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude = (sum(a ** 2 for a in v1) * sum(b ** 2 for b in v2)) ** 0.5
    return dot_product / magnitude

def change_orientation_dict(dict_data):
    result = []
    for i in range(len(list(dict_data.values())[0])):
        result.append({key: dict_data[key][i] for key in dict_data.keys()})
    return result

def query_vector_emb(query_embedding, delta_location, top_k=2, n_neighboors=1):
    df_emb = pl.scan_delta(delta_location)
    df_q = (
        df_emb
            .with_columns(pl.lit(query_embedding).alias("query_embedding"))
            .with_columns(
                pl.struct(["query_embedding", "vector"])
                .map_elements(
                    lambda cols: cosine_similarity(cols["query_embedding"], cols["vector"]),
                    return_dtype=float
                )
                .alias("similarity")
            )
    )

    df_q_results = (
        df_q.sort("similarity", descending=True).select(
            pl.col("uri"),
            pl.col("chunk_id").alias("similar_chunk_id"),
            pl.col("similarity").alias("similarity"),
        )
        .limit(top_k)
    )
    
    df_q_results = (
        df_q_results
        .join(
            df_emb,
            on="uri"
        ).filter(
            (pl.col("chunk_id") == pl.col("similar_chunk_id")) |
            (pl.col("chunk_id") >= pl.col("similar_chunk_id") - n_neighboors) &
            (pl.col("chunk_id") <= pl.col("similar_chunk_id") + n_neighboors)
        ).select(
            pl.col("uri"),
            pl.col("text"),
            pl.col("similar_chunk_id").alias("center_chunk_id"),
            pl.col("chunk_id"),
            pl.col("vector"),
            pl.col("similarity")
        )
    )

    # Retain the original scores, this can be used later for the UI
    df_q_scores = df_q_results.select(
        pl.col("uri"),
        pl.col("center_chunk_id"),
        pl.col("chunk_id"),
        pl.col("text"),
        pl.col("similarity")
    )

    # Now group by the uri and get the text on the correct order
    df_q_context = df_q_results.select(
        pl.col("uri"),
        pl.col("chunk_id"),
        pl.col("text")
    ).unique().sort(["uri", "chunk_id"], descending=False)
    df_q_context = df_q_context.group_by(["uri"], maintain_order=True).agg(
        pl.col("text").str.concat("")
    )
    
    # Convert to dictionary    
    dict_context = df_q_context.collect().to_dict(as_series=False)
    dict_detail = df_q_scores.collect().to_dict(as_series=False)
    
    return change_orientation_dict(dict_context), change_orientation_dict(dict_detail)