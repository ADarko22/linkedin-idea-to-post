from uuid import UUID

from linkedin_idea_to_post.config import DraftingSettings
from linkedin_idea_to_post.domain.drafting import (
    DraftContext,
    KnowledgeSelection,
    VoiceSelection,
)
from linkedin_idea_to_post.domain.embedding import EmbeddingGenerator, TextEmbedding
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus, ScoredPost
from linkedin_idea_to_post.domain.retrieval import (
    FullTextPostSearchQuery,
    PostRetriever,
    VectorPostSearchQuery,
)
from linkedin_idea_to_post.use_case.drafting.ranking import (
    reciprocal_rank_fusion,
    rerank_by_word_count_proximity,
)


class DraftContextService:
    def __init__(
        self,
        settings: DraftingSettings,
        embedding_generator: EmbeddingGenerator,
        retriever: PostRetriever,
    ) -> None:
        self._settings = settings
        self._embedding_generator = embedding_generator
        self._retriever = retriever

    def create_context(self, idea: str, target_word_count: int = 300) -> DraftContext:
        idea_embedding = self._embedding_generator.embed_text(idea)

        voice_candidates = self._find_voice_candidates(
            idea, idea_embedding, target_word_count
        )
        knowledge_candidates = self._find_knowledge_candidates(idea, idea_embedding)

        all_scored_posts = voice_candidates + knowledge_candidates

        return DraftContext(
            relevant_posts={
                scored_post.post.id: scored_post.post
                for scored_post in all_scored_posts
            },
            voice_selections=[
                VoiceSelection(post_id=c.post.id) for c in voice_candidates
            ],
            knowledge_selections=[
                KnowledgeSelection(post_id=c.post.id) for c in knowledge_candidates
            ],
            target_word_count=target_word_count,
        )

    def _hybrid_search(
        self,
        idea: str,
        idea_embedding: TextEmbedding,
        limit: int,
        statuses: list[PostStatus],
        origins: list[PostOrigin],
    ) -> tuple[list[tuple[UUID, float]], dict[UUID, Post]]:
        fts_posts = self._retriever.full_text_search(
            FullTextPostSearchQuery(
                search_text=idea, statuses=statuses, origins=origins, limit=limit
            )
        )
        semantic_posts = self._retriever.semantic_search(
            VectorPostSearchQuery(
                search_text_embedding=idea_embedding,
                statuses=statuses,
                origins=origins,
                limit=limit,
            )
        )

        fused = reciprocal_rank_fusion(
            semantic_ranked_ids=[sp.post.id for sp in semantic_posts],
            fts_ranked_ids=[sp.post.id for sp in fts_posts],
        )

        post_by_id: dict[UUID, Post] = {
            sp.post.id: sp.post for sp in (*fts_posts, *semantic_posts)
        }
        return fused, post_by_id

    def _find_knowledge_candidates(
        self, idea: str, idea_embedding: TextEmbedding
    ) -> list[ScoredPost]:
        limit = self._settings.knowledge_examples_count
        fused, post_by_id = self._hybrid_search(
            idea,
            idea_embedding,
            limit=limit * 2,
            statuses=[PostStatus.PUBLISHED],
            origins=[],
        )
        return [
            ScoredPost(post=post_by_id[post_id], score=score)
            for post_id, score in fused[:limit]
        ]

    def _find_voice_candidates(
        self, idea: str, idea_embedding: TextEmbedding, target_word_count: int
    ) -> list[ScoredPost]:
        limit = self._settings.voice_examples_count
        fused, post_by_id = self._hybrid_search(
            idea,
            idea_embedding,
            limit=limit * 2,
            statuses=[PostStatus.PUBLISHED],
            origins=[PostOrigin.HUMAN],
        )

        word_count_by_id = {
            post_id: len(post.body.split()) for post_id, post in post_by_id.items()
        }
        reranked = rerank_by_word_count_proximity(
            scored_ids=fused,
            word_count_by_id=word_count_by_id,
            target_word_count=target_word_count,
        )

        # todo Maximal Marginal Relevance - MMR
        #           - diversity selection: pick first highest voice_score
        #           - pick others by MMR, i.e. penalizing embedding vector similarity:
        #               - MRR(p) = L x voice_score(p) - (1-L) x max(cosine_similarity(p, s)), for each s candidate; L = 0.7

        return [
            ScoredPost(post=post_by_id[post_id], score=score)
            for post_id, score in reranked[:limit]
        ]
