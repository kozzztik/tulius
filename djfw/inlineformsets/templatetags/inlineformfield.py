from django.template import loader
from django import template

register = template.Library()


class FormFields(template.Node):
    def __init__(self, form_name, formset, head):
        self.form_name = form_name
        self.head = head
        self.formset_name = formset

    def _check_field(self, field, formset):
        if formset.static and (field.name == 'DELETE'):
            return False
        fk = getattr(formset, 'fk', None)
        if fk:
            fk = fk.name
        if field.is_hidden or (field.name == fk):
            return False
        return True

    def render(self, context):
        form = context[self.form_name]
        formset = context[self.formset_name]
        fields = [field for field in form if self._check_field(field, formset)]

        if self.head == '1':
            template_name = 'inlineheader.html'
        else:
            template_name = 'inlineform.html'
        return loader.render_to_string(
            'inlineformsets/' + template_name,
            {'fields': fields, 'form': form}
        )


@register.tag(name="inline_form_fields")
def do_form_field(parser, token):
    try:
        _, formname, formset, head = token.split_contents()
    except ValueError:
        msg = 'inline_form_fields tag requires a three arguments'
        raise template.TemplateSyntaxError(msg)
    return FormFields(formname, formset, head)
