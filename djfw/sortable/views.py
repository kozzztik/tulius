from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponse
from django import forms


class SortableViewMixin:
    sortable_model = None
    sortable_key = None
    sortable_field = 'order'
    sortable_queryset = None
    login_required = False

    def get_sortable_queryset(self):
        if self.sortable_queryset is None:
            if self.sortable_model:
                return self.sortable_model._default_manager.all()
            raise ImproperlyConfigured(
                "%(cls)s is missing a sortable queryset. Define "
                "%(cls)s.sortable_model or %(cls)s.sortable_queryset." % {
                    'cls': self.__class__.__name__
                })
        return self.queryset._clone()

    def post(self, request, *args, **kwargs):
        if self.login_required and self.request.user.is_anonymous:
            raise PermissionDenied('Login required')
        items = request.POST['items']
        items = items.split(',')
        if self.sortable_key:
            items = [item.replace(self.sortable_key, '') for item in items]
        items = [int(item) for item in items]
        order = 0
        queryset = self.get_sortable_queryset()
        for item in items:
            order += 1
            queryset.filter(pk=item).update(**{self.sortable_field: order})
        return HttpResponse("{}")


class SortableDetailViewMixin(SortableViewMixin):
    sortable_fk = None

    def get_sortable_queryset(self):
        self.object = self.get_object()
        queryset = super(SortableDetailViewMixin, self).get_sortable_queryset()
        if self.sortable_model and self.model:
            fk = forms.models._get_foreign_key(
                self.model, self.sortable_model, fk_name=self.sortable_fk)
            return queryset.filter(**{fk.name: self.object.pk})
        if self.sortable_fk:
            return queryset.filter(**{self.sortable_fk: self.object.pk})
        raise ImproperlyConfigured(
            "%(cls)s is missing a sortable foreign key. Define "
            "%(cls)s.sortable_model and %(cls)s.model, or "
            "%(cls)s.sortable_fk." % {
                'cls': self.__class__.__name__
            })


class DecoratorChainingMixin:
    def dispatch(self, *args, **kwargs):
        decorators = getattr(self, 'decorators', [])
        base = super(DecoratorChainingMixin, self).dispatch

        for decorator in decorators:
            base = decorator(base)
        return base(*args, **kwargs)


class ActionableMixin:
    action_param = 'action'
#    actions = {'my_action': {'method': 'my_proc'}}

    def dispatch_action(self, action_name, **kwargs):
        method = kwargs.pop('method', action_name)
        if callable(method):
            return method(**kwargs)
        return getattr(self, method)(**kwargs)

    def post(self, request, *args, **kwargs):
        if self.action_param in request.POST:
            action_name = request.POST[self.action_param]
        else:
            action_name = request.GET[self.action_param]
        action = self.actions[action_name].copy()
        return self.dispatch_action(action_name, **action)


class ActionableFormsMixin(ActionableMixin):
    #    actions = {'my_action':
    # {'form': 'MyForm', 'context_name': 'form', 'method': 'my_proc'}}

    def create_form(self, action_name, form, *args, **kwargs):
        if form:
            return form(*args, **kwargs)
        return None

    def get_forms(self):
        forms_dict = {}
        for action_name in self.actions.keys():
            action = self.actions[action_name].copy()
            form = action.pop('form', None)
            if form:
                context_name = action.pop('context_name', action_name + '_form')
                forms_dict[context_name] = self.create_form(action_name, form)
        return forms_dict

    def get_context_data(self, **kwargs):
        context = super(ActionableMixin, self).get_context_data(**kwargs)
        context.update(self.get_forms())
        return context

    def invalid_form(self, action, form):
        return HttpResponse(str(form))

    def dispatch_action(self, action_name, **kwargs):
        if 'form' in kwargs:
            form = self.create_form(
                action_name, kwargs.pop('form'), data=self.request.POST)
            if form and not form.is_valid():
                return self.invalid_form(action_name, form)
            method = kwargs.pop('method', action_name)
            if callable(method):
                return method(form, **kwargs)
            return getattr(self, method)(form, **kwargs)
        return super(ActionableFormsMixin, self).dispatch_action(
            action_name, **kwargs)
