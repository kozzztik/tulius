from django.utils.translation import gettext_lazy as _
from django import forms

from . import models


class EditVariationMainForm(forms.ModelForm):
    class Meta:
        model = models.Variation
        fields = ('name', 'description',)


class RoleForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = (
            'character',
            'avatar',
            'name',
            'sex',
            'description',
            'show_in_character_list',
            'show_in_online_character',
            'show_trust_marks',
            'requestable'
        )

    def __init__(self, *args, **kwargs):
        story = kwargs.pop('story')
        super().__init__(*args, **kwargs)
        self.fields['avatar'].queryset = self.fields[
            'avatar'].queryset.filter(story=story)
        self.fields['character'].queryset = self.fields[
            'character'].queryset.filter(story=story)


class RoleTextForm(forms.ModelForm):
    class Meta:
        model = models.Role
        fields = ('body', )


class RoleDeleteForm(forms.Form):
    role = forms.ModelChoiceField(
        queryset=models.Role.objects.all(),
        label=_('Role'),
        empty_label=None,
    )

    message = forms.CharField(
        required=False,
        label=_('Delete message'),
        widget=forms.Textarea,
    )

    def __init__(self, variation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = self.fields[
            'role'].queryset.filter(variation=variation)
