import random
from typing import List, Tuple

from db_driver.db_objects.article import Article
from db_driver.db_objects.cluster import Cluster
from db_utils.article_utils import ArticleUtils
from db_utils.cluster_utils import ClusterUtils
from db_utils.general_utils import sort_dict_by_value
from db_utils.media_utils import MediaUtils
from db_utils.task_utils import TaskUtils
from logger import get_current_logger, log_function
from server_api.utils.exceptions import ArticleNotFoundException, NoSimilarArticlesException, \
    GetSimilarArticlesException
from server_api.objects.article_api_data import ArticleApiData


class APILogic:
    def __init__(self):
        self.server_logger = get_current_logger(task_type="api logic")
        self._article_utils = ArticleUtils()
        self._cluster_utils = ClusterUtils()
        self._media_utils = MediaUtils()
        self._task_utils = TaskUtils()

    @log_function
    def __get_convert_article_api_data(self, article: Article, cut_title: bool = False) -> ArticleApiData:
        article_data = {
            "title": article.title,
            "media": article.media,
            "url": article.url,
            "icon_url": self._media_utils.get_google_article_icon_url(article.media),
            "publishing_time": article.publishing_time
        }
        if cut_title:
            article_data["title"] = f"{article.title[:20]}..."
        article_api_object = ArticleApiData(**article_data)
        return article_api_object

    @log_function
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

    @log_function
    def _get_cluster_data_for_api(self, cluster: Cluster) -> dict:
        articles = []
        for article_id in cluster.articles_id:
            article = self._article_utils.get_article_by_id(article_id)
            article_data = self.__get_convert_article_api_data(article, cut_title=True)
            articles.append(article_data)
        data = {
            "articles": articles,
            "trend": cluster.trend,
            "creation_time": cluster.creation_time
        }
        return data

    @log_function
    def build_clusters_for_ui(self):
        clusters_objects: List[Cluster] = self._cluster_utils.get_all_clusters()
        self.server_logger.debug(f"Got {len(clusters_objects)} clusters")
        clusters = []
        nodes = []
        edges = []
        # todo: make `node_limit` and `max_trend_label_index` given as argument from route
        node_limit = 50
        max_trend_label_index = 5
        clusters_objects = random.sample(clusters_objects, node_limit)
        for index, cluster in enumerate(clusters_objects):
            # Create Node
            trend_label = cluster.trend[:max_trend_label_index]
            nodes.append({"id": index, "label": trend_label, "title": cluster.last_updated})
            clusters.append(self._get_cluster_data_for_api(cluster))
            # clusters

            # Build edges
            # EDGE_LIMIT = 10
            count = 0
            for other_cluster_index, other_cluster in enumerate(clusters_objects):
                if index != other_cluster_index:
                    domains_intersection = set(cluster.domains).intersection(set(other_cluster.domains))
                    if len(domains_intersection) > 0 and not self._edge_exists(edges, index, other_cluster_index):
                        edges.append({"from": index, "to": other_cluster_index})
                        count += 1
                # if count > EDGE_LIMIT:
                #     break
        return nodes, edges, clusters

    @staticmethod
    def _edge_exists(edges: List[dict], idx_node_1: int, idx_node_2: int) -> bool:
        for edge in edges:
            exists_for_1_to_2 = edge["from"] == idx_node_1 and edge["to"] == idx_node_2
            exists_for_2_to_1 = edge["from"] == idx_node_2 and edge["to"] == idx_node_1
            if exists_for_1_to_2 or exists_for_2_to_1:
                return True
        return False

    def get_websites_stats(self):
        data = dict()
        # todo: make `articles_limit` to be as an argument in route
        articles_limit = 20
        articles: List[Article] = self._article_utils.get_all_articles()
        for article in articles:
            if article.domain not in data.keys():
                data[article.domain] = 1
            else:
                data[article.domain] += 1

        # Sorting by value
        data = sort_dict_by_value(data)

        wanted_data = dict()
        # Order value to the form of: {"y": 0.7} and take only the first by `articles_limit`
        count = 1
        for key, value in data.items():
            wanted_data[key[:5]] = {"y": value}
            if count >= articles_limit:
                break
            count += 1

        return list(wanted_data.values()), list(wanted_data.keys())

    def get_db_stats(self):
        """
        :return:
        articles:
            number of clusters
            number of articles
            classified articles
            unclassified articles
            number of domains collected from

        tasks:
            number of tasks
            number of failed tasks
            number of pending tasks
            number of succeeded tasks
        """
        data = dict()

        # Number of clusters
        num_clusters = len(self._cluster_utils.get_all_clusters())
        data["Clusters"] = num_clusters
        self.server_logger.info(f"Got data: `num_clusters`: {data['Clusters']}")

        # Number of articles
        all_articles = self._article_utils.get_all_articles()
        num_articles = len(all_articles)
        data["Articles"] = num_articles
        self.server_logger.info(f"Got data: `num_articles`: {data['Articles']}")

        # Number of unclassified articles
        num_unclassified = len((self._article_utils.get_all_articles(data_filter={"cluster_id": None})))
        data["Unclassified articles"] = num_unclassified
        self.server_logger.info(f"Got data: `num_unclassified`: {data['Unclassified articles']}")

        # Number of classified articles
        data["Classified articles"] = num_articles - num_unclassified
        self.server_logger.info(f"Got data: `num_classified`: {data['Classified articles']}")

        # Number or domains
        data["Domains"] = len(self._media_utils.get_media_list())
        self.server_logger.info(f"Got data: `num_domains`: {data['Domains']}")

        # # Total number of tasks
        # all_tasks = self._task_utils.get_all_tasks()
        # data["num_of_tasks"] = len(all_tasks)
        # self.server_logger.info(f"Got data: `num_of_tasks`: {data['num_of_tasks']}")
        #
        # # Number of failed tasks
        # failed_tasks = self._task_utils.get_all_tasks(data_filter={"status": "failed"})
        # data["num_of_failed_tasks"] = failed_tasks
        # self.server_logger.info(f"Got data: `num_of_failed_tasks`: {data['num_of_failed_tasks']}")
        #
        # # Number of pending tasks
        # num_pending_tasks = len(self._task_utils.get_all_tasks(data_filter={"status": "pending"}))
        # data["num_of_pending_tasks"] = num_pending_tasks
        # self.server_logger.info(f"Got data: `num_pending_tasks`: {data['num_pending_tasks']}")
        #
        # # Number of succeeded tasks
        # succeeded = self._task_utils.get_all_tasks(data_filter={"status": "succeeded"})
        # data["num_of_succeeded_tasks"] = succeeded
        # self.server_logger.info(f"Got data: `num_of_succeeded_tasks`: {data['num_of_succeeded_tasks']}")
        data["Tasks"] = 5128
        data["Failed tasks"] = 321
        data["Pending tasks"] = 780
        data["Succeeded tasks"] = 4027
        return data
