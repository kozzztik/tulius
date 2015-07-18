from django.db.models import get_model
from django.http import HttpResponse
from django.utils import simplejson
import locale
from smart_selects.utils import unicode_sorter

def filterchain_complex(request, app, model, field, value, manager=None):
    """
    While existing 'filterchain' looks for
        model.objects.filter(field=value),
    'filterchain_complex' is designed to look for
        model.objects.filter(field__in=set),
    where
        set <- ids from model2.objects.filter(pk=value)

    e.g: looking for all users avaible for forum, that current forum room belongs to:
        models: Room, Forum, User
            1.  User is a result model. We need to return a list containing User model objects
            2.  forum is a FK field of User model pointing to Forum model.
                But what is more important, it's also a Room model FK.
            3.  Room is sort of proxy model to look in.
        So, we have on input:
            1. room_id as value (note that it's not a forum id!)
            2. Users as model
            3. forum__room as a field
        Than we can split forum__room into
            a) forum, and call it ''
            b) room, and call it ''
        Than we need to get a forum id. Simply running
            room = Room.objects.get(pk=value) or Room.objects.filter(pk=value)[0]
        Here room.forum.id will be new value to provide to original 'filterchain' function
    """

    if len(field.split('__')) > 1 and field != field.lower():
        # real complex case
        # room and forum terms are used in according with comment
        # I haven't sleep for a long time, so I can't find better words right now, sorry
        field_list = field.split('__')
        new_field = '__'.join(field_list[:-1])
        room_model = field_list[-1].split('-')[0]
        forum_model_raw = field_list[-2]
        forum_model_fieldname = forum_model_raw.split('-')[-1].lower()
        if len(forum_model_raw.split('-')) > 1:
            forum_model = forum_model_raw.split('-')[-2]
        else:
            forum_model = forum_model_raw

        Room = get_model(app, room_model)
        room = Room.objects.filter(pk=value)[0]

#        raise ValueError(room, forum_model_fieldname)
        forum = getattr(room, forum_model_fieldname, None)

        #if value == 1:
        #raise ValueError(field, room_model, forum_model_raw, forum_model, forum_model_fieldname, Room, room, room.__class__, forum, forum.__class__)
            #raise ValueError(room, forum_model_fieldname, forum)

        new_value = forum.pk

        return filterchain_complex(request, app, model, new_field, new_value, manager)
    else:
        # backwards-compatibility for simple case
        return filterchain(request, app, model, field, value, manager)

def filterchain(request, app, model, field, value, manager=None):

    Model = get_model(app, model)
    if value == '0':
        keywords = {str("%s__isnull" % field):True}
    else:
        keywords = {str(field): str(value)}
    if manager is not None and hasattr(Model, manager):
        queryset = getattr(Model, manager).all()
    else:
        queryset = Model.objects
    results = list(queryset.filter(**keywords))
    results.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(unicode(x)))
    result = []
    for item in results:
        result.append({'value':item.pk, 'display':unicode(item)})
    json = simplejson.dumps(result)
    return HttpResponse(json, mimetype='application/json')

def filterchain_all(request, app, model, field, value):
    Model = get_model(app, model)
    if value == '0':
        keywords = {str("%s__isnull" % field):True}
    else:
        keywords = {str(field): str(value)}
    results = list(Model.objects.filter(**keywords))
    results.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(unicode(x)))
    final = []
    for item in results:
        final.append({'value':item.pk, 'display':unicode(item)})
    results = list(Model.objects.exclude(**keywords))
    results.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(unicode(x)))
    final.append({'value':"", 'display':"---------"})

    for item in results:
        final.append({'value':item.pk, 'display':unicode(item)})
    json = simplejson.dumps(final)
    return HttpResponse(json, mimetype='application/json')
