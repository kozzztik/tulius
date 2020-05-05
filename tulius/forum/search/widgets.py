from django import forms


class AutocompleteUsersWidget(forms.SelectMultiple):
    def render_options(self, choices, selected_choices):
        return ''
