from django.conf import urls

from tulius.stories import views
from tulius.stories import story_edit_views
from tulius.stories import edit_variation
from tulius.stories import avatar_uploads
from tulius.stories import materials_views
from tulius.stories import edit_story_cataloging as story_catalog
from tulius.stories import edit_variation_catalog as variation_catalog


app_name = 'tulius.stories'

urlpatterns = [
    # Story catalog
    urls.url(r'^$', views.IndexView.as_view(), name='index'),
    urls.url(r'^story/(?P<pk>\d+)/$', views.StoryView.as_view(), name='story'),
    urls.url(
        r'^character_info/(?P<pk>\d+)/$',
        views.CharacterInfoView.as_view(), name='character_info'),
    # Edit story
    urls.url(r'^add_story/$', views.AddStory.as_view(), name='add_story'),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/main/$',
        story_edit_views.StoryMainView.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_MAIN),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/texts/$',
        story_edit_views.StoryTextsView.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_TEXTS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/users/$',
        story_edit_views.StoryUsers.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_USERS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/graphics/$',
        story_edit_views.StoryGraphics.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_GRAPHICS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/variations/$',
        story_edit_views.EditStoryVariations.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_VARIATIONS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/characters/$',
        story_edit_views.EditStoryCharacters.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_CHARACTERS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/avatars/$',
        story_edit_views.StoryAvatarsView.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_AVATARS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/addvariation/$',
        story_edit_views.AddVariationView.as_view(), name='add_variation'),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/addcharacter/$',
        story_edit_views.AddCharacterView.as_view(), name='add_character'),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/illustrations/$',
        story_edit_views.StoryIllustrationsView.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_ILLUSTRATIONS),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/materials/$',
        story_edit_views.StoryMaterialsView.as_view(),
        name=story_catalog.EDIT_STORY_PAGES_MATERIALS),
    # variation
    urls.url(
        r'^variation/(?P<pk>\d+)/main/$',
        edit_variation.VarMainView.as_view(),
        name=variation_catalog.EDIT_VARIATION_PAGES_MAIN),
    urls.url(
        r'^variation/(?P<pk>\d+)/roles/$',
        edit_variation.EditVariationRoles.as_view(),
        name=variation_catalog.EDIT_VARIATION_PAGES_ROLES),
    urls.url(
        r'^variation/(?P<pk>\d+)/add_role/$',
        edit_variation.AddRole.as_view(), name='add_role'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/forum/$',
        edit_variation.edit_variation_forum,
        name=variation_catalog.EDIT_VARIATION_FORUM),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/delete_role/$',
        edit_variation.delete_role, name='delete_role'),
    urls.url(
        r'^variation/(?P<pk>\d+)/delete/$',
        edit_variation.DeleteVariation.as_view(), name='delete_variation'),
    urls.url(
        r'^variation/(?P<pk>\d+)/illustrations/',
        edit_variation.VarIllustrationsView.as_view(),
        name=variation_catalog.EDIT_VARIATION_PAGES_ILLUSTRATIONS),
    urls.url(
        r'^variation/(?P<pk>\d+)/materials/',
        edit_variation.VarMaterialsView.as_view(),
        name=variation_catalog.EDIT_VARIATION_PAGES_MATERIALS),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/add_illustration/',
        edit_variation.add_variation_illustration,
        name='add_variation_illustration'),
    urls.url(
        r'^variation/(?P<pk>\d+)/add_material/',
        edit_variation.AddVarMaterial.as_view(),
        name='add_variation_material'),
    urls.url(
        r'^role/(?P<pk>\d+)/$',
        edit_variation.EditRoleView.as_view(), name='role'),
    urls.url(
        r'^role/(?P<pk>\d+)/text/$',
        edit_variation.EditRoleTextView.as_view(), name='role_text'),
    urls.url(
        r'^role/(?P<pk>\d+)/view_text/$',
        edit_variation.RoleTextView.as_view(), name='role_view_text'),
    # characters and avatars
    urls.url(
        r'^character/(?P<pk>\d+)/$',
        story_edit_views.CharacterView.as_view(), name='character'),
    urls.url(
        r'^avatar/(?P<pk>\d+)/$',
        story_edit_views.EditAvatarView.as_view(), name='avatar'),
    urls.url(
        r'^avatar/(?P<pk>\d+)/remove/$',
        story_edit_views.StoryDeleteAvatarView.as_view(),
        name='delete_avatar'),
    # illustrations and materials
    urls.url(
        r'^material/(?P<pk>\d+)/$',
        views.MaterialView.as_view(), name='material'),
    urls.url(
        r'^edit_illustration/(?P<pk>\d+)/$',
        story_edit_views.EditIllustrationView.as_view(),
        name='edit_illustration'),
    urls.url(
        r'^edit_illustration/(?P<pk>\d+)/delete/$',
        story_edit_views.DeleteIllustrationView.as_view(),
        name='illustration_delete'),
    urls.url(
        r'^edit_material/(?P<pk>\d+)/$',
        story_edit_views.EditMaterialView.as_view(), name='edit_material'),
    urls.url(
        r'^edit_material/(?P<pk>\d+)/delete/$',
        story_edit_views.DeleteMaterialView.as_view(), name='material_delete'),
    urls.url(
        r'^edit_story/(?P<pk>\d+)/add_material/$',
        story_edit_views.AddMaterialView.as_view(), name='add_story_material'),
    # Uploads handling
    urls.url(
        r'^illustration/(?P<illustration_id>\d+)/$',
        materials_views.uploaded_illustration, name='illustration'),
    urls.url(
        r'^illustration_thumb/(?P<illustration_id>\d+)/$',
        materials_views.uploaded_illustration_thumb,
        name='illustration_thumb'),
    urls.url(
        r'^edit_story/(?P<story_id>\d+)/add_illustration/$',
        story_edit_views.add_story_illustration,
        name='add_story_illustration'),
    urls.url(
        r'^edit_illustration/(?P<illustration_id>\d+)/reload/$',
        views.edit_illustration_reload, name='illustration_reload'),
    urls.url(
        r'^edit_story/(?P<story_id>\d+)/avatars/upload/$',
        avatar_uploads.edit_story_avatar_upload, name='add_avatar'),
    urls.url(
        r'^avatar/(?P<avatar_id>\d+)/reload/$',
        avatar_uploads.edit_story_avatar_reload, name='reload_avatar'),
]
