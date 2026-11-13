# LinkedIn Idea to Post – Domain

This directory contains the core domain models and boundary contracts, ensuring the domain module remains independent of
external implementation details.

## Main Components

### 1. [post.py](post.py)

Defines the `Post` class, representing a LinkedIn post.

| Attribute    | Description                                      |
|--------------|--------------------------------------------------|
| **Title**    | The post's title.                                |
| **Content**  | The post's textual content.                      |
| **Metadata** | Additional information associated with the post. |

**Timestamps:** All timestamps use UTC to ensure consistency across different time zones.

### 2. [drafting.py](drafting.py)

Defines the `DraftWriter` protocol, which abstracts the logic responsible for transforming the user's idea into a
LinkedIn post draft.

| Method                                  | Description                                           |
|-----------------------------------------|-------------------------------------------------------|
| `write(request: DraftRequest) -> Draft` | Generates a LinkedIn post draft from the user's idea. |