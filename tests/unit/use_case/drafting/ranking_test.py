from uuid import UUID

import pytest

from linkedin_idea_to_post.use_case.drafting.ranking import (
    reciprocal_rank_fusion,
    rerank_by_word_count_proximity,
)

uuid1 = UUID(int=1)
uuid2 = UUID(int=2)
uuid3 = UUID(int=3)
uuid4 = UUID(int=4)


@pytest.mark.parametrize(
    "semantic_ranked_uuids,fts_ranked_uuids,semantic_weight,fts_weight,expected_ranked_uuids",
    [
        # fair weights prefer uuids present in both ranks
        ([uuid1, uuid2, uuid3], [uuid2, uuid4], 1.0, 1.0, [uuid2, uuid1, uuid4, uuid3]),
        ([uuid1, uuid2, uuid3], [uuid2, uuid4], 1.0, 0.7, [uuid2, uuid1, uuid3, uuid4]),
        # unfair weights prefer one rank over the other
        (
            [uuid1, uuid2, uuid3],
            [uuid4, uuid3, uuid2, uuid1],
            1.0,
            0.1,
            [uuid1, uuid2, uuid3, uuid4],
        ),
        (
            [uuid1, uuid2, uuid3],
            [uuid4, uuid3, uuid2, uuid1],
            0.01,
            1.0,
            [uuid4, uuid3, uuid2, uuid1],
        ),
    ],
)
def test_reciprocal_rank_fusion(
    semantic_ranked_uuids: list[UUID],
    fts_ranked_uuids: list[UUID],
    semantic_weight: int,
    fts_weight: int,
    expected_ranked_uuids: list[UUID],
):
    rrf_scored_uuids = reciprocal_rank_fusion(
        semantic_ranked_ids=semantic_ranked_uuids,
        fts_ranked_ids=fts_ranked_uuids,
        semantic_weight=semantic_weight,
        fts_weight=fts_weight,
    )
    rrf_uuids = [uuid for uuid, _ in rrf_scored_uuids]
    assert rrf_uuids == expected_ranked_uuids


# todo test


@pytest.mark.parametrize(
    "scored_ids,word_count_by_id,target_word_count,expected_scored_ids",
    [
        # same word count doesn't change ranking but can change scores
        (
            [(uuid1, 0.9), (uuid2, 0.5)],
            {uuid1: 10, uuid2: 10},
            10,
            [(uuid1, 0.9), (uuid2, 0.5)],
        ),
        (
            [(uuid1, 0.9), (uuid2, 0.5)],
            {uuid1: 5, uuid2: 5},
            10,
            [(uuid1, 0.6), (uuid2, 0.3333333333333333)],
        ),
        # different word count changes scores and can change ranking
        (
            [(uuid1, 0.9), (uuid2, 0.5)],
            {uuid1: 5, uuid2: 10},
            10,
            [(uuid1, 0.6), (uuid2, 0.5)],
        ),
        (
            [(uuid1, 0.9), (uuid2, 0.5)],
            {uuid1: 100, uuid2: 10},
            10,
            [(uuid2, 0.5), (uuid1, 0.09000000000000001)],
        ),
    ],
)
def test_rerank_by_word_count_proximity(
    scored_ids: list[tuple[UUID, float]],
    word_count_by_id: dict[UUID, int],
    target_word_count: int,
    expected_scored_ids: list[tuple[UUID, float]],
):
    reranked_scored_ids = rerank_by_word_count_proximity(
        scored_ids=scored_ids,
        word_count_by_id=word_count_by_id,
        target_word_count=target_word_count,
    )
    assert reranked_scored_ids == expected_scored_ids
