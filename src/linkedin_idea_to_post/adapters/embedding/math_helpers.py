import numpy as np
import numpy.typing as npt


def cosine_similarity(
    a: npt.NDArray[np.floating], b: npt.NDArray[np.floating]
) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
