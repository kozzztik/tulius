import json

from django import http
from django import shortcuts
from django import urls
from django.apps import apps
from django.views import generic
from django.contrib.auth import decorators
from django.utils.translation import ugettext_lazy as _

from djfw import subviews
from djfw import views as djfw_views
from djfw.sortable import views as sortable_views

from tulius.forum import models as forum
from tulius.games import views as games_views
from tulius.stories import models
from tulius.stories import edit_variation_forms
from tulius.stories import edit_variation_catalog as catalog
from tulius.stories import materials_forms
from tulius.stories import materials_views


GAME_FORUM_SITE_ID = apps.get_app_config('gameforum').GAME_FORUM_SITE_ID


class VarRightsMixin(djfw_views.RightsDetailMixin):
    model = models.Variation

    def check_rights(self, obj, user):
        self.story = obj.story
        return self.story.edit_right(user)

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        return super(VarRightsMixin, self).get_context_data(**kwargs)


class VarSubpageMixin:
    page_url = None

    def get_context_data(self, **kwargs):
        if self.page_url:
            kwargs['catalog_page'] = catalog.EditVariationSubpage(
                self.object, url=self.page_url)
        return super(VarSubpageMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse('stories:' + self.page_url, args=(self.object.pk,))


class VarMainView(
        VarRightsMixin, VarSubpageMixin, games_views.MessageMixin,
        generic.UpdateView):
    template_name = 'stories/variation/main.haml'
    page_url = catalog.EDIT_VARIATION_PAGES_MAIN
    success_message = _('story was successfully updated')
    form_class = edit_variation_forms.EditVariationMainForm

    def get_context_data(self, **kwargs):
        self.object.create_game = self.object.create_right(self.request.user)
        return super(VarMainView, self).get_context_data(**kwargs)


class EditVariationRoles(
        VarRightsMixin, VarSubpageMixin,
        sortable_views.SortableDetailViewMixin,
        generic.DetailView):
    template_name = 'stories/variation/roles.haml'
    sortable_key = "role_"
    sortable_field = 'order'
    sortable_model = models.Role
    page_url = catalog.EDIT_VARIATION_PAGES_ROLES

    def get_context_data(self, **kwargs):
        context = super(EditVariationRoles, self).get_context_data(**kwargs)
        context['delete_role_form'] = edit_variation_forms.RoleDeleteForm(
            self.object)
        return context


class VarIllustrationsView(
        VarRightsMixin, VarSubpageMixin, generic.DetailView):
    template_name = 'stories/materials/illustrations.haml'
    page_url = catalog.EDIT_VARIATION_PAGES_ILLUSTRATIONS

    def get_context_data(self, **kwargs):
        kwargs['illustrations'] = models.Illustration.objects.filter(
            variation=self.object)
        return super(VarIllustrationsView, self).get_context_data(**kwargs)


class VarMaterialsView(VarRightsMixin, VarSubpageMixin, generic.DetailView):
    template_name = 'stories/materials/materials.haml'
    page_url = catalog.EDIT_VARIATION_PAGES_MATERIALS

    def get_context_data(self, **kwargs):
        kwargs['materials'] = models.AdditionalMaterial.objects.filter(
            variation=self.object)
        return super(VarMaterialsView, self).get_context_data(**kwargs)


class RoleFormMixin:
    def get_form_kwargs(self):
        kwargs = super(RoleFormMixin, self).get_form_kwargs()
        kwargs['story'] = self.story
        return kwargs


class AddRole(
        VarRightsMixin, games_views.MessageMixin, RoleFormMixin,
        subviews.SubCreateView):
    template_name = 'stories/variation/role.haml'
    parent_model = models.Variation
    model = models.Role
    form_class = edit_variation_forms.RoleForm
    success_message = _('role was successfully added')

    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)

    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = catalog.CatalogPage(
            name=_('Add role'),
            parent=catalog.EditVariationSubpage(
                self.parent_object, url=catalog.EDIT_VARIATION_PAGES_ROLES))
        return super(AddRole, self).get_context_data(**kwargs)


