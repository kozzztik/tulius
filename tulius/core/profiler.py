import datetime
import uuid

import asyncio
import threading
import time
import logging

from django import http
from django.core import exceptions
from ua_parser import user_agent_parser

from tulius.core.elastic import indexer


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


def log_record(request, exec_time, response):
    # get only cached user. Don't trigger auth just for profiling needs.
    # Also, auth middleware may be not installed.
    user = getattr(request, '_cached_user', None)
    if isinstance(response, http.StreamingHttpResponse):
        content_length = None
    else:
        content_length = len(response.content)
    host = None
    try:
        host = request.get_host()
    except exceptions.DisallowedHost:
        pass
    now = datetime.datetime.utcnow()
    indexer.get_indexer().index({
        '_action': 'index',
        '_index': f'requests_{now.year}_{now.month}',
        '_id': str(uuid.uuid4()),
        '@timestamp': now.isoformat(),
        'message': request.path,
        'scheme': request.scheme,
        'host': host,
        'method': request.method,
        'status_code': response.status_code,
        'content_length': content_length,
        **({
            'app_name': request.resolver_match.app_name,
            'url_name': request.resolver_match.url_name,
            'view_name': request.resolver_match.view_name,
            'url_args': [str(arg) for arg in request.resolver_match.args],
            'url_kwargs': [{
                'name': name,
                'value': str(value)
            } for name, value in request.resolver_match.kwargs.items()]
        } if request.resolver_match else {}),
        'user': {
            'id': user.id,
            'title': user.username
        } if user and user.is_authenticated else None,
        'exec_time': exec_time / 1000000,
        'thread_id': threading.current_thread().ident,
        'ip': request.META['REMOTE_ADDR'],
        **get_user_data(request),
        **request.profiling_data,
    })


def profiler_middleware(get_response):
    if asyncio.iscoroutinefunction(get_response):
        return AsyncProfilerMiddleware(get_response)
    return SyncProfilerMiddleware(get_response)


class SyncProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter_ns()
        request.profiling_data = {}
        response = self.get_response(request)
        exec_time = time.perf_counter_ns() - start_time
        log_record(request, exec_time, response)
        return response


class AsyncProfilerMiddleware:
    _is_coroutine = asyncio.coroutines._is_coroutine

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        start_time = time.perf_counter_ns()
        request.profiling_data = {}
        response = await self.get_response(request)
        exec_time = time.perf_counter_ns() - start_time
        log_record(request, exec_time, response)
        return response


profiler_middleware.async_capable = True
