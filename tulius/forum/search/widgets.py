from django.forms import SelectMultiple  

class AutocompleteUsersWidget(SelectMultiple):  
    def render_options(self, choices, selected_choices):
        return ''