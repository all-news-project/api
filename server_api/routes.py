from flask import request, render_template

from logger import get_current_logger
from server_api import app
from server_api.api_logic import APILogic
from server_api.utils.consts import ServerApiConsts
from server_api.utils.exceptions import ArticleNotFoundException, NoSimilarArticlesException, \
    GetSimilarArticlesException


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_similar_articles', methods=['GET'])
def get_similar_articles():
    logger = get_current_logger()
    logger.debug(f"Try getting similar articles")
    return_data = {"articles_data": list(), "error_msg": "", "succeeded": False, "title": ""}
    if 'url' not in request.args:
        return_data["error_msg"] = ServerApiConsts.MSG_URL_REQUIRED
        logger.logger.warning(f"Didn't get the current url of the article")
    else:
        try:
            api_logic = APILogic()
            article_url: str = request.args['url']
            similar_articles_data, title = api_logic.get_similar_articles_data(article_url=article_url)
            return_data["articles_data"] = similar_articles_data
            return_data["title"] = title
            return_data["succeeded"] = True
            logger.info(f"Got {len(similar_articles_data)} similar articles")
        except ArticleNotFoundException:
            return_data["error_msg"] = ServerApiConsts.MSG_ARTICLE_NOT_FOUND
        except NoSimilarArticlesException:
            return_data["error_msg"] = ServerApiConsts.MSG_NO_SIMILAR_ARTICLES_FOUND
        except GetSimilarArticlesException:
            return_data["error_msg"] = ServerApiConsts.MSG_GETTING_SIMILAR_ARTICLES
        except Exception as e:
            logger.error(str(e))

    logger.info(f"(get_similar_articles) return data: `{return_data}`")
    return return_data


@app.route('/get_clusters_for_ui', methods=['GET'])
def get_clusters_for_ui():
    logger = get_current_logger()
    logger.debug(f"Try getting clusters for ui")
    return_data = {"nodes": list(), "edges": list(), "succeeded": False}
    try:
        api_logic = APILogic()
        nodes, edges, clusters = api_logic.build_clusters_for_ui()
        return_data["nodes"] = nodes
        return_data["edges"] = edges
        return_data["clusters"] = clusters
        return_data["succeeded"] = True
    except Exception as e:
        logger.error(str(e))

    logger.info(f"(get_similar_articles) return data: `{return_data}`")
    return return_data


@app.route('/get_websites_stats', methods=['GET'])
def get_websites_stats():
    logger = get_current_logger()
    logger.debug(f"Try getting websites statistic data for ui")
    return_data = {"values": list(), "labels": list(), "succeeded": False}
    try:
        api_logic = APILogic()
        values, labels = api_logic.get_websites_stats()
        return_data["values"] = values
        return_data["labels"] = labels
        return_data["succeeded"] = True
    except Exception as e:
        logger.error(str(e))

    logger.info(f"(get_websites_stats) return data: `{return_data}`")
    return return_data


@app.route('/get_db_stats', methods=['GET'])
def get_db_stats():
    logger = get_current_logger()
    logger.debug(f"Try getting db statistic data for ui")
    return_data = {"data": dict(), "succeeded": False}
    try:
        api_logic = APILogic()
        data = api_logic.get_db_stats()
        return_data["data"] = data
        return_data["succeeded"] = True
    except Exception as e:
        logger.error(str(e))

    logger.info(f"(get_db_stats) return data: `{return_data}`")
    return return_data
