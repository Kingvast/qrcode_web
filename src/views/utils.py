from inspect import isawaitable

from app.server import app
from marshmallow.exceptions import ValidationError
from sanic.response import json
from sanic.views import HTTPMethodView
from views.exceptions import APIException, WrongRequestFormat


def ok_response(body, message='', *args, **kwargs):
    """成功的 response
    """
    new_body = {'ok': True, 'message': message, 'result': body}
    return json(new_body, *args, **kwargs)


def failed_response(error_type, error_message, *args, **kwargs):
    """失败的 response
    """
    body = {'ok': False, 'error_type': error_type, 'message': error_message}
    return json(body, *args, **kwargs)


def validation_error_response(validation_error, *args, **kwargs):
    """字段验证失败的 response
    validation_error: ValidationError
    """
    errors = list()
    for field in validation_error.field_names:
        field_error = {
            'error_type': 'validation_error',
            'field': field,
            'message': validation_error.messages[field][0]
        }
        errors.append(field_error)

    new_body = {'ok': False, 'errors': errors}
    return json(new_body, *args, **kwargs)


class APIBaseView(HTTPMethodView):
    """扩展 class based view, 增加异常处理
    """

    async def dispatch_request(self, request, *args, **kwargs):
        """扩展 http 请求的分发, 添加错误处理
        """
        try:
            response = super(APIBaseView, self).dispatch_request(
                request, *args, **kwargs)
            if isawaitable(response):
                response = await response
        except Exception as exception:
            response = await self.handle_exception(exception)
        return response

    async def handle_exception(self, exception):
        """处理异常
        ValidationError, APIException: 返回适当的错误信息
        else: 重新抛出异常
        """
        if isinstance(exception, ValidationError):
            response = validation_error_response(exception)
        elif isinstance(exception, APIException):
            response = failed_response(
                error_type=exception.error_type,
                error_message=exception.error_message)
        else:
            # 非 debug 模式下, 发送错误消息到 sentry
            if not app.config.DEBUG:
                app.sentry.captureException()
            raise exception
        return response


class CreateView(APIBaseView):
    """创建数据的 view
    1. 获取上下文: 通过数据库或其他 model 层获取数据
    2. 验证请求数据
    3. 保存数据
    """
    serializer_class = None

    def get_serializer_class(self):
        """如果需要根据请求数据使用不同的 serializer, 在子类中覆盖这个方法
        """
        assert self.serializer_class is not None, \
            'Must assign serializer class'
        return self.serializer_class

    async def get_context(self, request, kwargs):
        """从数据库获取上下文, 用于传入 serializer 中, 帮助验证请求数据
        默认返回空字典, 需要特定的上下文在子类中覆盖这个方法
        """
        return request.files

    def response(self):
        """响应结果
        默认返回空 json 对象, 需要修改则在子类中覆盖这个方法
        """
        return ok_response({})

    def check_exists(self, name, platform):
        app_query = list(
            app.db.get_query_result({
                'app_name': {
                    '$eq': name
                },
                'type': platform,
            }))
        if len(list(app_query)) > 0:
            return False

        return True
