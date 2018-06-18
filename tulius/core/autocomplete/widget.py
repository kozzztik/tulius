import json

from django import urls
from django.forms import HiddenInput, TextInput
from django.utils.safestring import mark_safe


class AutocompleteWidget(TextInput):  
        class Media:
            css = {'all': ('autocomplete/css/jquery-ui-1.8.21.custom.css',)}
            js = (
                'autocomplete/jquery-1.7.2.min.js',
                'autocomplete/jquery-ui-1.8.21.custom.min.js',
                'autocomplete/autocomplete-select.js')
        """ 
        Autocomplete widget to use with jquery-autocomplete plugin. 
     
        Widget can use for static and dynamic (AJAX-liked) data. Also 
        you can relate some fields and it's values'll posted to autocomplete 
        view. 
     
        Widget support all jquery-autocomplete options that dumped to 
        JavaScript via django.utils.simplejson. 
     
        **Note** You must init one of ``choices`` or ``choices_url`` attribute. 
        Else widget raises TypeError when rendering. 
        """  
        def __init__(
                self, model, token, attrs=None, options=None,
                related_fields=None):
            """ 
            Optional arguments: 
            ------------------- 
                 
                * ``choices`` - Static autocomplete choices (similar to choices 
                used in Select widget). 
                 
                * ``choices_url`` - Path to autocomplete view or autocomplete 
                url name. 
                 
                * ``options`` - jQuery autocomplete plugin options. Auto dumped 
                to JavaScript via SimpleJSON 
                 
                * ``related_fields`` - Fields that relates to current (value 
                of this field will sended to autocomplete view via POST) 
            """  
            self.attrs = attrs or {}  
            self.options = options or {}  
            self.token = token
            self.model = model
            
            if related_fields:  
                extra = {}  
                if isinstance(related_fields, str):  
                    related_fields = list(related_fields)  
                    
                for field in related_fields:  
                    extra[field] = "%s_value" % field  
                    
                self.extra = extra
            else:
                self.extra = {}  
        
        def render(self, name, value=None, attrs=None):              
            self.choices_url = urls.reverse(
                'autocomplete:autocomplete', args=[self.token])
            choices = ''  
            final_attrs = self.build_attrs(attrs)  
            try:  
                choices = urls.reverse(str(self.choices_url))
            except urls.NoReverseMatch:
                choices = self.choices_url
            choices = u"""function(request, response){
                $.ajax({
                    url: "%s",
                    data: {q: request.term},
                    success: function(data) {
                        if (data != 'CACHE_MISS')
                        {
                            response($.map(data, function(item) {
                                return {
                                    label: item[1],
                                    value: item[1],
                                    real_value: item[0]
                                };
                            }));
                        }
                    },
                    dataType: "json"
                });
            }""" % (choices,)
            self.options['source'] = choices
            self.options['select'] = (
                'function(event, ui)' 
                ' { $(this).autocomplete_select(event, ui); }')
            self.options['change'] = (
                'function(event, ui) ' +
                '{ $(this).autocomplete_change(event, ui); }')
            self.options['appendTo'] = '#' + name + '_autocomplete'
            html_code = HiddenInput().render(
                name, value=value, attrs={'id': attrs['id']})
            if self.options or self.extra:  
                if 'extraParams' in self.options:  
                    self.options['extraParams'].update(self.extra)  
                else:  
                    self.options['extraParams'] = self.extra  
                    
                # options = simplejson.dumps(
                #  self.options, indent=4, sort_keys=True)
                options = ''
                for k, v in self.options.items():
                    if options:
                        options += ','
                    v = str(v)
                    if (v[:8] != 'function') and (v[:1] != '{'):
                        v = '"%s"' % (v,)
                    options += "\n            %s: %s" % (k, v)
                extra = []  
                
                for k, v in self.extra.items():  
                    options = options.replace(json.dumps(v), v)
                    extra.append(
                        u"function %s() { return $('#id_%s').val(); }\n" % (
                            v, k))
                    
                extra = u''.join(extra)  
            else:  
                extra, options = '', ''  
            attrs['id'] = attrs['id'] + '_autocomplete'
            if value:
                obj = self.model.objects.get(pk=value)
                value = str(obj)
            html_code += super(AutocompleteWidget, self).render(
                name + '_autocomplete', value, attrs)
            
            html_code += u""" 
    <script type="text/javascript">
        $(document).ready(function() {
            %s$("input[id$='%s_autocomplete']").autocomplete({%s
            }); 
        });
    </script> 
    """ % (extra, final_attrs['id'], options)  
      
            return mark_safe(html_code)
