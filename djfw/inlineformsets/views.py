from django.http import HttpResponseRedirect
from .core import get_formset


class DetailFormsetsMixin:
    formsets = {}
#    formsets = {'guestsformset':
#        {'model': GameGuest, 'extra': 1, 'form': Form},
#                'adminformset': {'model': GameAdmin, 'extra': 1},
#                }
    formset_objs = {}

    def get_formsets(self):
        if self.formset_objs:
            return self.formset_objs
        for formset_name in self.formsets:
            formset_def = self.formsets[formset_name]
            model = formset_def['model']
            extra = formset_def.get('extra', None)
            form = formset_def.get('form', None)
            formset = get_formset(
                self.model,
                model,
                self.request.POST or None,
                form,
                extra=extra,
                instance=self.object)
            self.formset_objs[formset_name] = formset
        return self.formset_objs

    def get_context_data(self, **kwargs):
        context = super(DetailFormsetsMixin, self).get_context_data(**kwargs)
        context.update(self.get_formsets())
        return context

    def get_success_url(self):
        pass

    def formset_invalid(self):
        pass

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        valid = True
        for formset_name in self.formset_objs:
            formset = self.formset_objs[formset_name]
            if not formset.is_valid():
                valid = False
        if valid:
            for formset in self.formset_objs.values():
                formset.save()
            # pylint: disable=assignment-from-no-return
            url = self.get_success_url()
            if url is not None:
                return HttpResponseRedirect(url)
        else:
            self.formset_invalid()
        context.update(self.formset_objs)
        return self.render_to_response(context)
