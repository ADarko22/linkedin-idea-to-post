import numpy as np
import pytest

from linkedin_idea_to_post.adapters.embedding.math_helpers import cosine_similarity


@pytest.mark.parametrize(
    ("vector_a", "vector_b", "expected_similarity"),
    [
        # Identical vectors (Angle = 0°, Cosine = 1.0)
        (np.array([1.0, 0.0]), np.array([1.0, 0.0]), 1.0),
        # Orthogonal vectors (Angle = 90°, Cosine = 0.0)
        (np.array([1.0, 0.0]), np.array([0.0, 1.0]), 0.0),
        # Exactly opposite vectors (Angle = 180°, Cosine = -1.0)
        (np.array([1.0, 2.0]), np.array([-1.0, -2.0]), -1.0),
        # 45-degree angle vectors (Cosine = 1 / sqrt(2) ≈ 0.7071068)
        (np.array([1.0, 0.0]), np.array([1.0, 1.0]), 1.0 / np.sqrt(2.0)),
        # Higher-dimensional vectors (e.g., 3-dimensional)
        (np.array([1.0, 2.0, 3.0]), np.array([4.0, 5.0, 6.0]), 0.9746318),
    ],
)
def test_cosine_similarity(
    vector_a: np.ndarray, vector_b: np.ndarray, expected_similarity: float
) -> None:
    result = cosine_similarity(vector_a, vector_b)
    # np.isclose safely handles floating-point arithmetic tolerances
    assert np.isclose(result, expected_similarity, atol=1e-6)
