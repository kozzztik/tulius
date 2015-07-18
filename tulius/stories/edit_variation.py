from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from .models import Variation, Role, AdditionalMaterial, RoleDeleteMark 
from .edit_variation_forms import EditVariationMainForm, RoleForm, RoleTextForm, RoleDeleteForm
from .materials_views import *
from .edit_variation_catalog import *
from tulius.forum.models import Thread, Comment
from tulius.gameforum import GAMEFORUM_SITE_ID
from django.views.generic import DeleteView, DetailView
from django.db import transaction
from djfw.sortable.views import SortableDetailViewMixin
import json  
from djfw.views import RightsDetailMixin
from djfw.subviews import SubCreateView
from django.views.generic.edit import UpdateView
from tulius.games.views import MessageMixin
from .materials_forms import AdditionalMaterialForm

class VarRightsMixin(RightsDetailMixin):
    model = Variation

    def check_rights(self, obj, user):
        self.story = obj.story
        return self.story.edit_right(user)
    
    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        return super(VarRightsMixin, self).get_context_data(**kwargs)
    
class VarSubpageMixin(object):
    page_url = None
    
    def get_context_data(self, **kwargs):
        if self.page_url:
            kwargs['catalog_page'] = EditVariationSubpage(self.object, url=self.page_url)
        return super(VarSubpageMixin, self).get_context_data(**kwargs)
    
    def get_success_url(self):
        return reverse('stories:' + self.page_url, args=(self.object.pk,))
    
class VarMainView(VarRightsMixin, VarSubpageMixin, MessageMixin, UpdateView):
    template_name = 'stories/variation/main.haml'
    page_url = EDIT_VARIATION_PAGES_MAIN
    success_message = _('story was successfully updated')
    form_class = EditVariationMainForm
    
    def get_context_data(self, **kwargs):
        self.object.create_game = self.object.create_right(self.request.user)
        return super(VarMainView, self).get_context_data(**kwargs)
    
class EditVariationRoles(VarRightsMixin, VarSubpageMixin, SortableDetailViewMixin, DetailView):
    template_name='stories/variation/roles.haml'
    sortable_key = "role_"
    sortable_field = 'order'
    sortable_model = Role
    page_url = EDIT_VARIATION_PAGES_ROLES

    def get_context_data(self, **kwargs):
        context = super(EditVariationRoles, self).get_context_data(**kwargs)
        context['delete_role_form'] = RoleDeleteForm(self.object)
        return context

class VarIllustrationsView(VarRightsMixin, VarSubpageMixin, DetailView):
    template_name='stories/materials/illustrations.haml'
    page_url = EDIT_VARIATION_PAGES_ILLUSTRATIONS
    
    def get_context_data(self, **kwargs):
        kwargs['illustrations'] = Illustration.objects.filter(variation=self.object)
        return super(VarIllustrationsView, self).get_context_data(**kwargs)
        
class VarMaterialsView(VarRightsMixin, VarSubpageMixin, DetailView):
    template_name='stories/materials/materials.haml'
    page_url = EDIT_VARIATION_PAGES_MATERIALS
    
    def get_context_data(self, **kwargs):
        kwargs['materials'] = AdditionalMaterial.objects.filter(variation=self.object)
        return super(VarMaterialsView, self).get_context_data(**kwargs)

class RoleFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RoleFormMixin, self).get_form_kwargs()
        kwargs['story'] = self.story
        return kwargs
    
class AddRole(VarRightsMixin, MessageMixin, RoleFormMixin, SubCreateView):
    template_name='stories/variation/role.haml'
    parent_model = Variation
    model = Role
    form_class = RoleForm
    success_message = _('role was successfully added')
    
    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)
    
    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = CatalogPage(name=_('Add role'), 
                                             parent=EditVariationSubpage(self.parent_object, url=EDIT_VARIATION_PAGES_ROLES))
        return super(AddRole, self).get_context_data(**kwargs)
    
class AddVarMaterial(VarRightsMixin, MessageMixin, SubCreateView):
    template_name='stories/materials/material.haml'
    parent_model = Variation
    model = AdditionalMaterial
    form_class = AdditionalMaterialForm
    
    def check_parent_rights(self, obj, user):
        return self.check_rights(obj, user)
    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _("add")
        kwargs['catalog_page'] = CatalogPage(name=_("Add material"), 
                                             parent=EditVariationSubpage(self.parent_object, url=EDIT_VARIATION_PAGES_MATERIALS))
        return super(AddVarMaterial, self).get_context_data(**kwargs)
    
    def get_success_url(self):
        return reverse('stories:' + EDIT_VARIATION_PAGES_MATERIALS, args=(self.parent_object.pk,))
    
