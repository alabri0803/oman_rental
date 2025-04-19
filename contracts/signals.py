from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from  .models import Contract
from properties.models import Unit

@receiver(post_save, sender=Contract)
def update_unit_status(sender, instance, **kwargs):
    if instance.pk:
        original = Contract.objects.get(pk=instance.pk)
        if original.status != instance.status:
            if instance.status == 'ACTIVE':
                instance.unit.status = 'OCCUPIED'
                instance.unit.save()
            elif instance.status in ['EXPIRED', 'TERMINATED']:
              instance.unit.status = 'VACANT'
              instance.unit.save()

@receiver(pre_save, sender=Contract)
def check_contract_status(sender, instance, created, **kwargs):
    if not created and instance.end_date < timezone.now().date() and instance.status == 'ACTIVE':
        instance.status = 'EXPIRED'
        instance.save()
        instance.unit.status = 'VACANT'
        instance.unit.save()