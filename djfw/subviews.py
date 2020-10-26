from django import http
from django import forms
from django.core import exceptions
from django.views.generic import edit
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _


class ParentObjectMixin:
    """
    Provides the ability to retrieve a parent object for further manipulation.
    """
    parent_model = None
    parent_queryset = None
    parent_slug_field = 'slug'
    parent_context_object_name = None
    parent_slug_url_kwarg = 'slug'
    parent_pk_url_kwarg = 'pk'
    parent_obj_foreign_key = None

    def check_parent_rights(self, obj, user):
        return True

    def get_parent_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_parent_queryset()
        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.parent_pk_url_kwarg, None)
        slug = self.kwargs.get(self.parent_slug_url_kwarg, None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)
        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_parent_slug_field()
            queryset = queryset.filter(**{slug_field: slug})
        # If none of those are defined, it's an error.
        else:
            raise AttributeError(
                'Generic parent detail view %s must be called with '
                'either an object pk or a slug.' % self.__class__.__name__)
        try:
            parent_obj = queryset.get()
        except exceptions.ObjectDoesNotExist as exc:
            raise http.Http404(
                _('No %(verbose_name)s found matching the query') %
                {'verbose_name': queryset.model._meta.verbose_name}
            ) from exc
        if not self.check_parent_rights(parent_obj, self.request.user):
            raise exceptions.PermissionDenied()

        if not self.parent_obj_foreign_key:
            obj = getattr(self, 'object')
            if obj:
                model = obj.__class__
            else:
                model = getattr(self, 'model')
            if model:
                fk = forms.models._get_foreign_key(parent_obj.__class__, model)
                self.parent_obj_foreign_key = fk.name
        return parent_obj

    def get_parent_queryset(self):
        """
        Get the queryset to look an object up against. May not be called if
        `get_object` is overridden.
        """
        if self.parent_queryset is None:
            if self.parent_model:
                return self.parent_model._default_manager.all()
            raise exceptions.ImproperlyConfigured(
                '%(cls)s is missing a queryset. Define '
                '%(cls)s.model, %(cls)s.queryset, or override '
                '%(cls)s.get_object().' % {
                    'cls': self.__class__.__name__
                })
        return self.parent_queryset._clone()

    def get_parent_slug_field(self):
        """
        Get the name of a slug field to be used to look up by slug.
        """
        return self.parent_slug_field

    def get_parent_context_object_name(self, obj):
        """
        Get the name to use for the object.
        """
        if self.parent_context_object_name:
            return self.parent_context_object_name
        if hasattr(obj, '_meta'):
            return smart_str(obj._meta.object_name.lower())
        return None

    def get_context_data(self, **kwargs):
        context = kwargs
        context_object_name = self.get_parent_context_object_name(
            self.parent_object)
        if context_object_name:
            context[context_object_name] = self.parent_object
        return context


class BaseParentCreateView(
        ParentObjectMixin, edit.ModelFormMixin, edit.ProcessFormView):
    """
    Base view for creating an new object instance.

    Using this base class requires subclassing to provide a response mixin.
    """
    def get(self, request, *args, **kwargs):
        self.object = None
        self.parent_object = self.get_parent_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.parent_object = self.get_parent_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.parent_obj_foreign_key:
            raise AttributeError("BaseCreate can`t determine foreign "
                                 "key for linking models.")
        setattr(self.object, self.parent_obj_foreign_key, self.parent_object)
        self.object.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = kwargs
        if 'form' not in context:
            context['form'] = self.get_form()
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        if self.parent_object:
            context['parent_object'] = self.parent_object
            context_object_name = self.get_parent_context_object_name(
                self.parent_object)
            if context_object_name:
                context[context_object_name] = self.parent_object
        return context


class SubCreateView(
        edit.SingleObjectTemplateResponseMixin, BaseParentCreateView):
    template_name_suffix = '_form'
