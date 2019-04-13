from django import forms
from django.contrib import auth

from . import models


User = auth.get_user_model()


class EditStoryMainForm(forms.ModelForm):
    class Meta:
        model = models.Story
        fields = (
            'name', 'short_comment', 'creation_year', 'hidden', 'genres', )


class EditStoryTextsForm(forms.ModelForm):
    class Meta:
        model = models.Story
        fields = ('announcement', 'announcement_preview', 'introduction', )


class StoryAuthorForm(forms.models.ModelForm):
    class Meta:
        model = models.StoryAuthor
        fields = ('user',)
        widgets = {
            'user': User.autocomplete_widget,
        }

    def after_constuct(self, formset, params, i):
        static = params['static']
        if static:
            for field in self.fields:
                self.fields[field].widget.attrs['disabled'] = True


class StoryAdminForm(forms.models.ModelForm):
    class Meta:
        model = models.StoryAdmin
        fields = ('user', 'create_game')
        widgets = {
            'user': User.autocomplete_widget,
        }


    def after_constuct(self, formset, params, i):
        static = params['static']
        if static:
            for field in self.fields:
                self.fields[field].widget.attrs['disabled'] = True


class VariationForm(forms.ModelForm):
    class Meta:
        model = models.Variation
        fields = ('name', 'description',)


class CharacterForm(forms.ModelForm):
    class Meta:
        model = models.Character
        exclude = ('story',)

    def __init__(self, *args, story=None, **kwargs):
        super(CharacterForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].queryset = self.fields[
            'avatar'].queryset.filter(story=story)


class AvatarForm(forms.ModelForm):
    class Meta:
        model = models.Avatar
        exclude = ('image', 'story')
