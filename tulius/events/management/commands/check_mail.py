# -*- coding: utf-8 -*-
from __future__ import print_function

from django.core.management.base import BaseCommand
from django.conf import settings
from tulius.events import IncomeMail
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

def load_backend(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing mail receiver backend %s: "%s"' % (path, e))
    except ValueError:
        raise ImproperlyConfigured('Error importing mail receiver backends. Is MAIL_RECEIVERS a correctly defined list or tuple?')
    try:
        cls = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" mail receiver' % (module, attr))
    return cls

class Command(BaseCommand):
        
    def handle(self, **options):
        middleware_list = getattr(settings, 'MAIL_RECEIVERS', [])
        middleware_list = [(load_backend(path), path) for path in middleware_list]
        for mail in IncomeMail.objects.all():
            for proc in middleware_list:
                exec_proc = proc[0]
                if exec_proc(mail):
                    break
            mail.delete()
