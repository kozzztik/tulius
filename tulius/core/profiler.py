import threading
import time
import logging

from django import http
from ua_parser import user_agent_parser


class ProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @staticmethod
    def get_user_data(request):
        result = {}
        try:
            user_data = user_agent_parser.Parse(
                request.META['HTTP_USER_AGENT']
                if 'HTTP_USER_AGENT' in request.META else '')
            user_agent = user_data['user_agent']
            os = user_data['os']
            device_family = user_data['device']['family']
            result = {
                'browser': user_agent['family'],
                'browser_version': user_agent['major'],
                'os': os['family'],
                'os_version': os['major'],
                'device': device_family,
                'mobile': device_family not in [None, 'Spider', 'Other'],

            }
            if user_agent['minor']:
                result['browser_version'] += '.' + user_agent['minor']
            if not result['os_version']:
                os_list = result['os'].split()
                if len(os_list) == 2:
                    result['os'] = os_list[0]
                    result['os_version'] = os_list[1]
            if os['minor']:
                result['os_version'] += '.' + os['minor']
        except Exception:
            logger = logging.getLogger('django.request')
            logger.error(
                'Cant parse user agent %s',
                request.META.get('HTTP_USER_AGENT'))
        return result

    def log_record(self, request, exec_time, response):
        if isinstance(response, http.StreamingHttpResponse):
            content_length = None
        else:
            content_length = len(response.content)
        logging.getLogger('profiler').info(request.path, extra={
            'method': request.method,
            'status_code': response.status_code,
            'content_length': content_length,
            **({
                'app_name': request.resolver_match.app_name,
                'url_name': request.resolver_match.url_name,
                'view_name': request.resolver_match.view_name,
                'url_args': request.resolver_match.args,
                'url_kwargs': [{
                    'name': name,
                    'value': value
                } for name, value in request.resolver_match.kwargs.items()]
            } if request.resolver_match else {}),
            'user': {
                'id': request.user.id,
                'title': request.user.username
            } if request.user.is_authenticated else None,
            'exec_time': exec_time / 1000000,
            'thread_id': threading.current_thread().ident,
            'ip': request.META['REMOTE_ADDR'],
            **self.get_user_data(request)
        })

    def __call__(self, request):
        start_time = time.perf_counter_ns()
        response = self.get_response(request)
        exec_time = time.perf_counter_ns() - start_time
        self.log_record(request, exec_time, response)
        return response
