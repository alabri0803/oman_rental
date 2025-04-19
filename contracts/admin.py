from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Contract, ContractAmendment, ContractDocument, ContractTermination

# Register your models here.

class ContractDocumentInline(admin.TabularInline):
    model = ContractDocument
    extra = 1

class ContractAmendmentInline(admin.TabularInline):
    model = ContractAmendment
    extra = 0
    readonly_fields = ('amendment_number', 'created_by', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('contract_number', 'unit', 'tenant', 'start_date', 'end_date', 'monthly_rent', 'status')
    list_filter = ('status', 'start_date', 'end_date', 'unit__building')
    search_fields = ('contract_number', 'tenant__username', 'tenant__company_name')
    inlines = [ContractDocumentInline, ContractAmendmentInline]
    readonly_fields = ('created_at', 'updated_at', 'signed_at')
    fieldsets = (
        (None, {
            'fields': ('contract_number', 'unit', 'tenant', 'status')
        }),
        (_('تفاصيل العقد'), {
            'fields': ('start_date', 'end_date', 'monthly_rent', 'payment_terms', 'secrity_deposit')
        }),
        (_('التوقيعات'), {
            'fields': ('signed__by_tenant', 'signed_by_landlord', 'signed_at')
        }),
        (_('الشروط والملاحظات'), {
            'fields': ('terms_and_conditions', 'notes')
        }),
        (_('المعلومات الإدارية'), {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )

@admin.register(ContractDocument)
class ContractDocumentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'description', 'uploaded_at')
    list_filter = ('contract__status',)
    search_fields = ('contract__contract_number', 'description')

@admin.register(ContractAmendment)
class ContractAmendmentAdmin(admin.ModelAdmin):
    list_display = ('contract', 'amendment_number', 'created_at', 'approved')
    list_filter = ('approved', 'created_at')
    search_fields = ('contract__contract_number', 'reason', 'changes')
    readonly_fields = ('created_by', 'created_at', 'approved_by', 'approved_at')

@admin.register(ContractTermination)
class ContractTerminationAdmin(admin.ModelAdmin):
    list_display = ('contract', 'termination_date')
    list_filter = ('termination_date',)
    search_fields = ('contract__contract_number', 'reason')
    readonly_fields = ('initiated_by', 'created_at', 'approved_by')