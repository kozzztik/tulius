from tulius.stories import models
from tulius import models as tulius_models
from django.test import client as django_client


def test_story_author_counter(superuser):
    value = superuser.user.stories_author
    story = models.Story(name='counter story', creation_year=2020)
    story.save()
    client = django_client.Client()
    client.login(
        username=superuser.user.username, password=superuser.user.username)
    # add author
    base_url = f'/stories/edit_story/{story.pk}/users/?widget=authorformset'
    response = client.post(base_url + '&action=add_item', {
        'authorformset-user': superuser.user.pk,
        'authorformset-user_autocomplete': superuser.user.username})
    assert response.status_code == 200
    # check
    obj = tulius_models.User.objects.get(pk=superuser.user.pk)
    assert obj.stories_author == (value + 1)
    # delete
    obj = models.StoryAuthor.objects.get(story=story, user=superuser.user)
    response = client.post(base_url + '&action=delete_item', {
        'id': obj.pk})
    assert response.status_code == 200
    # check
    obj = tulius_models.User.objects.get(pk=superuser.user.pk)
    assert obj.stories_author == value
