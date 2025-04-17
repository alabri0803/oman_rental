from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

# Create your views here.

class HomeView(TemplateView):
  template_name = 'pages/home.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('الرئيسية')
    return context

class DashboardView(LoginRequiredMixin, TemplateView):
  template_name = 'pages/dashboard.html'
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['title'] = _('لوحة التحكم')
    return context