from sqlite3 import IntegrityError

import pytest


def test_save_post_embedding_violates_fk(
    sample_embedding, in_memory_embedding_storage
) -> None:
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding is None

    with pytest.raises(IntegrityError):
        in_memory_embedding_storage.save(sample_embedding)


def test_save_and_get_post_embedding(
    sample_post, in_memory_storage, sample_embedding, in_memory_embedding_storage
) -> None:
    # post must exist to satisfy the FK Constraint
    in_memory_storage.save(sample_post)

    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding is None

    in_memory_embedding_storage.save(sample_embedding)
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding == sample_embedding


def test_delete_post_embedding(
    sample_post, in_memory_storage, sample_embedding, in_memory_embedding_storage
) -> None:
    # post must exist to satisfy the FK Constraint
    in_memory_storage.save(sample_post)

    in_memory_embedding_storage.save(sample_embedding)
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding == sample_embedding

    in_memory_embedding_storage.delete(sample_embedding.post_id)
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding is None


def test_post_delete_cascades_on_post_embedding(
    sample_post, in_memory_storage, sample_embedding, in_memory_embedding_storage
) -> None:
    # post must exist to satisfy the FK Constraint
    in_memory_storage.save(sample_post)

    in_memory_embedding_storage.save(sample_embedding)
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding == sample_embedding

    in_memory_storage.delete(sample_post.id)
    post_embedding = in_memory_embedding_storage.get(sample_embedding.post_id)
    assert post_embedding is None
