from django import forms
from django.db.models.query_utils import Q
from django.utils.translation import ugettext_lazy as _

from .models import GameThreadRight


class GameRightForm(forms.models.ModelForm):
    class Meta:
        model = GameThreadRight
        fields = '__all__'

    def after_constuct(self, formset, params, i):
        parent_thread = params['parent_thread']
        variation = parent_thread.variation
        query = Q(variation=variation)
        if ('gameadmin' in params) and (not params['gameadmin']):
            query = query & Q(show_in_character_list=True)
        self.fields['role'].queryset = self.fields['role'].queryset.filter(
            query).exclude(deleted=True)
        if parent_thread.limited_read:
            choices = [
                [person.id, person] for person in
                parent_thread.limited_read_list]
            self.fields['role'].widget.choices = choices


class RoleForm(forms.Form):
    # role = forms.Select(choices=())
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
