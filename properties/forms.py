from django import forms

from .models import Building, Unit, UnitImage, UnitType


class BuildingForm(forms.ModelForm):
  class Meta:
    model = Building
    fields = '__all__'
    widgets = {
      'description': forms.Textarea(attrs={'rows': 3}),
    }

class UnitTypeForm(forms.ModelForm):
  class Meta:
    model = UnitType
    fields = '__all__'
    widgets = {
      'description': forms.Textarea(attrs={'rows': 3}),
    }

class UnitForm(forms.ModelForm):
  class Meta:
    model = Unit
    fields = '__all__'
    widgets = {
      'features': forms.Textarea(attrs={'rows': 3}),
      'description': forms.Textarea(attrs={'rows': 3}),
    }

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)
    if user and user.user_type == 'INVESTOR':
      self.fields['building'].queryset = Building.objects.filter(owner=user)

class UnitImageForm(forms.ModelForm):
  class Meta:
    model = UnitImage
    fields = ['image', 'caption', 'is_featured']