class RoleRightsMixin(RightsDetailMixin):
    def check_rights(self, obj, user):
        self.story = obj.variation.story
        return self.story.edit_right(user)
    def get_role_page(self):
        return CatalogPage(instance=self.object, 
                           parent=EditVariationSubpage(self.object.variation, url=EDIT_VARIATION_PAGES_ROLES))

class BaseRoleEdit(RoleRightsMixin, MessageMixin, UpdateView):
    model = Role
    success_message = _('role was successfully updated')
    
    def get_context_data(self, **kwargs):
        kwargs['catalog_page'] = self.get_role_page()
        return super(BaseRoleEdit, self).get_context_data(**kwargs)
    
    def get_success_url(self):
        return reverse('stories:' + EDIT_VARIATION_PAGES_ROLES, args=(self.object.variation.id,))
    
class EditRoleView(RoleFormMixin, BaseRoleEdit):
    template_name = 'stories/variation/role.haml'
    form_class = RoleForm

class EditRoleTextView(BaseRoleEdit):
    template_name = 'stories/variation/role_text.haml'
    form_class = RoleTextForm
    
class RoleTextView(RoleRightsMixin, DetailView):
    template_name='stories/variation/role_view_text.haml'
    model = Role
    
    def get_context_data(self, **kwargs):
        kwargs['story'] = self.story
        kwargs['variation'] = self.object.variation
        kwargs['catalog_page'] =  CatalogPage(name=_('text'), parent=self.get_role_page())
        return super(RoleTextView, self).get_context_data(**kwargs)
    
def get_variation(user, variation_id):
    try:
        variation_id = int(variation_id)
    except:
        raise Http404()
    variation = get_object_or_404(Variation, id=variation_id)
    story = variation.story
    if not story.edit_right(user):
        raise Http404()
    return (story, variation)
    
@login_required
def add_variation_illustration(request, variation_id):
    """
    Edit story view - Add illustration view
    """
    (story, variation) = get_variation(request.user, variation_id)
    return upload_illustration(request, None, variation, None)
            
@login_required    
def edit_variation_forum(request, variation_id):
    (story, variation) = get_variation(request.user, variation_id)
    return HttpResponseRedirect(reverse('gameforum:variation', args=(variation.pk,)))
    
@login_required
def delete_role(request, variation_id):
    success = 'error'
    error_text = ''
    try:
        variation = Variation.objects.get(id=variation_id)
    except:
        error_text = 'No such variation %s' % (variation_id,)
    if variation and (not variation.edit_right(request.user)):
        error_text = 'No rights on %s' % (variation,)
    else:
        form = RoleDeleteForm(data=request.POST or None, variation=variation)
        if form.is_valid():
            role = form.cleaned_data['role']
            message = form.cleaned_data['message']
            if role.variation == variation:
                tree_id = variation.thread.tree_id if variation.thread else None
                if tree_id:
                    threads = Thread.objects.filter(tree_id=tree_id, data1=role.id, deleted=True, plugin_id=GAMEFORUM_SITE_ID)
                    threads = [thread for thread in threads if not thread.check_deleted()]
                else:
                    threads = [] 
                if threads:
                    error_text = _("Role cant be deleted - it has threads on game forum.")
                else:
                    if tree_id:
                        comments = Comment.objects.filter(parent__tree_id=tree_id, data1=role.id, deleted=True, plugin_id=GAMEFORUM_SITE_ID)
                        comments = [comment for comment in comments if not comment.parent.check_deleted()]
                    else:
                        comments = []
                    if comments:
                        error_text = _("Role cant be deleted - it has comments on game forum.")
                    else:
                        role.deleted = True
                        delete_mark = RoleDeleteMark(role=role, user=request.user, description=message)
                        with transaction.commit_on_success():
                            role.save()
                            delete_mark.save()
                        success = 'success'
    return HttpResponse(json.dumps({'result': success, 'error_text': unicode(error_text)}))

class DeleteVariation(VarRightsMixin, DeleteView):
    template_name = 'stories/edit_story/delete_variation.haml'
    model = Variation
    
    def get_success_url(self):
        return reverse('stories:edit_story_variations', args=(self.object.story.id,))
    