# LinkedIn Idea to Post – Embedding

## Main Components

### 1. [embedding_generator.py](embedding_generator.py)

The `PyTorchEmbeddingGenerator` implements `EmbeddingGenerator` using
the [sentence-transformers](https://github.com/UKPLab/sentence-transformers) framework backed by PyTorch.

#### Fixed-Size Vector Embedding

Uses the [SentenceTransformer](https://sbert.net/docs/quickstart.html#sentence-transformer) `.encode()` function, which
tokenizes the `Post` textual representation, passes the token IDs through the transformer model's attention layers, and
applies pooling to collapse variable-length text into a single fixed-size dense vector.

##### Embedding Models

- **Default:** Configured in [config.py](../../config.py)
  using [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5), which produces **1024-dimensional**
  vectors.
- **Testing:** Configured in [conftest.py](../../../../tests/conftest.py)
  using [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), which
  produces **384-dimensional** vectors for fast, lightweight testing.

_In order to generate embeddings for larger posts or using smaller models, chunking the input text and collecting
multiple embeddings can be done by adding the **[chonkie](https://github.com/feyninc/chonkie) library** (to explore in
case of scaling need)._
