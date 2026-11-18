from typing import Protocol

from linkedin_idea_to_post.domain.post import Post, PostEmbedding


class EmbeddingGenerator(Protocol):
    def generate(self, post: Post) -> PostEmbedding:
        # np.ndarray is a continuous block of memory, typically float32 bytes; tolist() unpacks to list[float]
        ...
