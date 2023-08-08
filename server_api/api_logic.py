from typing import List, Tuple

from db_driver.db_objects.article import Article
from db_driver.db_objects.cluster import Cluster
from db_utils.article_utils import ArticleUtils
from db_utils.cluster_utils import ClusterUtils
from db_utils.media_utils import MediaUtils
from logger import get_current_logger
from server_api.utils.exceptions import ArticleNotFoundException, NoSimilarArticlesException, \
    GetSimilarArticlesException
from server_api.objects.article_api_data import ArticleApiData


class APILogic:
    def __init__(self):
        self.server_logger = get_current_logger(task_type="api logic")
        self._article_utils = ArticleUtils()
        self._cluster_utils = ClusterUtils()
        self._media_utils = MediaUtils()

    def get_similar_articles_data(self, article_url: str) -> Tuple[List[ArticleApiData], str]:
        """
        This function get URL of an article and return similar articles that already classified to cluster
        :param article_url:
        :return:
        """
        self.server_logger.debug(f"Checking similar articles to article -> `{article_url}`")
        similar_articles: List[ArticleApiData] = list()
        article_object: Article = self._article_utils.get_article_by_url(article_url=article_url)

        if not article_object:
            desc = f"Didn't find article in db with article url: `{article_url}`"
            self.server_logger.warning(desc)
            raise ArticleNotFoundException(desc)

        # Getting title of article
        title = article_object.title

        if not article_object.cluster_id:
            desc = f"Didn't find similar classified articles in db with article url: `{article_url}`"
            self.server_logger.warning(desc)
            raise NoSimilarArticlesException(desc)

        # If cluster exists, getting other articles data
        self.server_logger.info(f"Found cluster: `{article_object.cluster_id}`")

        # Getting cluster
        try:
            cluster_object: Cluster = self._cluster_utils.get_cluster(article_object.cluster_id)
            articles = self._article_utils.get_articles(articles_id=cluster_object.articles_id)

            # Collect needed articles data
            self.server_logger.info(f"Got {len(articles)} similar articles")
            for index, article in enumerate(articles):

                # The same article the client is currently reading
                if article.url == article_url:
                    continue

                self.server_logger.debug(f"({index + 1}) Article data: `{str(article)}`")
                article_api_object = self.__get_convert_article_api_data(article=article)
                similar_articles.append(article_api_object)
        except Exception as e:
            desc = f"Error getting similar articles data - `{str(e)}`"
            self.server_logger.error(desc)
            raise GetSimilarArticlesException(desc)
        return similar_articles, title

    def __get_convert_article_api_data(self, article: Article) -> ArticleApiData:
        article_data = {
            "title": article.title,
            "media": article.media,
            "url": article.url,
            "icon_url": self._media_utils.get_google_article_icon_url(article.media),
            "publishing_time": article.publishing_time
        }
        article_api_object = ArticleApiData(**article_data)
        return article_api_object
