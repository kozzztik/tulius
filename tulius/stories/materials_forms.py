from django import forms
from . import models


class AdditionalMaterialForm(forms.ModelForm):
    class Meta:
        model = models.AdditionalMaterial
        exclude = ('story', 'variation',)

    use_required_attribute = False


class IllustrationForm(forms.ModelForm):
    class Meta:
        model = models.Illustration
        fields = ('name', 'admins_only',)
