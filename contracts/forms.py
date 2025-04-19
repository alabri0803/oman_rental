from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Contract, ContractDocument, ContractAmendment, ContractTermination
from django.core.exceptions import ValidationError
from django.utils import timezone

class ContractForm(forms.ModelForm):
  class Meta:
    model = Contract
    fields = ['unit', 'tenant', 'start_date', 'end_date', 'monthly_rent', 'payment_terms', 'security_deposit', 'terms_and_conditions', 'notes']
    widgets = {
      'start_date': forms.DateInput(attrs={'type': 'date'}),
      'end_date': forms.DateInput(attrs={'type': 'date'}),
      'terms_and_conditions': forms.Textarea(attrs={'rows': 5}),
      'notes': forms.Textarea(attrs={'rows': 3}),
    }
    labels = {
      'unit': _('الوحدة'),
      'tenant': _('المستأجر'),
      'start_date': _('تاريخ البدء'),
      'end_date': _('تاريخ الانتهاء'),
      'monthly_rent': _('الإيجار الشهري (ر.ع.)'),
      'payment_terms': _('فترة الدفع'),
      'security_deposit': _('الضمان المالي (ر.ع.)'),
      'terms_and_conditions': _('الشروط والأحكام'),
      'notes': _('ملاحظات'),
    }
  def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get('start_date')
    end_date = cleaned_data.get('end_date')
    if start_date and end_date and start_date >= end_date:
      raise ValidationError(_('تاريخ الانتهاء يجب أن يكون بعد تاريخ البدء.'))
    if unit and unit.status != 'VACANT':
      raise ValidationError(_('الوحدة يجب أن تكون شاغرة لإتمام العقد.'))
    return cleaned_data

class ContractAmendmentForm(forms.ModelForm):
  class Meta:
    model = ContractAmendment
    fields = ['reason', 'changes', 'new_monthly_rent', 'new_end_date']
    widgets = {
      'reason': forms.Textarea(attrs={'rows': 3}),
      'changes': forms.Textarea(attrs={'rows': 3}),
      'new_end_date': forms.DateInput(attrs={'type': 'date'}),
    }
    labels = {
      'reason': _('سبب التعديل'),
      'changes': _('التغييرات المطبقة'),
      'new_monthly_rent': _('الإيجار الشهري الجديد (ر.ع.)'),
      'new_end_date': _('تاريخ الانتهاء الجديد'),
    }
  def clean(self):
    cleaned_data = super().clean()
    new_monthly_rent = cleaned_data.get('new_monthly_rent')
    new_end_date = cleaned_data.get('new_end_date')
    if not new_monthly_rent and not new_end_date:
      raise ValidationError(_('يجب تحديد إما الايجار جديد أو تاريخ الانتهاء الجديد أو كليهما.'))
    return cleaned_data

class ContractTerminationForm(forms.ModelForm):
  class Meta:
    model = ContractTermination
    fields = ['termination_date', 'reason', 'penalty_amount', 'refund_amount', 'notes']
    widgets = {
      'termination_date': forms.DateInput(attrs={'type': 'date'}),
      'reason': forms.Textarea(attrs={'rows': 3}),
      'notes': forms.Textarea(attrs={'rows': 3}),
    }
    labels = {
      'termination_date': _('تاريخ الإنهاء'),
      'reason': _('سبب الإنهاء'),
      'penalty_amount': _('مبلغ الغرامة (ر.ع.)'),
      'refund_amount': _('مبلغ الاسترداد (ر.ع.)'),
      'notes': _('ملاحظات'),
    }
  def clean_termination_date(self):
    termination_date = self.cleaned_data.get('termination_date')
    if termination_date < timezone.now().date():
      raise ValidationError(_('تاريخ الإنهاء يجب أن يكون في المستقبل.'))
    return termination_date

class ContractSignForm(forms.ModelForm):
  signature = forms.CharField(widget=forms.HiddenInput(), required=True)
  sign_as = forms.ChoiceField(choices=[('landlord', _('المالك')), ('tenant', _('المستأجر'))], widget=forms.HiddenInput())

  def __init__(self, *args, **kwargs):
    self.contract = kwargs.pop('contract', None)
    self.user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)

  def clean(self):
    cleaned_data = super().clean()
    sign_as = cleaned_data.get('sign_as')
    if sign_as == 'landlord' and not self.user.user_type in ['INVESTOR', 'OWNER']:
      raise ValidationError(_('يجب أن تكون مالك أو مستثمر لتوقيع العقد.'))
    if sign_as == 'tenant' and self.user.user_type != 'TENANT':
      raise ValidationError(_('يجب أن تكون مستأجر لتوقيع العقد.'))
    return cleaned_data