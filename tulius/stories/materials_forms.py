from .models import *
from django import forms

class AdditionalMaterialForm(forms.ModelForm):
    class Meta:
        model = AdditionalMaterial
        exclude=('story', 'variation',)
        
class IllustrationForm(forms.ModelForm):
    class Meta:
        model = Illustration
        fields=('name', 'admins_only',)