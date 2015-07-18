from django.template import RequestContext, loader
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.views.generic import FormView
from django.http import HttpResponse, Http404
import json
from django.views.generic import DetailView
from django import forms
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).get(request, *args, **kwargs);
    @method_decorator(login_required)
    
    def post(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).post(request, *args, **kwargs);

class DecoratorChainingMixin(object):
    def dispatch(self, *args, **kwargs):
        decorators = getattr(self, 'decorators', [])
        call_prepare_funcs = getattr(self, 'call_prepare_funcs', [])
        base = super(DecoratorChainingMixin, self).dispatch

        for decorator in decorators:
            base = decorator(base)
        for func in call_prepare_funcs:
            func(self, *args, **kwargs)
        return base(*args, **kwargs)
    
class RightsDetailMixin(object):
    login_required = False
    superuser_required = False
    
    def get_object(self):
        obj = super(RightsDetailMixin, self).get_object()
        user = getattr(self.request, 'user')
        if not self.check_rights(obj, user):
            raise PermissionDenied()
        return obj
    
    # return TRUE if rights is OK, False if user have no rights
    def check_rights(self, obj, user):
        if (self.login_required or self.superuser_required) and (not user.is_authenticated()):
            return False
        if self.superuser_required and (not user.is_superuser):
            return False
        return True
    
    def dispatch(self, request, *args, **kwargs):
        if (self.login_required and (not request.user.is_authenticated())):
            return redirect_to_login(request.build_absolute_uri())
        try:
            return super(RightsDetailMixin, self).dispatch(request, *args, **kwargs)
        except PermissionDenied:
            if not request.user.is_authenticated():
                return redirect_to_login(request.build_absolute_uri())
            else:
                raise
    
class RenderMixin(object):
    def render(self, **kwargs):
        context_data = self.get_context_data(**kwargs)
        context = RequestContext(self.request, context_data)
        template = self.get_template_names()
        if isinstance(template, (list, tuple)):
            t = loader.select_template(template)
        elif isinstance(template, basestring):
            t = loader.get_template(template)
        return t.render(context)
    
class AjaxFormView(RenderMixin, FormView):
    template_name = 'snippets/ajax_form.haml'
    
    def form_valid(self, form):
        return HttpResponse(json.dumps({'result': True, 'redirect': self.get_success_url()}))
    
    def form_invalid(self, form):
        return HttpResponse(json.dumps({'result': False, 'html': self.render(form=form)}))
    
class AjaxModelFormView(AjaxFormView):
    def model_setup(self, model):
        pass
    
    def get_success_url(self):
        return self.model.get_absolute_url()
    
    def form_valid(self, form):
        self.model = form.save(commit=False)
        self.model_setup(self.model)
        self.model.save()
        return HttpResponse(json.dumps({'result': True, 'redirect': self.get_success_url()}))
    
class AjaxFormsetView(RenderMixin, DetailView):
    template_name = 'snippets/ajax_formset_table.haml'
    no_parent = False
    submodel = None
    model_edit_right = True
    model_read_right = True
    fk_name = None
    form_class = None
    form_fields = None
    form_exclude = None
    base_form = forms.ModelForm
    url_name = None
    html_id = None
    
    def get_html_id(self):
        return self.html_id or self.submodel.__name__ + '_formset'
    
    def __init__(self, obj=None, request=None, **kwargs):
        super(AjaxFormsetView, self).__init__(**kwargs)
        if self.model:
            self.fk = forms.models._get_foreign_key(self.model, self.submodel, fk_name=self.fk_name)
        else:
            self.fk = None
        if (obj or self.no_parent) and request:
            self.request = request
            self.prepare(obj, request.user)

    def prepare(self, obj, user, no_items=False):
        self.object = obj
        self.url = self.get_url(obj)
        self.opts = self.submodel._meta
        self.id = self.get_html_id()
        self.edit_right = self.get_edit_right(obj, user, None)
        self.read_right = self.get_read_right(obj, user, None)
        if not self.read_right:
            raise Http404()
        if not no_items:
            self.prepare_items(obj, user)
            
    def prepare_items(self, obj, user):
        if (not self.no_parent) and self.fk:
            self.items = self.submodel.objects.filter(**{self.fk.name: obj.pk})
        else:
            self.items = self.submodel.objects.all()
        self.items = [item for item in self.items if self.get_read_right(obj, user, item)]
        for item in self.items:
            item.edit_right = self.get_edit_right(obj, user, item)
            item.html_id = self.id + '_item%s' % (item.id)
        if self.edit_right:
            self.form = self.get_form_class()(prefix=self.id)
        
    def get_url(self, obj):
        if obj:
            return reverse(self.url_name, kwargs={self.pk_url_kwarg: obj.pk})
        else:
            return reverse(self.url_name)
            
    def get_edit_right(self, obj, user, item):
        return self.model_edit_right
    
    def get_read_right(self, obj, user, item):
        return self.model_read_right
    
    def get_form_class(self):
        if self.form_class:
            return self.form_class
        exclude = self.form_exclude or []
        if self.fk and not self.fk.name in exclude:
            exclude += [self.fk.name]
        return forms.models.modelform_factory(self.submodel, form=self.base_form, fields=self.form_fields, exclude=exclude)
    
    def get(self, request, *args, **kwargs):
        self.object = None if self.no_parent else self.get_object()
        self.prepare(self.object, request.user)
        context = self.get_context_data(view=self)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        self.object = None if self.no_parent else self.get_object()
        self.prepare(self.object, request.user, no_items=True)
        if not self.edit_right:
            raise Http404()
        form_class = self.get_form_class()
        initial = {self.fk.name: self.object} if self.fk else None
        self.form = form_class(data=request.POST or None, initial=initial, prefix=self.id)
        if 'item_id' in request.POST:
            item_id = request.POST['item_id']
            try:
                item_id = int(item_id)
            except:
                raise Http404()
            query = {'pk': item_id}
            if self.object:
                query[self.fk.name] = self.object
            item = get_object_or_404(self.submodel, **query)
            if not self.get_edit_right(self.object, self.request.user, item):
                raise Http404()
            item.delete()
        else:
            if self.form.is_valid():
                item = self.form.save(commit=False)
                if self.fk:
                    setattr(item, self.fk.name, self.object)
                item.save()
        self.prepare_items(self.object, request.user)
        context = self.get_context_data(view=self)
        return self.render_to_response(context)
    
    def __unicode__(self):
        return self.render(view=self)
