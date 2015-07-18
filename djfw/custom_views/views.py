from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.template import loader, Context
from django.http import HttpResponse, Http404
from django import forms
from httplib import HTTPResponse

class SortableViewMixin(object):
    class Meta:
        static_js = ['sortable/sortable.js']
        
    sortable_model = None
    sortable_key = None
    sortable_field = 'order'
    sortable_queryset = None
    login_required = False

    def get_sortable_queryset(self):
        if self.sortable_queryset is None:
            if self.sortable_model:
                return self.sortable_model._default_manager.all()
            else:
                raise ImproperlyConfigured(u"%(cls)s is missing a sortable queryset. Define "
                                           u"%(cls)s.sortable_model or %(cls)s.sortable_queryset." % {
                                                'cls': self.__class__.__name__
                                        })
        return self.queryset._clone()
    
    def post(self, request, *args, **kwargs):
        if self.login_required and self.request.user.is_anonymous():
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
            fk = forms.models._get_foreign_key(self.model, self.sortable_model, fk_name=self.sortable_fk)
            return queryset.filter(**{fk.name: self.object.pk})
        elif self.sortable_fk:
            return queryset.filter(**{self.sortable_fk: self.object.pk})
        else:
            raise ImproperlyConfigured(u"%(cls)s is missing a sortable foreign key. Define "
                                       u"%(cls)s.sortable_model and %(cls)s.model, or %(cls)s.sortable_fk." % {
                                            'cls': self.__class__.__name__
                                    })

class DecoratorChainingMixin(object):
    def dispatch(self, *args, **kwargs):
        decorators = getattr(self, 'decorators', [])
        base = super(DecoratorChainingMixin, self).dispatch

        for decorator in decorators:
            base = decorator(base)
        return base(*args, **kwargs)
    
class ActionableBase(object):
    class Meta:
        static_js = []
        static_css = []
        media_js = []
        media_css = []
        
    action_param = 'action'
#    actions = {'my_action': {'method': 'my_proc'}}
    
    def dispatch_action(self, action_name, **kwargs):
        method = kwargs.pop('method', action_name)
        if callable(method):
            return method(**kwargs)
        else:
            return getattr(self, method)(**kwargs)
        
    def post(self, request, *args, **kwargs):
        if not self.get_post_right():
            raise PermissionDenied()
        if self.action_param in request.POST:
            action_name = request.POST[self.action_param]
        else:
            action_name = request.GET[self.action_param]
        action = self.actions[action_name].copy()
        return self.dispatch_action(action_name, **action)

    def get_read_right(self, **kwargs):
        return True

    def get_post_right(self, **kwargs):
        return self.get_read_right(**kwargs)

#    def __new__(cls, name, bases, attrs):
#        super_new = super(ActionableBase, cls).__new__
#        metas = [getattr(b, 'Meta', None) for b in bases]
#        metas = [meta for meta in metas if meta]
#        static_js_list = []
#        static_css_list = []
#        media_js_list = []
#        media_css_list = []
#        for meta in metas:
#            static_js = getattr(meta, 'static_js', None)
#            static_css = getattr(meta, 'static_css', None)
#            media_js = getattr(meta, 'media_js', None)
#            media_css = getattr(meta, 'media_css', None)
#            if static_js:
#                static_js_list += static_js
#            if static_css:
#                static_css_list += static_css
#            if media_js:
#                media_js_list += media_js
#            if media_css:
#                media_css_list += media_css
#        from django.conf import settings
#        static_url = settings.STATIC_URL
#        media_url = settings.MEDIA_URL
#        static_js_list = [static_url + url for url in static_js_list]
#        static_css_list = [static_url + url for url in static_css_list]
#        media_js_list = [media_url + url for url in media_js_list]
#        media_css_list = [media_url + url for url in media_css_list]
#        obj = super_new(cls, name, bases, attrs)
#        meta = getattr(obj, 'Meta')
#        meta.js = static_js_list + media_js_list
#        meta.css = static_css_list + media_css_list
#        obj._meta = meta
#        return obj

