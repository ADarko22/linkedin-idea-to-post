import pytest

from linkedin_idea_to_post.use_case.post_management.post_write_management_service import (
    PostWriteManagementService,
)


def test_save_post_rolls_back_when_embedding_save_fails(
    sample_post,
    mock_embedding_generator,
    unit_of_work,
    in_memory_storage,
    in_memory_embedding_storage,
    failing_embedding_storage,
) -> None:
    # When an error occurs while saving post and its generated post embedding
    service = PostWriteManagementService(
        embedding_generator=mock_embedding_generator,
        unit_of_work=unit_of_work,
        post_storage=in_memory_storage,
        embedding_storage=failing_embedding_storage,
    )
    with pytest.raises(RuntimeError):
        service.save_post(sample_post)

    # Then no partial state is left: neither post nor the post embedding are saved. Atomic rollback
    assert in_memory_storage.get(sample_post.id) is None
    assert in_memory_embedding_storage.get(sample_post.id) is None


def test_save_post_successfully_saves_both_post_and_embedding(
    sample_post,
    mock_embedding_generator,
    unit_of_work,
    in_memory_storage,
    in_memory_embedding_storage,
) -> None:
    sample_embedding = mock_embedding_generator.generate(sample_post)
    # when successfully saving post and its generated post embedding
    service = PostWriteManagementService(
        embedding_generator=mock_embedding_generator,
        unit_of_work=unit_of_work,
        post_storage=in_memory_storage,
        embedding_storage=in_memory_embedding_storage,
    )

    service.save_post(sample_post)

    # Both post and post embedding are saved: Atomic commit
    assert in_memory_storage.get(sample_post.id) == sample_post
    assert in_memory_embedding_storage.get(sample_post.id) == sample_embedding


def test_delete_post_rolls_back_when_embedding_delete_fails(
    sample_post,
    mock_embedding_generator,
    unit_of_work,
    in_memory_storage,
    in_memory_embedding_storage,
    failing_embedding_storage,
) -> None:
    # Given a post and its post embeddings stored
    sample_embedding = mock_embedding_generator.generate(sample_post)
    with unit_of_work:
        in_memory_storage.save(sample_post)
        in_memory_embedding_storage.save(sample_embedding)

    assert in_memory_storage.get(sample_post.id) == sample_post
    assert in_memory_embedding_storage.get(sample_post.id) == sample_embedding

    # when an error occurs while deleting the post via the PostWriteManagementService
    service = PostWriteManagementService(
        embedding_generator=mock_embedding_generator,
        unit_of_work=unit_of_work,
        post_storage=in_memory_storage,
        embedding_storage=failing_embedding_storage,
    )
    with pytest.raises(RuntimeError):
        service.delete_post(sample_post.id)

    # Then no partial state is left: neither post nor the post embedding are deleted. Atomic rollback
    assert in_memory_storage.get(sample_post.id) == sample_post
    assert in_memory_embedding_storage.get(sample_post.id) == sample_embedding


def test_delete_post_successfully_deletes_both_post_and_embedding(
    sample_post,
    mock_embedding_generator,
    unit_of_work,
    in_memory_storage,
    in_memory_embedding_storage,
) -> None:
    # Given a post and its post embeddings stored
    sample_embedding = mock_embedding_generator.generate(sample_post)
    with unit_of_work:
        in_memory_storage.save(sample_post)
        in_memory_embedding_storage.save(sample_embedding)

    assert in_memory_storage.get(sample_post.id) == sample_post
    assert in_memory_embedding_storage.get(sample_post.id) == sample_embedding

    # when deleting the post successfully
    service = PostWriteManagementService(
        embedding_generator=mock_embedding_generator,
        unit_of_work=unit_of_work,
        post_storage=in_memory_storage,
        embedding_storage=in_memory_embedding_storage,
    )
    service.delete_post(sample_post.id)

    # Then both post and post embedding are deleted. Atomic commit
    assert in_memory_storage.get(sample_post.id) is None
    assert in_memory_embedding_storage.get(sample_post.id) is None
