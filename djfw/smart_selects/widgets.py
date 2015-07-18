import django
from django.conf import settings
from django.forms.widgets import Select, SelectMultiple
from django.core.urlresolvers import reverse
from django.utils.encoding import iri_to_uri
from django.utils.safestring import mark_safe
from django.db.models import get_model
import locale
from django.forms.util import flatatt
from smart_selects.utils import unicode_sorter
from django.utils.encoding import StrAndUnicode, force_unicode
from itertools import chain
from django.utils.html import escape, conditional_escape


if django.VERSION >= (1, 2, 0) and getattr(settings,
		'USE_DJANGO_JQUERY', True):
	USE_DJANGO_JQUERY = True
else:
	USE_DJANGO_JQUERY = False
	JQUERY_URL = getattr(settings, 'JQUERY_URL', 'http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js')


class ChainedSelect(Select):
	def __init__(self, app_name, model_name, chain_field, model_field, show_all, auto_choose, manager=None, *args, **kwargs):
		self.app_name = app_name
		self.model_name = model_name
		self.chain_field = chain_field
		self.model_field = model_field
		self.show_all = show_all
		self.auto_choose = auto_choose
		self.manager = manager
		super(Select, self).__init__(*args, **kwargs)

	class Media:
		if USE_DJANGO_JQUERY:
			js = ["%s%s" % (settings.ADMIN_MEDIA_PREFIX, i) for i in
					('js/jquery.min.js', 'js/jquery.init.js')]
		elif JQUERY_URL:
			js = (
				JQUERY_URL,
			)

	def render(self, name, value, attrs=None, choices=()):

		if len(name.split('-')) > 1: # formset
			chain_field = '-'.join(name.split('-')[:-1] + [self.chain_field])
		else:
			chain_field = self.chain_field

		chain_field_is_complex = (len(chain_field.split('__')) > 1)
		chain_field_original = chain_field
		chain_field = chain_field.split('__')[0]

		if self.show_all:
			view_name = "chained_filter_all"
		else:
			view_name = "chained_filter"
		kwargs = {'app':self.app_name, 'model':self.model_name, 'field':self.model_field, 'value':"1"}
		if self.manager is not None:
			kwargs.update({'manager': self.manager})
		url = "/".join(reverse(view_name, kwargs=kwargs).split("/")[:-2])
		if self.auto_choose:
			auto_choose = 'true'
		else:
			auto_choose = 'false'
		empty_label = iter(self.choices).next()[1] # Hacky way to getting the correct empty_label from the field instead of a hardcoded '--------'
		js = """
		<script type="text/javascript">
		//<![CDATA[
		(function($) {
			function fireEvent(element,event){
				if (document.createEventObject){
				// dispatch for IE
				var evt = document.createEventObject();
				return element.fireEvent('on'+event,evt)
				}
				else{
				// dispatch for firefox + others
				var evt = document.createEvent("HTMLEvents");
				evt.initEvent(event, true, true ); // event type,bubbling,cancelable
				return !element.dispatchEvent(evt);
				}
			}

			function dismissRelatedLookupPopup(win, chosenId) {
				var name = windowname_to_id(win.name);
				var elem = document.getElementById(name);
				if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
					elem.value += ',' + chosenId;
				} else {
					elem.value = chosenId;
				}
				fireEvent(elem, 'change');
				win.close();
			}

			$(document).ready(function(){
			//jQuery(document).ready(function($) {
				function fill_field(val, init_value){
					if (!val || val==''){
						options = '<option value="">%(empty_label)s<'+'/option>';
						$("#%(id)s").html(options);
						$('#%(id)s option:first').attr('selected', 'selected');
						$("#%(id)s").trigger('change');
						return;
					}
					$.getJSON("%(url)s/"+val+"/", function(j){
						var options = '<option value="">%(empty_label)s<'+'/option>';
						for (var i = 0; i < j.length; i++) {
							options += '<option value="' + j[i].value + '">' + j[i].display + '<'+'/option>';
						}
						var width = $("#%(id)s").outerWidth();
						$("#%(id)s").html(options);
						if (navigator.appVersion.indexOf("MSIE") != -1)
							$("#%(id)s").width(width + 'px');
						$('#%(id)s option:first').attr('selected', 'selected');
						var auto_choose = %(auto_choose)s;
						if(init_value){
							$('#%(id)s option[value="'+ init_value +'"]').attr('selected', 'selected');
						}
						if(auto_choose && j.length == 1){
							$('#%(id)s option[value="'+ j[0].value +'"]').attr('selected', 'selected');
						}
						$("#%(id)s").trigger('change');
					})
				}

				if(!$("#id_%(chainfield)s").hasClass("chained")){
					var val = $("#id_%(chainfield)s").val();
					fill_field(val, "%(value)s");
				}

				$("#id_%(chainfield)s").change(function(){
					var start_value = $("#%(id)s").val();
					var val = $(this).val();
					fill_field(val, start_value);
				})
			})
			var oldDismissAddAnotherPopup = dismissAddAnotherPopup;
			dismissAddAnotherPopup = function(win, newId, newRepr) {
				oldDismissAddAnotherPopup(win, newId, newRepr);
				if (windowname_to_id(win.name) == "id_%(chainfield)s") {
					$("#id_%(chainfield)s").change();
				}
			}
		})(jQuery || django.jQuery);
		//]]>
		</script>

		""" % {
			"chainfield": chain_field or 'null',
			"url": url or 'null',
			"id": attrs['id'] or 'null',
			'value': value or 'null',
			'auto_choose': auto_choose or 'null',
			'empty_label': empty_label or 'null'
		}
		final_choices = []
		if value:
			items = self.queryset.filter(pk=value)
			#raise ValueError((value, self.queryset, items))
			try:
				pk = getattr(items[0], self.model_field + "_id")
				filter = {self.model_field:pk}
			except AttributeError:
				try: # maybe m2m?
					pks = getattr(items[0], self.model_field).all().values_list('pk', flat=True)
					filter = {self.model_field + "__in":pks}
				except AttributeError:
					try: # maybe a set?
						pks = getattr(item, self.model_field + "_set").all().values_list('pk', flat=True)
						filter = {self.model_field + "__in":pks}
					except: # give up
						filter = {}
			filtered = list(get_model(self.app_name, self.model_name).objects.filter(**filter).distinct())
			filtered.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(unicode(x)))
			for choice in filtered:
				final_choices.append((choice.pk, unicode(choice)))
		#if len(final_choices) > 1:
			#final_choices = [("", (empty_label))] + final_choices
		if self.show_all:
			final_choices.append(("", (empty_label)))
			self.choices = list(self.choices)
			self.choices.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(x[1]))
			for ch in self.choices:
				if not ch in final_choices:
					final_choices.append(ch)
		self.choices = ()
		final_attrs = self.build_attrs(attrs, name=name)
		if 'class' in final_attrs:
			final_attrs['class'] += ' chained'
		else:
			final_attrs['class'] = 'chained'
		output = super(ChainedSelect, self).render(name, value, final_attrs, choices=final_choices)
		output += js
		return mark_safe(output)


