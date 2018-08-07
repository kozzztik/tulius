import threading
import time
import logging

from djfw.profiler import models
from djfw.profiler import wrappers
from djfw.profiler.ua_parser import user_agent_parser


decorators_lock = threading.Lock()
decorated = False


class ProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # TODO: DB logging broken after django 2.0 migration
        # decorators_lock.acquire()
        # try:
        #     global decorated
        #     if not decorated:
        #         from django.template.base import Template
        #         Template.render = templates_decorator(Template.render)
        #         from django.db.backends import util
        #         util.CursorWrapper = CursorWrapper
        #         util.CursorDebugWrapper.execute = cursor_exec_decorator(
        #             util.CursorDebugWrapper.execute)
        #         decorated = True
        # finally:
        #     decorators_lock.release()

    def process_view(self, request, view_func, view_args, view_kwargs):
        rec = models.ProfilerMessage()
        rec.module_name = view_func.__module__[:255]
        rec.func_name = getattr(view_func, '__name__', None)
        if not rec.func_name:
            cls = getattr(view_func, '__class__', None)
            if cls:
                rec.func_name = getattr(cls, '__name__', None)
            if not rec.func_name:
                return
        rec.func_name = rec.func_name[:255]
        user = getattr(request, 'user', None)
        if user and (not user.is_anonymous):
            rec.user_id = user.pk
        rec.exec_time = int(time.clock() * 1000)
        wrappers.local_counter.clear()
        rec.db_time = 0
        rec.db_count = 0
        rec.template_time = 0
        rec.template_db_time = 0
        rec.template_db_count = 0
        rec.thread_id = threading.current_thread().ident
        if view_args:
            try:
                rec.exec_param = int(view_args[0])
            except:
                pass
        elif view_kwargs:
            try:
                rec.exec_param = int(view_kwargs.values()[0])
            except:
                pass
        rec.ip = request.META['REMOTE_ADDR']
        try:
            user_data = user_agent_parser.Parse(
                request.META['HTTP_USER_AGENT']
                if 'HTTP_USER_AGENT' in request.META else '')
            user_agent = user_data['user_agent']
            rec.browser = user_agent['family']
            rec.browser_version = user_agent['major']
            if user_agent['minor']:
                rec.browser_version += '.' + user_agent['minor']
            os = user_data['os']
            rec.os = os['family']
            rec.os_version = os['major']
            if not rec.os_version:
                os_list = rec.os.split()
                if len(os_list) == 2:
                    rec.os = os_list[0]
                    rec.os_version = os_list[1]
            if os['minor']:
                rec.os_version += '.' + os['minor']
            device = user_data['device']
            device_family = device['family']
            rec.device = device_family
            rec.mobile = True if (
                device_family and not (device_family == 'Spider')
            ) else False
        except:
            logger = logging.getLogger('django.request')
            logger.error(
                'Cant parse user agent %s', request.META['HTTP_USER_AGENT'])
        request.profiler = rec

    def save_rec(self, request, error=False):
        rec = getattr(request, 'profiler', None)
        if (not rec) or rec.pk:
            return
        end_time = int(time.clock() * 1000)
        rec.exec_time = end_time - rec.exec_time
        rec.db_time = wrappers.local_counter.exec_time
        rec.template_time = wrappers.local_counter.temlate_time
        rec.template_db_time = wrappers.local_counter.template_db_time
        rec.template_db_count = wrappers.local_counter.template_db_count
        if rec.db_time > rec.exec_time:
            rec.db_time = rec.exec_time
        rec.db_count = wrappers.local_counter.exec_count
        rec.error = error
        rec.save()

    def __call__(self, request):
        self.save_rec(request)
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        self.save_rec(request, error=True)
