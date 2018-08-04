from django.utils.translation import ugettext_lazy as _
from django import forms


class TimeSelectorForm(forms.Form):

    weight = forms.ChoiceField(
        required=False,
        choices=[],
        label=_(u'weight'),
    )

    period = forms.ChoiceField(
        required=False,
        choices=[],
        label=_(u'period'),
    )

    def __init__(self, period_choices, weight_choices, *args, **kwargs):
        super(TimeSelectorForm, self).__init__(*args, **kwargs)
        self.fields['period'].choices = period_choices
        self.fields['weight'].choices = weight_choices