class ChainedMultipleSelect(SelectMultiple):
	def __init__(self, app_name, model_name, chain_field, model_field, show_all, auto_choose, manager=None, *args, **kwargs):
		self.app_name = app_name
		self.model_name = model_name
		self.chain_field = chain_field
		self.model_field = model_field
		self.show_all = show_all
		self.auto_choose = auto_choose
		self.manager = manager
		super(Select, self).__init__(*args, **kwargs)

	class Media:
		if USE_DJANGO_JQUERY:
			js = ["%s%s" % (settings.ADMIN_MEDIA_PREFIX, i) for i in
					('js/jquery.min.js', 'js/jquery.init.js')]
		elif JQUERY_URL:
			js = (
				JQUERY_URL,
			)

	def render(self, name, value, attrs=None, choices=()):

		if len(name.split('-')) > 1: # formset
			chain_field = '-'.join(name.split('-')[:-1] + [self.chain_field])
		else:
			chain_field = self.chain_field

		chain_field_is_complex = (len(chain_field.split('__')) > 1)
		chain_field_original = chain_field
		chain_field = chain_field.split('__')[0]

		if self.show_all:
			view_name = "chained_filter_all"
		else:
			view_name = "chained_filter"

		kwargs = {'app':self.app_name, 'model':self.model_name, 'field':self.model_field, 'value':"1"}

		if self.manager is not None:
			kwargs.update({'manager': self.manager})

		url = "/".join(reverse(view_name, kwargs=kwargs).split("/")[:-2])

		if self.auto_choose:
			auto_choose = 'true'
		else:
			auto_choose = 'false'

		js = """
		<script type="text/javascript">
		//<![CDATA[
		(function($) {
			function fireEvent(element,event){
				if (document.createEventObject){
				// dispatch for IE
				var evt = document.createEventObject();
				return element.fireEvent('on'+event,evt)
				}
				else{
				// dispatch for firefox + others
				var evt = document.createEvent("HTMLEvents");
				evt.initEvent(event, true, true ); // event type,bubbling,cancelable
				return !element.dispatchEvent(evt);
				}
			}

			function dismissRelatedLookupPopup(win, chosenId) {
				var name = windowname_to_id(win.name);
				var elem = document.getElementById(name);
				if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
					elem.value += ',' + chosenId;
				} else {
					elem.value = chosenId;
				}
				fireEvent(elem, 'change');
				win.close();
			}

			$(document).ready(function() {
			//jQuery(document).ready(function($) {

				function fill_field(val, init_value){
					if (!val || val==''){
						options = '';
						$("#%(id)s").html(options);
						$('#%(id)s option:first').attr('selected', 'selected');
						$("#%(id)s").trigger('change');
						return;
					}
					$.getJSON("%(url)s/"+val+"/", function(j){
						var options = '';
						for (var i = 0; i < j.length; i++) {
							options += '<option value="' + j[i].value + '">' + j[i].display + '<'+'/option>';
						}
						var width = $("#%(id)s").outerWidth();
						$("#%(id)s").html(options);
						if (navigator.appVersion.indexOf("MSIE") != -1)
							$("#%(id)s").width(width + 'px');
						var auto_choose = %(auto_choose)s;
						if(init_value){
							for(i in init_value) {
								$('#%(id)s option[value="'+ init_value[i] +'"]').attr('selected', 'selected');
							}
						}
						/*
						if(auto_choose && j.length == 1){
							$('#%(id)s option[value="'+ j[0].value +'"]').attr('selected', 'selected');
						}
						*/
						$("#%(id)s").trigger('change');
					})
				}

				if(!$("#id_%(chainfield)s").hasClass("chained")){
					var val = $("#id_%(chainfield)s").val();
					fill_field(val, %(value)s);
				}

				$("#id_%(chainfield)s").change(function(){
					var start_value = $("#%(id)s").val();
					var val = $(this).val();
					fill_field(val, start_value);
				})
			})
			var oldDismissAddAnotherPopup = dismissAddAnotherPopup;
			dismissAddAnotherPopup = function(win, newId, newRepr) {
				oldDismissAddAnotherPopup(win, newId, newRepr);
				if (windowname_to_id(win.name) == "id_%(chainfield)s") {
					$("#id_%(chainfield)s").change();
				}
			}
		})(jQuery || django.jQuery);
		//]]>
		</script>

		""" % {
			"chainfield": chain_field or 'null',
			"url":url or 'null',
			"id": attrs['id'],
			'value':value or 'null',
			'auto_choose': auto_choose or 'null',
		}

		model_to_filter = get_model(self.app_name, self.model_name)
		model_field_to_filter = self.model_field
		#raise ValueError(model_to_filter, model_field_to_filter)
		if value:
			items = self.queryset.filter(pk__in=value)
			if items:
				model_field_to_filter_list = model_field_to_filter.split('__')
				pk = items[0]
				for step in model_field_to_filter_list:
					pk = getattr(pk, step, None)
				if isinstance(pk, object):
					pk = pk.pk
				final_choices = model_to_filter.objects.filter(**{model_field_to_filter: pk})
				final_choices = [(c.id, unicode(c)) for c in final_choices]
		else:
			final_choices = []

		if self.show_all:
			self.choices = list(self.choices)
			self.choices.sort(cmp=locale.strcoll, key=lambda x:unicode_sorter(x[1]))
			for ch in self.choices:
				if not ch in final_choices:
					final_choices.append(ch)
		self.choices = ()
		final_attrs = self.build_attrs(attrs, name=name)

		if 'class' in final_attrs:
			final_attrs['class'] += ' chained'
		else:
			final_attrs['class'] = 'chained'

		output = self.parent_render(name, value, final_attrs, choices=final_choices)
		output += js
		return mark_safe(output)

	def parent_render(self, name, value, attrs=None, choices=()):
		if value is None: value = []
		final_attrs = self.build_attrs(attrs, name=name)
		output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
		options = self.render_options(choices, value)
		if options:
			output.append(options)
		output.append('</select>')
		return mark_safe(u'\n'.join(output))

	def render_option(self, selected_choices, option_value, option_label):
		option_value = force_unicode(option_value)
		selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
		return u'<option value="%s"%s>%s</option>' % (
			escape(option_value), selected_html,
			conditional_escape(force_unicode(option_label)))

	def render_options(self, choices, selected_choices):
		# Normalize to strings.
		selected_choices = set([force_unicode(v) for v in selected_choices])
		output = []
		for option_value, option_label in chain(self.choices, choices):
			if isinstance(option_label, (list, tuple)):
				output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
				for option in option_label:
					output.append(self.render_option(selected_choices, *option))
				output.append(u'</optgroup>')
			else:
				output.append(self.render_option(selected_choices, option_value, option_label))
		return u'\n'.join(output)