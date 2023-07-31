class ArticleNotFoundException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class NoSimilarArticlesException(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class GetSimilarArticlesException(Exception):
    def __init__(self, msg: str):
        self.msg = msg
