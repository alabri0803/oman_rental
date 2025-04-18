from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, UpdateView

from .forms import CustomUserCreationForm, LoginForm, UserUpdateForm
from .models import CustomUser

# Create your views here.

def register_view(request):
  if request.method == 'POST':
    form = CustomUserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.is_active = False
      user.save()
      messages.success(request, _('تم إنشاء الحساب بنجاح! يرجي انتظار التفعيل من المسؤول.'))
      return redirect('accounts:login')
  else:
    form = CustomUserCreationForm()
  return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
  if request.method == 'POST':
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
      username = form.cleaned_data.get('username')
      password = form.cleaned_data.get('password')
      user = authenticate(request, username=username, password=password)
      if user is not None:
        if user.is_active:
          login(request, user)
          messages.success(request, _('تم تسجيل الدخول بنجاح!'))
          return redirect('pages:dashboard')
        else:
          messages.error(request, _('الحساب غير مفعل، يرجي الانتظار حتى يتم التفعيل.'))
    else:
      messages.error(request, _('بيانات الدخول غير صحيحة.'))
  else:
    form = LoginForm()
  return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
  logout(request)
  messages.success(request, _('تم تسجيل الخروج بنجاح!'))
  return redirect('pages:home')

class UserListView(ListView):
  model = CustomUser
  template_name = 'accounts/user_list.html'
  context_object_name = 'users'
  def get_queryset(self):
    if self.request.user.user_type == 'ADMIN':
      return CustomUser.objects.all()
    elif self.request.user.user_type == 'INVESTOR':
      return CustomUser.objects.filter(user_type__in=['TENANT', 'SIGNER'])
    return CustomUser.objects.none()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('قائمة المستخدمين')
    return context

class UserDetailView(DetailView):
  model = CustomUser
  template_name = 'accounts/user_detail.html'
  context_object_name = 'user_obj'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تفاصيل المستخدم')

class UserUpdateView(UpdateView):
  model = CustomUser
  form_class = UserUpdateForm
  template_name = 'accounts/user_update.html'
  success_url = reverse_lazy('accounts:profile')
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('تعديل الملف الشخصي')
    return context

@login_required
def profile_view(request):
  return render(request, 'accounts/profile.html', {'title': _('الملف الشخصي')})
    