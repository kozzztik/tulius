from django.utils.translation import gettext_lazy as _
from django import forms

from tulius.stories.models import Role, Story
from tulius.models import User
from .models import Game


class AddGameForm(forms.ModelForm):
    class Meta:
        model = Game
        exclude = (
            'variation', 'status', 'announcement', 'announcement_preview',
            'introduction', 'requests_text', 'card_image', 'top_banner',
            'bottom_banner', 'show_announcement', 'skin', 'deleted')


class GameInviteForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        label=_('Role'),
        empty_label=None,
    )
    user = forms.ModelChoiceField(
        required=True,
        queryset=User.objects.all(),
        label=_('User'),
        widget=User.autocomplete_widget,
    )
    message = forms.CharField(
        required=False,
        label=_('Message'),
        widget=forms.Textarea,
    )

    def __init__(self, variation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = self.fields['role'].queryset.filter(
            variation=variation).exclude(deleted=True)


class GameChangeStoryForm(forms.Form):
    story = forms.ModelChoiceField(
        queryset=Story.objects.all(),
        label=_('New story'),
        required=True,
        empty_label=None,
    )


class GameUserForm(forms.Form):
    user = forms.ModelChoiceField(
        required=True,
        queryset=User.objects.all(),
        label=_('User'),
    )
