from collections import defaultdict
from uuid import UUID


def reciprocal_rank_fusion(
    semantic_ranked_ids: list[UUID],
    fts_ranked_ids: list[UUID],
    k: int = 60,
    semantic_weight: float = 1.0,
    fts_weight: float = 0.7,
) -> list[tuple[UUID, float]]:
    """
    Re-ranks by accounting for both semantic rank and fts rank.
    The semantic_weight and fts_weight are used to boost a preference, by default towards higher ranked semantic.

    For example:
        Given the default settings and the following posts:
        - semantic_ranked_ids = [post1, post2, post3]
        - fts_ranked_ids = [post2, post4]

        The computed reciprocal rank fusion is:
        rrf(post1) = 1 / 61 = 0.016
        rrf(post2) = 1 / 62 + 0.7 / 61 = 0.0276
        rrf(post3) = 1 / 63 = 0.0158
        rrf(post4) = 0.7 / 62 = 0.112

        The final ranking is: [post2, post1, post3, post4]
        post2 is the highest ranked because it appears in both semantic and fts.
        post3 is higher than post4 because semantic_weight is higher than fts_weight.
    """
    rrf: dict[UUID, float] = defaultdict(float)

    for rank, post_id in enumerate(semantic_ranked_ids, start=1):
        rrf[post_id] += semantic_weight / (k + rank)

    for rank, post_id in enumerate(fts_ranked_ids, start=1):
        rrf[post_id] += fts_weight / (k + rank)

    # sort descending by rrf
    return sorted(
        rrf.items(),
        key=lambda pair: pair[1],
        reverse=True,
    )


def rerank_by_word_count_proximity(
    scored_ids: list[tuple[UUID, float]],
    word_count_by_id: dict[UUID, int],
    target_word_count: int,
) -> list[tuple[UUID, float]]:
    """
    Re-ranks by word-count proximity: ids that closer to the target word count improve their score.
    """
    rescored_ids = [
        (id, score * _length_factor(word_count_by_id[id], target_word_count))
        for id, score in scored_ids
    ]
    return sorted(rescored_ids, key=lambda pair: pair[1], reverse=True)


def _length_factor(word_count: int, target_word_count: int) -> float:
    denominator = 1 + abs(word_count - target_word_count) / target_word_count
    return 1 / denominator
