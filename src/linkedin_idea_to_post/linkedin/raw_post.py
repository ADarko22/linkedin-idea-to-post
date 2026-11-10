from pydantic import BaseModel


class RawPost(BaseModel):
    date: str
    share_link: str
    shareCommentary: str
