from django import forms
from django import urls
from django.contrib import auth

from tulius.games.models import RequestQuestion
from .models import Game, GameGuest, GameAdmin, GameWinner


User = auth.get_user_model()


class EditGameMainForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = (
            'serial_number', 'name', 'short_comment', 'status',
            'show_announcement')


class EditGameTextsForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = (
            'announcement', 'announcement_preview', 'introduction',
            'requests_text', )


class GameGuestForm(forms.models.ModelForm):
    class Meta:
        model = GameGuest
        fields = ('user',)
        widgets = {
            'user': User.autocomplete_widget,
        }


class GameAdminForm(forms.models.ModelForm):
    class Meta:
        model = GameAdmin
        fields = ('user',)
        widgets = {
            'user': User.autocomplete_widget,
        }


class GameWinnerForm(forms.models.ModelForm):
    class Meta:
        model = GameWinner
        fields = '__all__'

    def after_constuct(self, formset, params, i):
        game = params['game']
        self.fields['user'].widget.choices_url = urls.reverse(
            'games:game_edit_players', args=(game.pk,))


class EditGameRequestForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('requests_text', )


class GameRequestQuestionForm(forms.models.ModelForm):
    class Meta:
        model = RequestQuestion
        fields = '__all__'
