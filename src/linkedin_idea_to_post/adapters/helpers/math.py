import numpy as np
import numpy.typing as npt


def cosine_similarity(
    a: npt.NDArray[np.floating], b: npt.NDArray[np.floating]
) -> float:
    """Computes cosine similarity between two 1D vectors.
    Returns a score bounded in [-1.0, 1.0].
    """
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def matrix_vector_cosine_similarity(
    matrix: npt.NDArray[np.floating], query_vector: npt.NDArray[np.floating]
) -> npt.NDArray[np.floating]:
    """Computes cosine similarity between a 2D matrix [N, D] and a 1D query vector [D].
    Returns an array of scores of shape [N] bounded in [-1.0, 1.0].
    """
    if matrix.size == 0 or query_vector.size == 0:
        return np.array([], dtype=np.float32)

    query_norm = np.linalg.norm(query_vector)
    if np.isclose(query_norm, 0.0, atol=1e-12):
        return np.zeros(matrix.shape[0], dtype=np.float32)

    row_norms = np.linalg.norm(matrix, axis=1)
    valid_mask = row_norms > 0.0

    scores = np.zeros(matrix.shape[0], dtype=np.float32)
    scores[valid_mask] = (matrix[valid_mask] @ query_vector) / (
        row_norms[valid_mask] * query_norm
    )
    return scores


def top_k_indices(scores: npt.NDArray[np.floating], k: int) -> npt.NDArray[np.integer]:
    """Returns the indices of the top K highest scores in descending order."""
    if k <= 0 or len(scores) == 0:
        return np.array([], dtype=int)

    effective_k = min(k, len(scores))
    # argsort sorts ascending, [::-1] reverses to descending, [:effective_k] slices top K
    return np.argsort(scores)[::-1][:effective_k]
