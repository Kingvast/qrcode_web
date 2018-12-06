"""
sanic server
"""

from app import app
from cloudant import Cloudant
from views.routers import blueprint

app.blueprint(blueprint)


@app.listener('before_server_start')
def start_connection(app, loop):
    app.client = Cloudant(
        app.config.COUCHDB_USER,
        app.config.COUCHDB_PASSWORD,
        url=app.config.COUCHDB_URL,
        connect=True)
    app.db = app.client[app.config.COUCHDB_DATABASE]
    app.records = app.client[app.config.COUCHDB_RECORDS]


@app.listener('after_server_stop')
def stop_connection(app, loop):
    app.client.disconnect()


def run_server():
    """启动服务器
    根据启动参数加载配置, 如果没有相应的配置文件直接抛出错误
    """
    app.run(
        host=app.config.HOST,
        port=app.config.PORT,
        workers=app.config.WORKERS,
        debug=app.config.DEBUG)
