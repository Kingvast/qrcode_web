import json
import shutil
import time

from jinja2 import Environment, PackageLoader, select_autoescape

from app.server import app
from marshmallow import ValidationError
from sanic import response
from sanic.response import html
from sanic.views import HTTPMethodView
from views.serializers import RequestFormSchema
from views.utils import CreateView, failed_response, ok_response

# jiaja2 配置
env = Environment(
    loader=PackageLoader('views.routers', '../templates'),
    autoescape=select_autoescape(['html', 'xml', 'tpl']))


def template(tpl, **kwargs):
    template = env.get_template(tpl)
    return html(template.render(kwargs))


class UploadApp(CreateView):
    serializer_class = RequestFormSchema

    async def post(self, request, *args, **kwargs):
        self.context = await self.get_context(request, kwargs)
        serializer_class = self.get_serializer_class()
        # 反序列化请求数据
        serializer = serializer_class(strict=True, context=self.context)
        self.validated_data, errors = serializer.load(request.form)
        # 保存数据
        app_name = self.validated_data['app_name']
        version = self.validated_data['version']
        app_type = self.validated_data['type']
        app_query = list(
            app.db.get_query_result({
                'app_name': {
                    '$eq': app_name
                },
                'type': app_type,
                'version': version
            }))
        if len(list(app_query)) > 0:
            failed_response('app exist', 'app already exist')
            return template(
                'upload_result.html',
                upload_result='上传失败，app已存在',
                display_property='none',
                upload_url="location.href='http://{host}:{port}/upload'".
                format(host='localhost', port=app.config.PORT))
        if app_type == 'ios':
            application = app_name + '_' + version + '.ipa'
        else:
            application = app_name + '_' + version + '.apk'
        file_path = app.config.APP_FILES_DIR + application

        try:
            with open(file_path, 'wb') as f:
                f.write(self.context['file'][0].body)
            self.validated_data['file_path'] = file_path
        except KeyError:
            raise ValidationError("App file must exist")

        image_type = self.context['app_icon'][0].name.split('.')[-1]
        image_path = '{APP_IMAGES_DIR}{app_name}_{app_type}_{version}.' \
                     '{image_type}'.format(
                                APP_IMAGES_DIR=app.config.APP_IMAGES_DIR,
                                app_name=app_name,
                                app_type=app_type,
                                version=version,
                                image_type=image_type)

        try:
            with open(image_path, 'wb') as f:
                f.write(self.context['app_icon'][0].body)
            self.validated_data['image_path'] = image_path
        except KeyError:
            raise ValidationError('Image Not Exist')

        self.validated_data['updated_on'] = time.strftime(
            '%Y-%m-%d', time.localtime(time.time()))
        if self.check_exists(app_name, app_type):
            records = self.validated_data
            records['downloads'] = 0
            records['find'] = 'true'
            app.records.create_document(records)
        else:
            app_record = list(
                app.records.get_query_result({
                    'app_name': {
                        '$eq': app_name
                    },
                    'type': app_type
                }))
            doc_id = app_record[0]['_id']
            doc = app.records[doc_id]
            doc['version'] = version
            doc.save()

        app.db.create_document(self.validated_data)
        response_json = json.loads(self.response().body.decode("utf-8"))
        if response_json['ok'] is True:
            return template(
                'upload_result.html',
                upload_result='上传成功',
                display_property='inline',
                download_url=
                "location.href='http://{host}:{port}/download/{app_name}'".
                format(
                    host='localhost',
                    port=app.config.PORT,
                    app_name=str(app_name)),
                upload_url="location.href='http://{host}:{port}/upload'".
                format(host='localhost', port=app.config.PORT))

        else:
            return template(
                'upload_result.html',
                upload_result='上传失败',
                display_property='none',
                upload_url="location.href='http://{host}:{port}/upload'".
                format(host='localhost', port=app.config.PORT))

    async def get(self, request):
        return template('upload.html')


