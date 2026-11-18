import numpy as np
import pytest

from linkedin_idea_to_post.adapters.helpers.math import (
    cosine_similarity,
    matrix_vector_cosine_similarity,
    top_k_indices,
)


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


def test_matrix_vector_cosine_similarity_perfect_match():
    matrix = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32)
    query = np.array([1.0, 0.0], dtype=np.float32)

    scores = matrix_vector_cosine_similarity(matrix, query)

    # First row is identical -> 1.0, second is orthogonal -> 0.0, third is 45 deg -> ~0.707
    assert scores[0] == 1.0
    assert scores[1] == 0.0
    assert np.isclose(scores[2], 0.7071067, atol=1e-6)


def test_matrix_vector_cosine_similarity_zero_norm():
    matrix = np.array([[0.0, 0.0]], dtype=np.float32)
    query = np.array([1.0, 1.0], dtype=np.float32)

    scores = matrix_vector_cosine_similarity(matrix, query)
    assert scores[0] == 0.0


def test_top_k_indices_returns_sorted_descending():
    scores = np.array([0.1, 0.9, 0.5, 0.8], dtype=np.float32)

    indices = top_k_indices(scores, k=2)

    # Highest score is 0.9 (index 1), second highest is 0.8 (index 3)
    np.testing.assert_array_equal(indices, [1, 3])


def test_top_k_indices_with_k_larger_than_scores():
    scores = np.array([0.4, 0.2], dtype=np.float32)
    indices = top_k_indices(scores, k=5)
    np.testing.assert_array_equal(indices, [0, 1])
