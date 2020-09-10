from django import forms
from django import urls
from django.utils import text
from django.utils.translation import gettext_lazy as _

from tulius.stories import models


EMPTY_CHOICE = ('', '---------')


class StoryFilterForm(forms.Form):

    filter_by_author = forms.ModelChoiceField(
        required=False,
        queryset=models.User.objects.all(),
        label=_(u'Author'),
    )
    filter_by_genre = forms.ModelChoiceField(
        required=False,
        queryset=models.Genre.objects.all(),
        label=_(u'Genre'),
    )
    filter_by_creation_year = forms.ChoiceField(
        required=False,
        choices=EMPTY_CHOICE + models.CREATION_YEAR_CHOICES,
        label=_(u'Creation year'),
    )

    def __init__(self, *args, **kwargs):
        super(StoryFilterForm, self).__init__(*args, **kwargs)
        self.fields['filter_by_author'].queryset = self.fields[
            'filter_by_author'].queryset.filter(
                pk__in=[
                    author['user'] for author in
                    models.StoryAuthor.objects.values('user').distinct()])
        self.fields['filter_by_author'].widget = forms.Select()
        self.fields['filter_by_author'].widget.choices = [
            EMPTY_CHOICE] + self.author_choice(
                self.fields['filter_by_author'].queryset)
        self.fields['filter_by_genre'].queryset = self.fields[
            'filter_by_genre'].queryset.filter(
                pk__in=[
                    v['genres'] for v in models.Story.objects.values(
                        'genres').distinct()])
        self.fields['filter_by_creation_year'].choices = [EMPTY_CHOICE] + [
            (v['creation_year'], v['creation_year']) for v in
            models.Story.objects.order_by('-creation_year').values(
                'creation_year').distinct()
        ]

    def author_choice(self, authors):
        author_list = []
        for author in authors:
            author_list.append((author.pk, author))
        return sorted(author_list, key=self.sorting_function)

    def sorting_function(self, value):
        authors = models.StoryAuthor.objects.filter(user=value[1])
        return authors.count()


class AddStoryForm(forms.ModelForm):
    url = urls.reverse_lazy('stories:add_story')
    caption = _('Add story')
    submit_caption = text.format_lazy(
        '<i class="icon-plus"></i> {}', _('Add story'))

    class Meta:
        model = models.Story
        fields = ('name', 'short_comment', 'creation_year', )
