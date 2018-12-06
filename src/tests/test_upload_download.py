import importlib
import os
import tempfile

import pytest

from app.server import app as sanic_app
from sanic.server import HttpProtocol


@pytest.yield_fixture
def app():
    """
    创建 sanic app, 进入时同步数据表, 退出时删除测试数据
    """

    if 'DEBUG' not in sanic_app.config:
        config_object = importlib.import_module('configs')
        sanic_app.config.from_object(config_object)

    yield sanic_app


@pytest.fixture
def client(loop, app, test_client):
    """创建 http client
    """
    return loop.run_until_complete(test_client(app, protocol=HttpProtocol))


class TestUploadDownload:

    client = None

    async def test_upload_and_download(self, client):
        self.client = client
        await self.upload()
        # await self.download()

    async def upload(self):
        """测试上传
        """
        root_dir = os.path.split(os.path.realpath(__file__))[0] + '/'
        apk_file = open(root_dir + '/zhajinhua.apk')

        data = {
            'app_name': '3Q_DouDiZhu.apk',
            'version': '1.1.1',
            'type': 'android',
            'bundle_id': '',
            'package_name': 'zhajinhua',
            'md5': '********',
            'file': apk_file
        }
        url = '/upload'
        response = await self.client.post(url, data=data)
        assert response.status is 200
        response_json = await response.json()
        print(response_json)
        assert response_json['ok']

    async def download(self):
        """测试下载
        """

        url = '/download?app_name=3Q_DouDiZhu.apk'
        response = await self.client.get(
            url,
            headers={
                'User-Agent':
                ('Mozilla/5.0 (Linux; U; Android 4.4.4; zh-CN; '
                 'HTC D820u Build/KTU84P) AppleWebKit/537.36 '
                 '(KHTML, like Gecko) Version/4.0 Oupeng/10.2.3.88150 '
                 'Mobile Safari/537.36')
            })
        assert response.status is 200
