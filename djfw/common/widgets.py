from django import forms
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.safestring import mark_safe

class MarkItUpWidget(forms.Textarea):
	"""
	Widget for a MarkItUp editor textarea.
	"""

	def _media(self):
		return forms.Media(
			css = {
				'screen': (
				'/media/markitup/markitup/skins/simple/style.css',
				'/media/markitup/markitup/sets/tulius_html/style.css',
				)
			},
			js = (
			'/media/markitup/markitup/jquery.markitup.js',
			'/media/markitup/markitup/sets/tulius_html/set.js',
			'/media/markitup/markitup/ajax_csrf.js',
			)
		)
	media = property(_media)

	def render(self, name, value, attrs=None):
		html = super(MarkItUpWidget, self).render(name, value, attrs)

		try:
			preview_url = (
			'mySettings["previewParserPath"] = "%s";'
			% reverse('markitup_preview'))
		except NoReverseMatch:
			preview_url = "";

		html += """
        <script type="text/javascript">
			(function($) {
				$(document).ready(function() {
					var element = $("#%(id)s");
					if(!element.hasClass("markItUpEditor")) {
						%(preview_url)s
						element.markItUp(mySettings);
					}
				});
			})(jQuery || django.jQuery);
        </script>
        """ % {
			'id': attrs['id'],
			'preview_url': preview_url
		}

		return mark_safe(html)