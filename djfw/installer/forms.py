from collections import OrderedDict

from django import forms
from django.conf import settings
from django.forms.widgets import media_property
from django.utils.translation import ugettext_lazy as _

from .maintaince import operations
from .models import MaintenanceLog


class AddMaintainceForm(forms.Form):
    do_backup = forms.BooleanField(
        label=_(u'Do backup'),
        initial=True,
        required=False
    )
    repository = forms.BooleanField(
        label=_(u'Update repository'),
        initial=True,
        required=False
    )
    buildout = forms.BooleanField(
        label=_(u'Update dependecies'),
        initial=True,
        required=False
    )
    vhost = forms.BooleanField(
        label=_(u'Update apache virtual host'),
        initial=True,
        required=False
    )
    syncdb = forms.BooleanField(
        label=_(u'Migrate DB'),
        initial=True,
        required=False
    )
    static = forms.BooleanField(
        label=_(u'Collect static files'),
        initial=True,
        required=False
    )
    comment = forms.CharField(
        max_length=255,
        label=_(u'Comment'),
        initial='',
        required=False,
        widget=forms.Textarea()
    )


class ChangeMaintainceForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLog
        fields = ('end_time', 'state', 'status')


def get_declared_fields(bases, attrs, with_base_fields=True):
    fields = []
    operation_list = getattr(
        settings, 'INSTALLER_OPERATIONS', operations.DEFAULT_OPERATIONS)
    for operation in operation_list:
        field = forms.BooleanField(
            label=operation.caption,
            initial=operation.default_run, required=False)
        fields = fields + [(operation.name, field)]
    comment = forms.CharField(
        max_length=255,
        label=_(u'Comment'),
        initial='',
        required=False,
        widget=forms.Textarea()
    )
    fields = fields + [('comment', comment)]
    # fields.sort(key=lambda x: x[1].creation_counter)
    return OrderedDict(fields)


class OptionsFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        new_class = super(OptionsFormMetaclass, cls).__new__(
            cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class


class OperationsForm(forms.BaseForm):
    __metaclass__ = OptionsFormMetaclass