class AddVarMaterial(
        VarRightsMixin, games_views.MessageMixin, subviews.SubCreateView):
    template_name = 'stories/materials/material.haml'
    parent_model = models.Variation
    model = models.AdditionalMaterial
    form_class = materials_forms.AdditionalMaterialForm

    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)

    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = catalog.CatalogPage(
            name=_("Add material"),
            parent=catalog.EditVariationSubpage(
                self.parent_object,
                url=catalog.EDIT_VARIATION_PAGES_MATERIALS))
        return super(AddVarMaterial, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse(
            'stories:' + catalog.EDIT_VARIATION_PAGES_MATERIALS,
            args=(self.parent_object.pk,))


class RoleRightsMixin(djfw_views.RightsDetailMixin):
    def check_rights(self, obj, user):
        self.story = obj.variation.story
        return self.story.edit_right(user)

    def get_role_page(self):
        return catalog.CatalogPage(
            instance=self.object,
            parent=catalog.EditVariationSubpage(
                self.object.variation, url=catalog.EDIT_VARIATION_PAGES_ROLES))


class BaseRoleEdit(
        RoleRightsMixin, games_views.MessageMixin, generic.UpdateView):
    model = models.Role
    success_message = _('role was successfully updated')

    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = self.get_role_page()
        return super(BaseRoleEdit, self).get_context_data(**kwargs)

    def get_success_url(self):
        return urls.reverse(
            'stories:' + catalog.EDIT_VARIATION_PAGES_ROLES,
            args=(self.object.variation.id,))


class EditRoleView(RoleFormMixin, BaseRoleEdit):
    template_name = 'stories/variation/role.haml'
    form_class = edit_variation_forms.RoleForm


class EditRoleTextView(BaseRoleEdit):
    template_name = 'stories/variation/role_text.haml'
    form_class = edit_variation_forms.RoleTextForm


class RoleTextView(RoleRightsMixin, generic.DetailView):
    template_name = 'stories/variation/role_view_text.haml'
    model = models.Role

    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        kwargs['variation'] = self.object.variation
        kwargs['catalog_page'] = catalog.CatalogPage(
            name=_('text'), parent=self.get_role_page())
        return super(RoleTextView, self).get_context_data(**kwargs)


def get_variation(user, variation_id):
    try:
        variation_id = int(variation_id)
    except:
        raise http.Http404()
    variation = shortcuts.get_object_or_404(models.Variation, id=variation_id)
    story = variation.story
    if not story.edit_right(user):
        raise http.Http404()
    return story, variation


@decorators.login_required
def add_variation_illustration(request, variation_id):
    """
    Edit story view - Add illustration view
    """
    (_, variation) = get_variation(request.user, variation_id)
    return materials_views.upload_illustration(request, None, variation, None)


@decorators.login_required
def edit_variation_forum(request, variation_id):
    (_, variation) = get_variation(request.user, variation_id)
    return http.HttpResponseRedirect(f'/play/variation/{variation.pk}/')


# pylint: disable=too-many-branches
@decorators.login_required
def delete_role(request, variation_id):
    success = 'error'
    error_text = ''
    variation = None
    try:
        variation = models.Variation.objects.get(id=variation_id)
    except:
        error_text = 'No such variation %s' % (variation_id,)
    if variation and (not variation.edit_right(request.user)):
        error_text = 'No rights on %s' % (variation,)
    else:
        form = edit_variation_forms.RoleDeleteForm(
            data=request.POST or None, variation=variation)
        if form.is_valid():
            role = form.cleaned_data['role']
            message = form.cleaned_data['message']
            if role.variation == variation:
                tree_id = (
                    variation.thread.tree_id if variation.thread else None)
                if tree_id:
                    threads = forum.Thread.objects.filter(
                        tree_id=tree_id, data1=role.id, deleted=True,
                        plugin_id=GAME_FORUM_SITE_ID)
                    threads = [
                        thread for thread in threads
                        if not thread.check_deleted()]
                else:
                    threads = []
                if threads:
                    error_text = _(
                        "Role cant be deleted - it has threads on game forum.")
                else:
                    if tree_id:
                        comments = forum.Comment.objects.filter(
                            parent__tree_id=tree_id, data1=role.id,
                            deleted=True, plugin_id=GAME_FORUM_SITE_ID)
                        comments = [
                            comment for comment in comments
                            if not comment.parent.check_deleted()]
                    else:
                        comments = []
                    if comments:
                        error_text = _(
                            "Role cant be deleted - "
                            "it has comments on game forum.")
                    else:
                        role.deleted = True
                        delete_mark = models.RoleDeleteMark(
                            role=role, user=request.user, description=message)
                        role.save()
                        delete_mark.save()
                        success = 'success'
    return http.HttpResponse(
        json.dumps({'result': success, 'error_text': str(error_text)}))


class DeleteVariation(VarRightsMixin, generic.DeleteView):
    template_name = 'stories/edit_story/delete_variation.haml'
    model = models.Variation

    def get_success_url(self):
        return urls.reverse(
            'stories:edit_story_variations',
            args=(self.object.story.id,))
