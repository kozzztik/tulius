# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class ColorPickerWidget(forms.TextInput):
	class Media:
		css = {
			'all': (
				#settings.MEDIA_URL + 'colors/css/colorpicker.css',
				settings.MEDIA_URL + 'farbtastic/farbtastic.css',
			)
		}
		js = (
			#settings.MEDIA_URL + 'colors/js/colorpicker.js',
			settings.MEDIA_URL + 'farbtastic/farbtastic.js',
		)

	def __init__(self, language=None, attrs=None):
		self.language = language or settings.LANGUAGE_CODE[:2]
		super(ColorPickerWidget, self).__init__(attrs=attrs)

	def render(self, name, value, attrs=None):
		rendered = super(ColorPickerWidget, self).render(name, value, attrs)
		js = """
		<div id="colorpicker"></div>
		<script type="text/javascript">(function($){
			$('#colorpicker').farbtastic('#id_%s');
		})(jQuery || django.jQuery);
		</script>
		""" % (name);
		return mark_safe(rendered + mark_safe(js))
#        return rendered + mark_safe(u"""<script type="text/javascript">(function($){
#$(function(){
#    var preview = $('<div class="color-picker-preview"><div style="background-color:#%s"></div></div>').insertAfter('#id_%s');
#    $('#id_%s').ColorPicker({
#        color: '%s',
#        onSubmit: function(hsb, hex, rgb, el) { $(el).val(hex); $(el).ColorPickerHide();$(preview).find('div').css('backgroundColor', '#' + hex); },
#        onBeforeShow: function () { $(this).ColorPickerSetColor(this.value); }
#    }).bind('keyup', function(){ $(this).ColorPickerSetColor(this.value); });
#});})(jQuery || django.jQuery);</script>""" % (value, name, name, value))