class ActionableViewMixin(ActionableBase):
#    widgets = {'my_widget': {'class': MyWidget}}
    widgets_param = 'widget'
    def __init__(self, *args, **kwargs):
        super(ActionableViewMixin, self).__init__(*args, **kwargs)
        widgets_list = {}
        for widget_name in self.widgets.keys():
            widget_data = self.widgets[widget_name].copy()
            widget_class = widget_data.pop('class')
            widgets_list[widget_name] = widget_class(self, widget_name, **widget_data)
        self.widgets_list = widgets_list
        
    def get_context_data(self, **kwargs):
        context = super(ActionableViewMixin, self).get_context_data(**kwargs)
        context['view'] = self
        return context
        
    def get_css_list(self):
        return self._meta.css
    
    def get_js_list(self):
        return self._meta.js

    def get_media(self):
        media = ''
        for css in self.get_css_list():
            media += '<link rel="stylesheet" type="text/css" href="%s" />\r\n' % css
        for js in self.get_js_list():
            media += '<script type="text/javascript" src="%s"></script>\r\n' % js
        return media

    def get(self, request, *args, **kwargs):
        if not self.get_read_right():
            raise PermissionDenied()
        return super(ActionableViewMixin, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if self.widgets_param in request.POST:
            widget_name = request.POST[self.widgets_param]
        else:
            widget_name = request.GET.get(self.widgets_param, None)
        if widget_name:
            widget = self.widgets_list[widget_name]
            return widget.post(request, *args, **kwargs)
        else:
            return super(ActionableViewMixin, self).post(request, *args, **kwargs)
        
    def __getitem__(self, key):
        return self.widgets_list[key]
    
    def __iter__(self):
        for name in self.widgets_list:
            yield self[name]
    
class WidgetBase(ActionableBase):
    view = None
    name = ''
    
    def __init__(self, view, name, **kwargs):
        self.view = view
        self.name = name
        cls = self.__class__
        for key, value in kwargs.iteritems():
            if not hasattr(cls, key):
                raise TypeError(u"%s() received an invalid keyword %r" % (cls.__name__, key))
            setattr(self, key, value)

    def get_read_right(self, **kwargs):
        return self.view.get_read_right(widget=self, widget_name=self.name)

    def get_post_right(self, **kwargs):
        return self.view.get_post_right(widget=self, widget_name=self.name)
    
class TemplatedWidget(WidgetBase):
    template_name = ''
    widget_context_name = ''
    
    def get_context_data(self):
        context_name = self.widget_context_name or 'widget'
        return {context_name: self}
    
    def get_template_name(self):
        return self.template_name
    
    def __unicode__(self):
        if not self.get_read_right():
            return ''
        c = Context(self.get_context_data())
        t = loader.get_template(self.get_template_name())
        return t.render(c)

class FormWidget(TemplatedWidget):
    class Meta:
        static_js = ['']
    form_class = None
    context_name = ''
    valid_template = ''
    action = ''
    valid_action = ''
    invalid_action = ''
    css_class = ''
    template_name = 'custom_views/form.html'
    button_name = 'Send'
    
    def __init__(self, *args, **kwargs):
        super(FormWidget, self).__init__(*args, **kwargs)
        self.form = self.form_class(self.request.POST or None)
        
    def get_context_data(self):
        context = super(FormWidget, self).get_context_data()
        context_name = self.context_name or 'form'
        context[context_name] = self.form
        return context
    
    def post(self, request, *args, **kwargs):
        if not self.get_post_right():
            raise PermissionDenied()
        form = self.form_class(data=self.request.POST)
        if self.action:
            action = getattr(self.view, self.action)
            return action(form)
        if form.is_valid():
            if self.valid_action:
                action = getattr(self.view, self.action)
                return action(form)
            return self.valid_form(form)
        else:
            if self.invalid_action:
                action = getattr(self.view, self.action)
                return action(form)
            return self.invalid_form(form)
    
    def valid_form(self, form):
        if self.valid_template:
            c = Context(self.get_context_data())
            t = loader.get_template(self.get_template_name())
            template = t.render(c)
        else:
            template = self.__unicode__()
        return HTTPResponse(template)
     
    def invalid_form(self, form):
        return HTTPResponse(self.__unicode__())
    
class TwitterFormWidget(FormWidget):
    template_name = 'custom_views/twitter_form.html'
    
from django.forms.models import fields_for_model, modelform_factory

class FormsetWidget(TemplatedWidget):
    template_name = 'custom_views/formset.html'
    model = None
    actions = {'add_item': {'method': 'add_item'}, 'delete_item': {'method': 'delete_item'}}
    form_class = None
    fk = ''
    queryset = None
    fields = None # ['field1']
    exclude_fields = None # ['field2']
    form_initials = None # {'field1': 1}
    prefix = ''
    table_class = ''
    editable = True
    
    def __init__(self, *args, **kwargs):
        super(FormsetWidget, self).__init__(*args, **kwargs)
        
    def get_editable(self):
        print 'try2'
        if callable(self.editable):
            return self.editable(self.view)
        else:
            return self.editable
            
    def get_parent_object(self):
        if hasattr(self, 'obj'):
            return self.obj
        obj = getattr(self.view, 'object', None)
        if not obj:
            method = getattr(self.view, 'get_object', None)
            if method:
                obj = method()
            else:
                return self.model._default_manager.all()
        self.obj = obj
        if not self.fk:
            fk = forms.models._get_foreign_key(obj.__class__, self.model)
            self.fk = fk.name
        return self.obj
    
    def get_queryset(self):
        if self.queryset:
            return self.queryset
        obj = self.get_parent_object()
        exclude = self.exclude_fields or []
        exclude = list(exclude)
        if not self.fk in exclude:
            self.exclude_fields = exclude + [self.fk]
        self.queryset = self.model._default_manager.filter(**{self.fk: obj})
        return self.queryset
        
    def get_context_data(self):
        context = super(FormsetWidget, self).get_context_data()
        self.formset = self.prepare_formset()
        self.editable = self.get_editable()
        if not hasattr(self, 'form'):
            self.form = self.get_formclass()(initial=self.form_initials, prefix=self.name)
        return context
    
    def add_item(self):
        if not self.get_editable():
            raise PermissionDenied()
        form = self.get_formclass()(data=self.view.request.POST, initial=self.form_initials, prefix=self.name)
        if form.is_valid():
            obj = form.save(commit=False)
            parent = self.get_parent_object()
            if self.fk:
                setattr(obj, self.fk, parent)
            obj.save()
        else:
            self.form = form
        return HttpResponse(unicode(self))
    
    def delete_item(self):
        if not self.get_editable():
            raise PermissionDenied()
        pk = self.view.request.POST['id']
        self.get_queryset().filter(pk=pk).delete()
        return HttpResponse("{}")
    
    def get_formfield_callback(self):
        return None
    
    def get_formfield(self, obj, name, formfield):
        display = getattr(obj, 'get_' + name + '_display', None)
        if display:
            return unicode(display())
        return unicode(getattr(obj, name, ''))
    
    def prepare_formset(self):
        formset = []
        queryset = self.get_queryset()
        model = queryset.model
        fields =  fields_for_model(model, self.fields, self.exclude_fields, None, self.get_formfield_callback())
        for obj in queryset:
            form = {'obj': obj}
            form_fields = []
            for field in fields.keys():
                form_fields += [{'name': field, 'value': self.get_formfield(obj, field, fields[field])}]
            form['fields'] = form_fields
            formset += [form]
        formset_fields = []
        for field_name in fields.keys():
            for field in model._meta.fields:
                if field.name == field_name:
                    formset_fields += [field]
                    break
        formset = {'fields': formset_fields, 'model': model, 'forms': formset}
        return formset
    
    def get_formclass(self):
        if not self.form_class:
            model = self.get_queryset().model
            self.form_class = modelform_factory(model, fields=self.fields, exclude=self.exclude_fields)
        return self.form_class