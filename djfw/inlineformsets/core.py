from django.forms.formsets import DEFAULT_MAX_NUM
from django.template import loader
from django.conf import settings
from django import forms

class InlineFormset(forms.models.BaseInlineFormSet):
    def __init__(self, data=None, instance=None, queryset=None,
                    errorclass='help-inline', tableclass='', params=None, static=False, **kwargs):
        self.error_class = errorclass
        self.table_class = tableclass
        if not tableclass:
            self.tableclass = getattr(settings, 'INLINE_FORMSET_CLASS', '')
        self.params = params
        self.static = static
        self.dinamic = not static
        super(InlineFormset, self).__init__(data, None, instance, None, None, queryset, **kwargs)
                 
    def _after_form_constuct(self, form, i):
        proc = getattr(form, 'after_constuct', None)
        if proc and callable(proc):
            proc(self, self.params, i)
        
    def _construct_form(self, i, **kwargs):
        form = super(InlineFormset, self)._construct_form(i, **kwargs)
        self._after_form_constuct(form, i)
        return form
        
    def __unicode__(self):
        if self.instance:
            pk = self.instance.pk
        else:
            pk = None
        form = self.form(initial={self.fk.name: pk })
        self._after_form_constuct(form, None)
        return loader.render_to_string('inlineformsets/inlineformset.html', 
            {'formset': self, 'template': form, 'error_class': self.error_class})

class SimpleFormset(forms.models.BaseModelFormSet):
    def __init__(self, data=None, queryset=None,
                    errorclass='help-inline', tableclass='', params=None, static=False, **kwargs):
        self.error_class = errorclass
        self.tableclass = tableclass
        if not tableclass:
            self.tableclass = getattr(settings, 'INLINE_FORMSET_CLASS', '')
        self.params = params
        self.static = static
        self.dinamic = not static
        super(SimpleFormset, self).__init__(data=data, queryset=queryset, **kwargs)
                 
    def _after_form_constuct(self, form, i):
        proc = getattr(form, 'after_constuct', None)
        if proc and callable(proc):
            proc(self, self.params, i)
            
    def _construct_form(self, i, **kwargs):
        form = super(SimpleFormset, self)._construct_form(i, **kwargs)
        self._after_form_constuct(form, i)
        return form
        
    def __unicode__(self):
        form = self.form()
        self._after_form_constuct(form, None)
        return loader.render_to_string('inlineformsets/inlineformset.html', 
            {'formset': self, 'template': form, 'error_class': self.error_class})
    

    def get_default_prefix(self):
        model = getattr(self, 'model', None)
        if model:
            return model._meta.object_name.lower() + '_form'
        else:
            return ''
                
    
def get_formset_factory(parent_model, model, form=None, fk_name=None,
                          fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, 
                          formfield_callback=None, params=None, base_form=forms.ModelForm):
    if parent_model:
        fk = forms.models._get_foreign_key(parent_model, model, fk_name=fk_name)
        # enforce a max_num=1 when the foreign key to the parent model is unique.
        if fk.unique:
            max_num = 1
    else:
        fk = None
    if not form:
        form = forms.models.modelform_factory(model, form=base_form, fields=fields, exclude=exclude, 
            formfield_callback=formfield_callback)
    if max_num is None:
        max_num = DEFAULT_MAX_NUM
    # hard limit on forms instantiated, to prevent memory-exhaustion attacks
    # limit defaults to DEFAULT_MAX_NUM, but developer can increase it via max_num
    absolute_max = max(DEFAULT_MAX_NUM, max_num)

    attrs = {'form': form, 'extra': extra,
             'can_order': can_order, 'can_delete': can_delete,
             'min_num': 1,
             'max_num': max_num,
             'params': params, 'absolute_max': absolute_max}
    if fk:
        FormSet = type(form.__name__ + 'FormSet', (InlineFormset,), attrs)
        FormSet.model = model
        FormSet.fk = fk
    else:
        FormSet = type(form.__name__ + 'FormSet', (SimpleFormset,), attrs)
        FormSet.model = model
    FormSet.validate_max = 100
    return FormSet

def get_formset(parent_model, model, data, form=None, fk_name=None,
                          fields=None, exclude=None, extra=3, can_order=False, can_delete=True, 
                          max_num=None, instance=None, formfield_callback=None, params=None, static=False, queryset=None,
                          base_form=forms.ModelForm):
    factory = get_formset_factory(parent_model, model, form, fk_name, fields, exclude,
                          extra, can_order, can_delete, max_num, formfield_callback, params, base_form=base_form)
    if instance:
        return factory(data or None, instance=instance, params=params, static=static, queryset=queryset)
    else:
        return factory(data or None, params=params, static=static, queryset=queryset)