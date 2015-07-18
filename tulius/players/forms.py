from django.utils.translation import ugettext_lazy as _
from django import forms
from django.contrib import auth
from pm.models import PrivateMessage
from tulius.models import User

class RankForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = ('rank',)
        
class ProfileSettingsForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = ('sex', 'icq', 'skype', 'show_played_games', 'show_played_characters', 'game_inline', 'animation_speed')

class PersonalSettingsForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = ('hide_trustmarks', 'show_online_status', 'compact_text', 'signature')

class SendMessageForm(forms.models.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ('body',)
    
class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        required = False,
        label = _(u'Email'),
    )
    new_pass = forms.CharField(
        required = False,
        label = _(u'New password'),
        widget= forms.PasswordInput
    )
    repeat_pass = forms.CharField(
        required = False,
        label = _(u'Repeat password'),
        widget= forms.PasswordInput
    )
    current_pass = forms.CharField(
        required = False,
        label = _(u'Current password'),
        widget= forms.PasswordInput
    )
    
    def clean_current_pass(self):
        current_pass = self.cleaned_data['current_pass']
        email = self.cleaned_data['email']
        new_pass = self.cleaned_data['new_pass']
        if (email <> self.user.email) or (new_pass):
            if not current_pass:
                raise forms.ValidationError(_("You need current password to change this settings"))
            user = auth.authenticate(username=self.user.username, password=current_pass)
            if not user:
                raise forms.ValidationError(_("Invalid password"))
            if new_pass:
                self.change_pass = True
            if email <> self.user.email:
                self.change_email = True
        return current_pass
    
    def clean_repeat_pass(self):
        new_pass = self.cleaned_data['new_pass']
        repeat_pass = self.cleaned_data['repeat_pass']
        if new_pass or repeat_pass:
            if new_pass <> repeat_pass:
                raise forms.ValidationError(_("Passwords don`t match"))
        return repeat_pass
    
    def __init__(self, user, data):
        self.user = user
        self.change_email = False
        self.change_pass = False
        super(ChangeEmailForm, self).__init__(data=data or None, initial={'email': user.email})
        
PLAYERS_SORT_STORIES_AUTHORED = 0
PLAYERS_SORT_GAMES_PLAYED_INC = 1
PLAYERS_SORT_GAMES_PLAYED_DEC = 2
PLAYERS_SORT_REG_DATE = 3
PLAYERS_SORT_ALPH = 4

PLAYERS_SORT_TYPE = (
    (PLAYERS_SORT_STORIES_AUTHORED, _("stories count")),
    (PLAYERS_SORT_GAMES_PLAYED_INC, _("games played count increasing")),
    (PLAYERS_SORT_GAMES_PLAYED_DEC, _("games played count decreasing")),
    (PLAYERS_SORT_REG_DATE, _("registration date")),
    (PLAYERS_SORT_ALPH, _("alphabetical")),
    )

class PlayersFilterForm(forms.Form):

    filter_by_player = forms.ModelChoiceField(
        required = False,
        queryset = User.objects.all(),
        label = _(u'Player'),
    )

    sort_type = forms.ChoiceField(
        required = False,
        choices = PLAYERS_SORT_TYPE,
        label = _(u'sort by'),
    )

class NotificationForm(forms.Form):
    enabled = forms.BooleanField(
        required = False,
        label = _(u'enabled'),
    )
