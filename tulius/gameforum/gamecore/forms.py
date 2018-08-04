from django.utils.translation import ugettext_lazy as _
from django import forms


class RoleForm(forms.Form):
    role = forms.ChoiceField(label=_('Character'), choices=())

    def __init__(self, admin, roles, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        choices = []
        if admin:
            choices += [('', '-----')]
        choices += [(role.pk, str(role)) for role in roles if role]
        self.fields['role'].choices = choices
        self.fields['role'].required = not admin


class EditorForm(forms.Form):
    editor = forms.ChoiceField(label=_('Editor'), choices=())

    def __init__(self, admin, roles, *args, **kwargs):
        super(EditorForm, self).__init__(*args, **kwargs)
        choices = []
        if admin:
            choices += [('', '-----')]
        choices += [(editor.pk, str(editor)) for editor in roles if editor]
        self.fields['editor'].choices = choices
        self.fields['editor'].required = not admin
