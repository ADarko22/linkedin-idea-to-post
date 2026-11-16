import pytest

from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.retrieval import PostSearchQuery


@pytest.fixture
def seeded_posts(post_factory, in_memory_storage) -> tuple[Post, Post]:
    post1 = post_factory(
        title="Quality of Life is important.",
        body="Having a good life, healthy food and active days is more important than a high paid 9 to 6 job.",
        topics={"quality_of_life", "healthy_food", "active_days", "job"},
    )
    post2 = post_factory(
        title="Job satisfaction is important.",
        body="Having a good job that makes you happy is more important than a high paid 9 to 6 job.",
        topics={"satisfaction", "job"},
    )
    in_memory_storage.save(post1)
    in_memory_storage.save(post2)
    return post1, post2


# --- Retrieval & Ranking Behavior ---


@pytest.mark.parametrize(
    ("query_text", "expected_first_index"),
    [
        ("I'm living an happy life.", 0),
        ("Living an happy job for self-growth.", 1),
    ],
)
def test_full_text_search_ranks_most_relevant_post_first(
    seeded_posts, in_memory_retriever, query_text: str, expected_first_index: int
) -> None:
    query = PostSearchQuery(text=query_text, limit=2)
    relevant_posts = in_memory_retriever.full_text_search(query)

    assert len(relevant_posts) == 2
    assert relevant_posts[0] == seeded_posts[expected_first_index]


def test_full_text_search_retrieves_nothing_when_no_terms_match(
    seeded_posts, in_memory_retriever
) -> None:
    query = PostSearchQuery(text="Idea matching no words..", limit=2)
    assert in_memory_retriever.full_text_search(query) == []


# --- Trigger & Index Synchronization Tests ---


def test_insert_trigger_indexes_topics_via_json_each(
    post_factory, in_memory_storage, in_memory_retriever
) -> None:
    """Verifies AFTER INSERT trigger extracts and indexes JSON array elements in $.topics."""
    post = post_factory(
        title="Deployment Lessons",
        body="Measure p99 latency before scaling nodes.",
        topics={"observability", "kubernetes"},
    )
    in_memory_storage.save(post)

    results = in_memory_retriever.full_text_search(
        PostSearchQuery(text="observability")
    )
    assert results == [post]


def test_update_trigger_purges_old_terms_and_indexes_new_terms(
    post_factory, in_memory_storage, in_memory_retriever
) -> None:
    """Verifies AFTER UPDATE trigger executes FTS5 'delete' for OLD values and inserts NEW values."""
    post = post_factory(
        title="Monolith Architecture",
        body="Running a single Java JAR on bare metal.",
        topics={"java", "monolith"},
    )
    in_memory_storage.save(post)
    assert in_memory_retriever.full_text_search(PostSearchQuery(text="Monolith")) == [
        post
    ]

    updated_post = post.model_copy(
        update={
            "title": "Event Streaming",
            "body": "Building pipelines with Apache Kafka.",
            "topics": {"kafka", "streaming"},
        }
    )
    in_memory_storage.save(updated_post)

    # Stale terms must be purged from the inverted index
    assert in_memory_retriever.full_text_search(PostSearchQuery(text="Monolith")) == []
    assert in_memory_retriever.full_text_search(PostSearchQuery(text="Java")) == []

    # New terms must be searchable
    assert in_memory_retriever.full_text_search(
        PostSearchQuery(text="Apache Kafka")
    ) == [updated_post]


def test_delete_trigger_removes_document_from_index(
    post_factory, in_memory_storage, in_memory_retriever
) -> None:
    """Verifies AFTER DELETE trigger removes the row from posts_fts."""
    post = post_factory(
        title="Terraform Modules",
        body="Managing cloud state safely.",
        topics={"terraform"},
    )
    in_memory_storage.save(post)
    assert in_memory_retriever.full_text_search(PostSearchQuery(text="Terraform")) == [
        post
    ]

    in_memory_storage.delete(post.id)

    assert in_memory_retriever.full_text_search(PostSearchQuery(text="Terraform")) == []
