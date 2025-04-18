from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_user_permissions(sender, instance, created, **kwargs):
  if created:
    owner_group, created = Group.objects.get_or_create(name=_('Owners'))
    investor_group, created = Group.objects.get_or_create(name=_('Investors'))
    tenant_group, created = Group.objects.get_or_create(name=_('Tenants'))
    signer_group, created = Group.objects.get_or_create(name=_('Signers'))
    admin_group, created = Group.objects.get_or_create(name=_('Admins'))
    if instance.user_type == 'OWNER':
      instance.groups.add(owner_group)
    elif instance.user_type == 'INVESTOR':
      instance.groups.add(investor_group)
    elif instance.user_type == 'TENANT':
      instance.groups.add(tenant_group)
    elif instance.user_type == 'SIGNER':
      instance.groups.add(signer_group)
    elif instance.user_type == 'ADMIN':
      instance.groups.add(admin_group)