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
    logger.debug(f"Try getting similar articles"),
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
            logger.debug(str(e))

    logger.info(f"(get_similar_articles) return data: `{return_data}`")
    return return_data
