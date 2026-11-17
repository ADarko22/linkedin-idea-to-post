import pytest

from linkedin_idea_to_post.adapters.embedding.math_helpers import cosine_similarity


@pytest.mark.integration
def test_embedding_semantic_sanity(embedding_generator, post_factory):
    post_java = post_factory(body="Concurrency with lightweight threads.")
    post_kotlin = post_factory(
        body="Asynchronous programming with structured concurrency."
    )
    post_baking = post_factory(body="Fermentation times and flour hydration ratios.")

    # Build embeddings
    post_java_embedding = embedding_generator.generate(post_java)
    post_kotlin_embedding = embedding_generator.generate(post_kotlin)
    post_baking_embedding = embedding_generator.generate(post_baking)

    # Compute cosine similarities: A * B / |A| * |B|
    post_java_kotlin_similarity = cosine_similarity(
        post_java_embedding, post_kotlin_embedding
    )
    post_java_baking_similarity = cosine_similarity(
        post_java_embedding, post_baking_embedding
    )
    post_kotlin_banking_similarity = cosine_similarity(
        post_kotlin_embedding, post_baking_embedding
    )

    # The tech posts should be significantly closer semantically than the baking post
    assert post_java_kotlin_similarity > post_java_baking_similarity
    assert post_java_kotlin_similarity > post_kotlin_banking_similarity

    assert post_java_kotlin_similarity > 0.5
    assert post_java_baking_similarity < 0.2
    assert post_kotlin_banking_similarity < 0.2
