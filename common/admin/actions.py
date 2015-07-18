# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from common.csv_unicode_writer import UnicodeWriter

def export_as_csv(modeladmin, request, queryset):
    """
    Generic csv export admin action.
    """
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')
    writer = UnicodeWriter(response)
    field_names = [field.name for field in opts.fields]
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for obj in queryset:
        row = []
        for field in field_names:
            if field in field_names:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                val = u"%s" % (val,)
                row.append(val)
        writer.writerow(row)
    return response
export_as_csv.short_description = _(u'Экспортировать выбранное в формате электронной таблицы csv')
