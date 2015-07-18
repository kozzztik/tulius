from django.utils.timezone import make_aware, get_current_timezone
from django.conf import settings
from datetime import datetime
import csv
import os
import sys
from django.core.files.base import ContentFile
from django.utils.encoding import smart_unicode
import logging
logger = logging.getLogger('django.request')

def simple_open_file(path, binary=False):
    path = settings.MEDIA_ROOT + 'migrate/' + path
    if not os.path.exists(path):
        return None
    read_mode = 'r'
    if binary:
        read_mode += 'b'
    f = open(path, read_mode)
    return f

def open_file(path):
    path = settings.MEDIA_ROOT + 'migrate/' + path
    if not os.path.exists(path):
        return None
    f = open(path, 'r')
    data = f.read()
    data = data.replace('\x00', '')
    f.close()
    f = ContentFile(data)
    csv.field_size_limit(sys.maxint)
    reader = csv.reader(f, delimiter='|', quoting=csv.QUOTE_NONE)
    return reader

def prepare_str(s):
    s2 = s.replace('[BR]', '<br />').replace('[br]', '<br />').replace('[i]', '<i>').replace('[/i]', '</i>')
    s2 = s2.replace('[s]', '<s>').replace('[/s]', '</s>').replace('[b]', '<b>').replace('[/b]', '</b>')
    return s2

def open_inc_file(path):
    path = settings.MEDIA_ROOT + 'migrate/' + path
    if not os.path.exists(path):
        return ''
    f = open(path, 'r')
    return prepare_str(unicode(f.read().decode('cp1251')))

def get_obj(row, model, **kwargs):
    obj_id = parse_str(row[0])
    models = model.objects.filter(old_id = obj_id, **kwargs)
    if models:
        return models[0]
    else:
        return model(old_id = obj_id, **kwargs)

def get_gamed_obj(row, model, game=None, **kwargs):
    obj_id = parse_str(row[0])
    if game:
        models = model.objects.filter(game=game, old_id = obj_id, **kwargs)
    else:
        models = model.objects.filter(game__isnull=True, old_id = obj_id, **kwargs)
    if models:
        return models[0]
    else:
        return model(old_id = obj_id, game=game, **kwargs)

def get_obj_or_none(model, **kwargs):
    objs = model.objects.filter(**kwargs)
    if objs:
        return objs[0]
    else:
        return None
    
def parse_date(s):
    timezone = get_current_timezone()
    return make_aware(datetime.strptime(s, "%d.%m.%Y"), timezone)
    
def parse_str(s):
    return smart_unicode(s.decode('cp1251'))

def parse_str_def(row, num, value=''):
    if len(row) > num:
        return prepare_str(smart_unicode(row[num].decode('cp1251')))
    else:
        return smart_unicode(value)
