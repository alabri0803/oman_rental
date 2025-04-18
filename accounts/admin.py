from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = CustomUser
  list_display = ['username', 'email', 'user_type', 'company_name', 'is_active', 'is_authorized']
  list_filter = ['user_type', 'is_active', 'is_authorized']
  fieldsets = (
    (None, {'fields': ('username', 'password')}),
    (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
    (_('Company info'), {'fields': ('user_type', 'company_name', 'commercial_registration', 'tax_number')}),
    (_('Permissions'), {'fields': ('is_active', 'is_authorized', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
  )
  add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'email', 'user_type', 'phone_number', 'password1', 'password2'),
    }),
  )
  search_fields = ['username', 'email', 'company_name', 'phone_number']

admin.site.register(CustomUser, CustomUserAdmin)