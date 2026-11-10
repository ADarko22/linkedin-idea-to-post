from linkedin_idea_to_post.linkedin.raw_post import RawPost


class CSVPostParserResult:
    def __init__(self):
        self.raw_posts = list[RawPost]()
        self.errors = list[str]()

    def add_error(self, error: str):
        self.errors.append(error)

    def add_raw_post(self, raw_post: RawPost):
        self.raw_posts.append(raw_post)
