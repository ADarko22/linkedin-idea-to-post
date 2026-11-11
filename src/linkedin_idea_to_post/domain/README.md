# LinkedIn Idea to Post – Domain

This directory contains the core domain models and logic of the LinkedIn Idea to Post application.

## Content

### 1. [post.py](post.py)

Defines the `Post` class, which represents a LinkedIn post.

It includes attributes such as:

- **Title**: The post's title.
- **Content**: The post's textual content.
- **Metadata**: Additional information associated with the post.

All timestamps use UTC to ensure consistency across different time zones.

### 2. [post_text.py](post_text.py)

Contains pure functions for extracting text from the textual content of a LinkedIn post.

These functions are designed to be reusable across different parts of the application.