from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from linkedin_idea_to_post.config import EmbeddingSettings
from linkedin_idea_to_post.domain.embedding import EmbeddingGenerator
from linkedin_idea_to_post.domain.post import Post


def _retrieve_embedding_model(embedding_settings: EmbeddingSettings) -> str | Path:
    local_model_path = embedding_settings.local_model_path

    # Check if local path already exists and has files
    if local_model_path.exists() and any(local_model_path.iterdir()):
        return local_model_path

    # If not found locally, download using the model name string
    print(
        f"Model not found at {local_model_path}. Downloading {embedding_settings.model_name}..."
    )
    temp_model = SentenceTransformer(embedding_settings.model_name)

    # Save weights locally for future offline runs
    local_model_path.mkdir(parents=True, exist_ok=True)
    temp_model.save(str(local_model_path))

    return embedding_settings.model_name


class PyTorchEmbeddingGenerator(EmbeddingGenerator):
    def __init__(self, embedding_settings: EmbeddingSettings) -> None:
        embedding_model = _retrieve_embedding_model(embedding_settings)
        self.sentence_transformer = SentenceTransformer(
            model_name_or_path=embedding_model,
            device=embedding_settings.device,
        )

    def generate(self, post: Post) -> np.ndarray:
        # embedding only post body (title and topics are metadata extracted from the body)
        return self.sentence_transformer.encode(post.body, convert_to_numpy=True)
