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

- ** Default:** Configured in [config.py](../../config.py)
  using [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5), which produces **1024-dimensional**
  vectors.
- **Testing:** Configured in [conftest.py](../../../../tests/conftest.py)
  using [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), which
  produces **384-dimensional** vectors for fast, lightweight testing.

### 2. [math_helpers.py](math_helpers.py)

Provides vector math utilities, such as [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) computed
via NumPy (`np.dot`, `np.linalg.norm`) with floating-point tolerance assertions (`np.isclose`).