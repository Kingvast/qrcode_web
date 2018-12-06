from sanic.blueprints import Blueprint
from views import views

blueprint = Blueprint('app_qrcode')

blueprint.static('/static', './static')

blueprint.add_route(views.UploadApp.as_view(), '/upload', methods=['POST'])
blueprint.add_route(views.DownloadApp.as_view(), '/download', methods=['GET'])

blueprint.add_route(
    views.DownloadPage.as_view(), '/download/<app_name>', methods=['GET'])
blueprint.add_route(
    views.PlistDownload.as_view(),
    '/download/ios/<app_name>.plist',
    methods=['GET'])
blueprint.add_route(views.AppList.as_view(), '/apps', methods=['GET'])
