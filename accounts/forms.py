from django import forms
from django.contrib.auth.forms import (
  AuthenticationForm,
  UserChangeForm,
  UserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
  password1 = forms.CharField(
    label=_('كلمة المرور'),
    strip=False,
    widget=forms.PasswordInput(attrs={'autocomplate': 'new-password'}),
  )
  password2 = forms.CharField(
    label=_('تأكيد كلمة المرور'),
    widget=forms.PasswordInput(attrs={'autocomplate': 'new-password'}),
    strip=False,
  )
  class Meta:
    model = CustomUser
    fields = ('username', 'email', 'user_type', 'phone_number')
    labels = {
      'username': _('اسم المستخدم'),
      'email': _('البريد الإلكتروني'),
      'user_type': _('نوع المستخدم'),
      'phone_number': _('رقم الهاتف'),
    }
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields:
      self.fields[field].required = True

class CustomUserChangeForm(UserChangeForm):
  class Meta:
    model = CustomUser
    fields = '__all__'

class LoginForm(AuthenticationForm):
  username = forms.CharField(
    label=_('اسم المستخدم أو البريد الإلكتروني'),
  )
  password = forms.CharField(
    label=_('كلمة المرور'),
    widget=forms.PasswordInput,
  )
  error_messages = {
    'invalid_login': _('يرجي إدخال اسم المستخدم/بريد الإلكتروني وكلمة المرور الصحيحة.'),
    'inactive': _('هذا الحساب غير مفعل'),
  }

class UserUpdateForm(forms.ModelForm):
  class Meta:
    model = CustomUser
    fields = ('first_name', 'last_name', 'email', 'phone_number', 'company_name')
    labels = {
      'first_name': _('الاسم الأول'),
      'last_name': _('الاسم الأخير'),
      'email': _('البريد الإلكتروني'),
      'phone_number': _('رقم الهاتف'),
      'company_name': _('اسم الشركة'),
    }