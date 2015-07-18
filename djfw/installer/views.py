from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.template import loader, Context
from django.contrib.admin import helpers
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse_lazy, reverse
from .models import Backup, MaintenanceLog
from .forms import AddMaintainceForm, ChangeMaintainceForm, OperationsForm 
from .maintaince import MaintainceWorker
from django.conf import settings

def download_backup(request, object_id):
    if request.user.is_anonymous():
        raise Http404()
    if not request.user.is_staff:
        raise Http404()
    backup = get_object_or_404(Backup, id=object_id)
    file_obj = open(backup.path(), 'rb')
    response = HttpResponse(file_obj, mimetype='application/x-gzip')
    response['Content-Disposition'] = 'filename=' + backup.file_name()
    return response

def on_maintaince_view(request, obj, template_name = 'installer/on_maintaince.html'):
    template = loader.get_template(template_name)
    return HttpResponse(template.render(Context({'obj': obj})), status=503)
            
class AddMaintainceView(FormView):
    template_name = 'admin/change_form.html'
    form_class = OperationsForm
    modeladmin = None
    model = MaintenanceLog
    extra_context = {}
    success_url = reverse_lazy('admin:installer_maintenancelog_changelist')
    success_url2 = reverse_lazy('admin:installer_maintenancelog_changelist')
    form_url = ''
    
    def render_to_response(self, context, **response_kwargs):
        return self.modeladmin.render_change_form(self.request, context, form_url=self.form_url, add=True)
    
    def get_admin_form(self, form):
        return helpers.AdminForm(form, [(None, {'fields': form.base_fields.keys()})], {})
    
    def get_context_data(self, **kwargs):
        model = self.model
        opts = model._meta
        form = kwargs['form']
        context = {
            'title': _('Start %s') % force_unicode(opts.verbose_name),
            'adminform': self.get_admin_form(form),
            'is_popup': "_popup" in self.request.REQUEST,
            'show_delete': False,
            'media': self.modeladmin.media,
            'inline_admin_formsets': [],
            'errors': helpers.AdminErrorList(form, []),
            'app_label': opts.app_label,
            #'opts': opts,
        }
        context.update(self.extra_context or {})
        return context
    
    def form_valid(self, form):
        opts = [key for key in form.cleaned_data.keys() if (key <> 'comment') and form.cleaned_data[key]]
        log = MaintenanceLog()
        log.status = _("Maintaince started")  if opts else _("Manual maintaince")
        log.comment = form.cleaned_data['comment']
        log.operations = opts
        log.save()
        if opts:
            MaintainceWorker(log, opts).start()
            return HttpResponseRedirect(reverse('admin:installer_maintenancelog_change', args=(log.pk,)))
        return HttpResponseRedirect(self.get_success_url())

class ChangeMaintainceView(AddMaintainceView):
    obj = None
    template_name = 'admin/change_form.html'
    form_class = ChangeMaintainceForm
    
    def get_form(self, form_class):
        self.add_js_media = []
        worker = MaintainceWorker(self.obj)
        form = worker.get_form(self.request)
        if (not form) or getattr(form, 'reload', False):
            self.add_js_media += [u'%sinstaller/reload.js' % settings.STATIC_URL]
        else:
            pass
        if not form:
            form = form_class(self.request.POST or None, self.request.FILES or None, instance=self.obj)
                
        return form
    
    def get_context_data(self, **kwargs):
        context = super(ChangeMaintainceView, self).get_context_data(**kwargs)
        media = context['media']
        media.add_js(self.add_js_media)
        context['title'] = unicode(self.obj)
        return context
    
    def form_valid(self, form):
        worker = MaintainceWorker(self.obj)
        worker.form_valid(form)
        return HttpResponseRedirect(reverse('admin:installer_maintenancelog_change', args=(self.obj.pk,)))
        #return HttpResponseRedirect(self.get_success_url())