class DownloadApp(HTTPMethodView):
    """根据请求平台自动返回对应的 APP 应用
    """

    def get_device_family(self, user_agent):
        if 'iphone' in user_agent.lower() or 'ipad' in user_agent.lower():
            return 'ios'
        else:
            return 'android'

    async def get(self, request):
        device_family = self.get_device_family(request.headers['user-agent'])
        app_name = request.raw_args['app_name']
        app_details = list(
            app.db.get_query_result({
                'app_name': {
                    '$eq': app_name
                },
                'type': device_family
            },
                                    sort=[{
                                        'version': 'desc'
                                    }]))
        if app_details:
            app_record = list(
                app.records.get_query_result({
                    'app_name': {
                        '$eq': app_name
                    },
                    'type': device_family
                }))

            if app_record:
                doc_id = app_record[0]['_id']
                doc = app.records[doc_id]
                doc['downloads'] = doc['downloads'] + 1
                doc.save()

            app_info = app_details[0]
            application = app_info['file_path']
            download_name = application.split('/')[-1]
            return await response.file(application, filename=download_name)
        else:
            return failed_response('not exist', 'app not exist')


class PlistDownload(HTTPMethodView):
    async def get(self, request, app_name):
        app_details = list(
            app.db.get_query_result({
                'app_name': {
                    '$eq': app_name
                },
                'type': 'ios'
            },
                                    sort=[{
                                        'version': 'desc'
                                    }]))

        if app_details:
            app_record = list(
                app.records.get_query_result({
                    'app_name': {
                        '$eq': app_name
                    },
                    'type': device_family
                }))

            if app_record:
                doc_id = app_record[0]['_id']
                doc = app.records[doc_id]
                doc['downloads'] = doc['downloads'] + 1
                doc.save()

            app_info = app_details[0]
            ipa_url = app.config.APP_URL + app_info['app_name']
            app_info['ipa_url'] = ipa_url
            tem = template(
                'install.plist',
                ipa_url=app_info['ipa_url'],
                icon_url=app_info['image_path'],
                name=app_info['app_name'],
                bundle_id=app_info['bundle_id'],
                version=app_info['version'])
            headers = {"Content-Disposition": 'attachment'}
            return response.text(tem, headers=headers, content_type='text/xml')
        else:
            return failed_response('not exist', 'app not exist')


class DownloadPage(HTTPMethodView):
    def get_device_family(self, user_agent):
        if 'iphone' in user_agent.lower() or 'ipad' in user_agent.lower():
            return 'ios'
        else:
            return 'android'

    async def get(self, request, app_name):
        device_family = self.get_device_family(request.headers['user-agent'])
        app_details = list(
            app.db.get_query_result({
                'app_name': {
                    '$eq': app_name
                },
                'type': device_family
            },
                                    sort=[{
                                        'version': 'desc'
                                    }]))
        if app_details:
            image_path = app_details[0]['image_path']
            shutil.copy(image_path, './static/img/icon.png')
            app_url = 'https://{host}:{port}/download/{app_name}'.format(
                host=app.config.HOST,
                port=app.config.PORT,
                app_name=str(app_name))
            if device_family is 'android':
                app_download_url = \
                    'http://{host}:{port}/download?app_name={app_name}'.format(
                        host=app.config.HOST, port=app.config.PORT,
                        app_name=str(app_name))
            else:
                app_download_url = 'itms-services://?action=download-manifest&url=https://{host}:{port}/download/ios/{app_name}.plist'.format(
                    host=app.config.HOST,
                    port=app.config.PORT,
                    app_name=str(app_name))
            return template(
                'download.html',
                app_icon='../static/img/icon.png',
                app_name=app_details[0]['app_name'],
                app_version=app_details[0]['version'],
                updated_on=app_details[0]['updated_on'],
                app_download=app_download_url,
                app_url=app_url)
        else:
            return template('404.html')


class AppList(HTTPMethodView):
    async def get(self, request):
        app_details = list(
            app.records.get_query_result({
                'find': {
                    '$eq': 'true'
                }
            }))
        for app_detail in app_details:
            app_detail['image_path'] = shutil.copy2(app_detail['image_path'],
                                                    './static/img/')
        return template('app_list.html', app_details=app_details)
