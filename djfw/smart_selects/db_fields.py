from django.db.models.fields.related import ForeignKey, RECURSIVE_RELATIONSHIP_CONSTANT, ManyToManyField
import form_fields
try:
    from south.modelsinspector import add_introspection_rules
    has_south = True
except:
    has_south = False


class ChainedForeignKey(ForeignKey):
    """
    chains the choices of a previous combo box with this one
    """
    def __init__(self, to, chained_field=None, chained_model_field=None, show_all=False, auto_choose=False, **kwargs):
        ForeignKey.__init__(self, to, **kwargs)
        
        self.chain_field = chained_field
        self.model_field = chained_model_field
        self.show_all = show_all
        self.auto_choose = auto_choose
        
        if isinstance(to, basestring):
            if to ==RECURSIVE_RELATIONSHIP_CONSTANT:
                raise ValueError("'%s' is unfortunately not supported by ChainedForeignKey. Use app_name.ModelName instead" % (RECURSIVE_RELATIONSHIP_CONSTANT,))
            else:
                self.app_name, self.model_name = to.split('.')
        else:
            self.app_name = to._meta.app_label
            self.model_name = to._meta.object_name        

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.ChainedModelChoiceField,
            'queryset': self.rel.to._default_manager.complex_filter(self.rel.limit_choices_to),
            'to_field_name': self.rel.field_name,
            'app_name': self.app_name,
            'model_name': self.model_name,
            'chain_field': self.chain_field,
            'model_field': self.model_field,
            'show_all':self.show_all,
            'auto_choose':self.auto_choose,
        }
        defaults.update(kwargs)
        return super(ChainedForeignKey, self).formfield(**defaults)



class GroupedForeignKey(ForeignKey):
    """
    Opt Grouped Field
    """
    def __init__(self, to, group_field, **kwargs):
        self.group_field = group_field
        self._choices = True
        ForeignKey.__init__(self, to, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.GroupedModelSelect,
            'queryset': self.rel.to._default_manager.complex_filter(
                                                    self.rel.limit_choices_to),
            'to_field_name': self.rel.field_name,
            'order_field': self.group_field,
        }
        defaults.update(kwargs)
        return super(ForeignKey, self).formfield(**defaults)


class ChainedManyToManyField(ManyToManyField):
    """
    chains the choices of a previous combo box with this one. mulitiselect variation
    """
    def __init__(self, to, chained_field=None, chained_model_field=None, show_all=False, auto_choose=False, **kwargs):
        ManyToManyField.__init__(self, to, **kwargs)
        
        self.chain_field = chained_field
        self.model_field = chained_model_field
        self.show_all = show_all
        self.auto_choose = auto_choose
        
        if isinstance(to, basestring):
            if to ==RECURSIVE_RELATIONSHIP_CONSTANT:
                raise ValueError("'%s' is unfortunately not supported by ChainedForeignKey. Use app_name.ModelName instead" % (RECURSIVE_RELATIONSHIP_CONSTANT,))
            else:
                self.app_name, self.model_name = to.split('.')
        else:
            self.app_name = to._meta.app_label
            self.model_name = to._meta.object_name        

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.ChainedModelMultipleChoiceField,
            'queryset': self.rel.to._default_manager.complex_filter(self.rel.limit_choices_to),
            #'to_field_name': self.rel.field_name,
            'app_name': self.app_name,
            'model_name': self.model_name,
            'chain_field': self.chain_field,
            'model_field': self.model_field,
            'show_all':self.show_all,
            'auto_choose':self.auto_choose,
        }
        defaults.update(kwargs)
        return super(ChainedManyToManyField, self).formfield(**defaults)


if has_south:
    rules_grouped = [(
        (GroupedForeignKey,),
        [],
        {
            'to': ['rel.to', {}],
            'group_field': ['group_field', {}],
        },
    )]

    add_introspection_rules([], ["^smart_selects\.db_fields\.ChainedForeignKey"])
    add_introspection_rules([], ["^smart_selects\.db_fields\.ChainedManyToManyField"])
    add_introspection_rules(rules_grouped, ["^smart_selects\.db_fields\.GroupedForeignKey"])


