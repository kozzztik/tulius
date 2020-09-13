from django.utils.translation import gettext_lazy as _
from django import forms

from tulius.models import User


class RankForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = ('rank',)


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
        required=False,
        queryset=User.objects.all(),
        label=_(u'Player'),
        widget=User.autocomplete_widget
    )

    sort_type = forms.ChoiceField(
        required=False,
        choices=PLAYERS_SORT_TYPE,
        label=_(u'sort by'),
    )
