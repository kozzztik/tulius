from django import forms
from django import urls
from django.utils.translation import ugettext_lazy as _, _string_concat
from .models import *


EMPTY_CHOICE = ('', '---------')


class StoryFilterForm(forms.Form):

    filter_by_author = forms.ModelChoiceField(
        required=False,
        queryset=User.objects.all(),
        label=_(u'Author'),
    )
    filter_by_genre = forms.ModelChoiceField(
        required=False,
        queryset=Genre.objects.all(),
        label=_(u'Genre'),
    )
    filter_by_creation_year = forms.ChoiceField(
        required=False,
        choices=(EMPTY_CHOICE) + CREATION_YEAR_CHOICES,
        label=_(u'Creation year'),
    )

    def __init__(self, *args, **kwargs):
        super(StoryFilterForm, self).__init__(*args, **kwargs)
        self.fields['filter_by_author'].queryset = self.fields[
            'filter_by_author'].queryset.filter(
                pk__in=[
                    author['user'] for author in
                    StoryAuthor.objects.values('user').distinct()]
        )
        self.fields['filter_by_author'].widget = forms.Select()
        self.fields['filter_by_author'].widget.choices = [
            EMPTY_CHOICE] + self.author_choice(
                self.fields['filter_by_author'].queryset)
        self.fields['filter_by_genre'].queryset = self.fields[
            'filter_by_genre'].queryset.filter(
                pk__in=[
                    v['genres'] for v in Story.objects.values(
                        'genres').distinct()]
        )
        self.fields['filter_by_creation_year'].choices = [EMPTY_CHOICE] + [
            (v['creation_year'], v['creation_year']) for v in
            Story.objects.order_by('-creation_year').values(
                'creation_year').distinct()
        ]
        
    def author_choice(self, authors):
        author_list = []
        for author in authors:
            author_list.append((author.pk, author))
        return sorted(author_list, key=self.sorting_function)

    def sorting_function(self, tuple):
        authors = StoryAuthor.objects.filter(user=tuple[1])
        return authors.count() 


class AddStoryForm(forms.ModelForm):
    url = urls.reverse_lazy('stories:add_story')
    caption = _('Add story')
    submit_caption = _string_concat(
        '<i class="icon-plus"></i> ', _('Add story'))

    class Meta:
        model = Story
        fields = ('name', 'short_comment', 'creation_year', )
