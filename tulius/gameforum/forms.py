from django import forms
from django.db.models.query_utils import Q

from .models import GameThreadRight


class GameRightForm(forms.models.ModelForm):
    class Meta:
        model = GameThreadRight
        fields = '__all__'

    use_required_attribute = False
    empty_permitted = True

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
