class SampleForm(forms.Form):  
    name = forms.CharField(label=_('Name'))  
    country = forms.CharField(label=_('Country'),  
        widget=AutocompleteWidget(choices_url='autocomplete_countries', related_fields=('city',)))  
    city = forms.CharField(label=_('City),  
        widget=AutocompleteWidget(choices_url='autocomplete_cities', related_fields=('country',)))  
    sports = forms.ChoiceField(label=_('Sports'), choices=SPORTS_CHOICES,  
        widget=AutocompleteWidget(options={'minChars': 0, 'autoFill': True, 'mustMatch': True}))  
        
READ

http://djangonaut.blogspot.com/2008/05/jquery-autocompletewidget-django.html

include init.html into your head.

for ModelForms use

class GameGuestForm(forms.models.ModelForm):
    class Meta:
        model = GameGuest
        widgets = {
            'user': AutocompleteWidget(choices_url='autocomplete:user', options={'minChars': 0, 'autoFill': True, 'mustMatch': True}),
        }