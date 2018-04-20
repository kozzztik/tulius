from django import forms

from tulius.forum.models import ThreadAccessRight


class ThreadAccessRightForm(forms.ModelForm):
    class Meta:
        model = ThreadAccessRight
        fields = '__all__'

    def after_constuct(self, formset, params, i):
        if 'parent_thread' in params:
            parent_thread = params['parent_thread']
            if parent_thread and parent_thread.limited_read:
                choices = [
                    [person.id, person] for person in
                    parent_thread.limited_read_list]
                self.fields['user'].widget = forms.widgets.Select(
                    choices=choices)
