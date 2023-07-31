import os

from api.server_api import app

if __name__ == '__main__':
    HOST = os.getenv(key="HOST", default="0.0.0.0")
    DEBUG_MODE = bool(os.getenv(key="DEBUG_MODE", default=False))
    app.run(host=HOST, debug=DEBUG_MODE)
