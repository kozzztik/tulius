from .models import ExceptionMessage, ExceptionTraceback, ExceptionMETAValue, ExceptionCookie
import sys
import traceback

class ExceptionMiddleware():
    def buildqueryString(self, params):
        if not params:
            return ""
        return "\n".join(["%s=%s" % (k, v) for k, v in params.items()])

    def process_exception(self, request, exception):
        exception_message = ExceptionMessage()
        user = getattr(request, 'user', None)
        if user and (not user.is_anonymous()):
            exception_message.user = user
        tracebacklist = None
        exception_message.save()
        try:
            exception_message.get_data = self.buildqueryString(getattr(request, 'GET', None))[:100]
            exception_message.post_data = self.buildqueryString(getattr(request, 'POST', None))[:100]
            exception_message.save()
        except:
            pass
        request.bug_message = exception_message
        (exc_type, exc_value, exc_traceback) = sys.exc_info()
        try:
            try:
                exception_message.classname = exc_type.__name__
                exception_message.title = unicode(exc_value)
                exception_message.title = exception_message.title[:125]
                exception_message.save()
            except:
                pass
            tracebacklist = traceback.extract_tb(exc_traceback)
            tr_entry = None
            for (tr_filename, tr_line, tr_function, tr_text) in tracebacklist:
                tr_entry = ExceptionTraceback(exception_message=exception_message)
                tr_entry.filename = tr_filename
                try:
                    tr_entry.line_num = int(tr_line)
                except:
                    pass 
                tr_entry.function_name = tr_function
                tr_entry.body = tr_text
                tr_entry.save()
            if tr_entry:
                exception_message.location = tr_entry.filename + " in " + tr_entry.function_name + \
                    ", line " + str(tr_entry.line_num)
                exception_message.save()
        finally:
            tracebacklist = None
            exc_traceback = None
        cookies = getattr(request, 'COOKIES', None)
        if cookies:
            for cookie in cookies:
                try:
                    cookie_entry = ExceptionCookie(name=cookie, exception_message=exception_message)
                    cookie_entry.value = cookies[cookie][:125]
                    cookie_entry.save()
                except:
                    pass
        metas = getattr(request, 'META', None)
        if metas:
            for meta in metas:
                if meta == 'PATH_INFO':
                    exception_message.path = metas[meta]
                    exception_message.save()
                meta_entry = ExceptionMETAValue(name=meta, exception_message=exception_message)
                try:
                    meta_entry.value = unicode(metas[meta])
                    meta_entry.save()
                except:
                    pass
        request.bug_message = exception_message
        return None
    