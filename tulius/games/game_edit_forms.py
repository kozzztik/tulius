from django import forms
from .models import Game, GameGuest, GameAdmin, GameWinner
from tulius.games.models import RequestQuestion
from django.core.urlresolvers import reverse

class EditGameMainForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('serial_number', 'name', 'short_comment', 'status', 'show_announcement')

class EditGameTextsForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('announcement', 'announcement_preview', 'introduction', 'requests_text', )
        
class GameGuestForm(forms.models.ModelForm):
    class Meta:
        model = GameGuest

class GameAdminForm(forms.models.ModelForm):
    class Meta:
        model = GameAdmin

class GameWinnerForm(forms.models.ModelForm):
    class Meta:
        model = GameWinner

    def after_constuct(self, formset, params, i):
        game = params['game']
        self.fields['user'].widget.choices_url = reverse('games:game_edit_players', args=(game.pk,))

class EditGameRequestForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('requests_text', )

class GameRequestQuestionForm(forms.models.ModelForm):
    class Meta:
        model = RequestQuestion
