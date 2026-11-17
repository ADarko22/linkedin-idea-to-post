from typing import Protocol

import numpy as np

from linkedin_idea_to_post.domain.post import Post


class EmbeddingGenerator(Protocol):
    def generate(self, post: Post) -> np.ndarray:
        # np.ndarray is a continuous block of memory, typically float32 bytes; tolist() unpacks to list[float]
        ...
