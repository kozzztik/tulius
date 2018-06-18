from django.conf.urls import url
from .views import *
from .story_edit_views import *
from .edit_variation import *
from .avatar_uploads import edit_story_avatar_upload, edit_story_avatar_reload


app_name = 'tulius.stories'

urlpatterns = [
    # Story catalog
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^story/(?P<pk>\d+)/$', StoryView.as_view(), name='story'),
    url(
        r'^character_info/(?P<pk>\d+)/$',
        CharacterInfoView.as_view(), name='character_info'),
    # Edit story
    url(r'^add_story/$', AddStory.as_view(), name='add_story'),
    url(
        r'^edit_story/(?P<pk>\d+)/main/$',
        StoryMainView.as_view(), name=EDIT_STORY_PAGES_MAIN),
    url(
        r'^edit_story/(?P<pk>\d+)/texts/$',
        StoryTextsView.as_view(), name=EDIT_STORY_PAGES_TEXTS),
    url(
        r'^edit_story/(?P<pk>\d+)/users/$',
        StoryUsers.as_view(), name=EDIT_STORY_PAGES_USERS),
    url(
        r'^edit_story/(?P<pk>\d+)/graphics/$',
        StoryGraphics.as_view(), name=EDIT_STORY_PAGES_GRAPHICS),
    url(
        r'^edit_story/(?P<pk>\d+)/variations/$',
        EditStoryVariations.as_view(), name=EDIT_STORY_PAGES_VARIATIONS),
    url(
        r'^edit_story/(?P<pk>\d+)/characters/$',
        EditStoryCharacters.as_view(), name=EDIT_STORY_PAGES_CHARACTERS),
    url(
        r'^edit_story/(?P<pk>\d+)/avatars/$',
        StoryAvatarsView.as_view(), name=EDIT_STORY_PAGES_AVATARS),
    url(
        r'^edit_story/(?P<pk>\d+)/addvariation/$',
        AddVariationView.as_view(), name='add_variation'),
    url(
        r'^edit_story/(?P<pk>\d+)/addcharacter/$',
        AddCharacterView.as_view(), name='add_character'),
    url(
        r'^edit_story/(?P<pk>\d+)/illustrations/$',
        StoryIllustrationsView.as_view(), name=EDIT_STORY_PAGES_ILLUSTRATIONS),
    url(
        r'^edit_story/(?P<pk>\d+)/materials/$',
        StoryMaterialsView.as_view(), name=EDIT_STORY_PAGES_MATERIALS),
    # variation
    url(
        r'^variation/(?P<pk>\d+)/main/$',
        VarMainView.as_view(), name=EDIT_VARIATION_PAGES_MAIN),
    url(
        r'^variation/(?P<pk>\d+)/roles/$',
        EditVariationRoles.as_view(), name=EDIT_VARIATION_PAGES_ROLES),
    url(
        r'^variation/(?P<pk>\d+)/add_role/$',
        AddRole.as_view(), name='add_role'),
    url(
        r'^variation/(?P<variation_id>\d+)/forum/$',
        edit_variation_forum, name=EDIT_VARIATION_FORUM),
    url(
        r'^variation/(?P<variation_id>\d+)/delete_role/$',
        delete_role, name='delete_role'),
    url(
        r'^variation/(?P<pk>\d+)/delete/$',
        DeleteVariation.as_view(), name='delete_variation'),
    url(
        r'^variation/(?P<pk>\d+)/illustrations/',
        VarIllustrationsView.as_view(),
        name=EDIT_VARIATION_PAGES_ILLUSTRATIONS),
    url(
        r'^variation/(?P<pk>\d+)/materials/',
        VarMaterialsView.as_view(), name=EDIT_VARIATION_PAGES_MATERIALS),
    url(
        r'^variation/(?P<variation_id>\d+)/add_illustration/',
        add_variation_illustration, name='add_variation_illustration'),
    url(
        r'^variation/(?P<pk>\d+)/add_material/',
        AddVarMaterial.as_view(), name='add_variation_material'),

    url(r'^role/(?P<pk>\d+)/$', EditRoleView.as_view(), name='role'),
    url(
        r'^role/(?P<pk>\d+)/text/$',
        EditRoleTextView.as_view(), name='role_text'),
    url(
        r'^role/(?P<pk>\d+)/view_text/$',
        RoleTextView.as_view(), name='role_view_text'),
    # characters and avatars
    url(
        r'^character/(?P<pk>\d+)/$',
        CharacterView.as_view(), name='character'),
    url(r'^avatar/(?P<pk>\d+)/$', EditAvatarView.as_view(), name='avatar'),
    url(
        r'^avatar/(?P<pk>\d+)/remove/$',
        StoryDeleteAvatarView.as_view(), name='delete_avatar'),
    # illustrations and materials
    url(r'^material/(?P<pk>\d+)/$', MaterialView.as_view(), name='material'),
    url(
        r'^edit_illustration/(?P<pk>\d+)/$',
        EditIllustrationView.as_view(), name='edit_illustration'),
    url(
        r'^edit_illustration/(?P<pk>\d+)/delete/$',
        DeleteIllustrationView.as_view(), name='illustration_delete'),
    url(
        r'^edit_material/(?P<pk>\d+)/$',
        EditMaterialView.as_view(), name='edit_material'),
    url(
        r'^edit_material/(?P<pk>\d+)/delete/$',
        DeleteMaterialView.as_view(), name='material_delete'),
    url(
        r'^edit_story/(?P<pk>\d+)/add_material/$',
        AddMaterialView.as_view(), name='add_story_material'),
    # Uploads handling
    url(
        r'^illustration/(?P<illustration_id>\d+)/$',
        uploaded_illustration, name='illustration'),
    url(
        r'^illustration_thumb/(?P<illustration_id>\d+)/$',
        uploaded_illustration_thumb, name='illustration_thumb'),
    url(
        r'^edit_story/(?P<story_id>\d+)/add_illustration/$',
        add_story_illustration, name='add_story_illustration'),
    url(
        r'^edit_illustration/(?P<illustration_id>\d+)/reload/$',
        edit_illustration_reload, name='illustration_reload'),
    url(
        r'^edit_story/(?P<story_id>\d+)/avatars/upload/$',
        edit_story_avatar_upload, name='add_avatar'),
    url(
        r'^avatar/(?P<avatar_id>\d+)/reload/$',
        edit_story_avatar_reload, name='reload_avatar'),
]
