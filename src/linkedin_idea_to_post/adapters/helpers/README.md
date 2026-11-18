# LinkedIn Idea to Post – Helpers

A common module to the adapters, providing helper pure functions.

## Main Components

### 1. [math_helpers.py](math.py)

Provides vector math utilities, such as [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) computed
via NumPy (`np.dot`, `np.linalg.norm`) with floating-point tolerance assertions (`np.isclose`).