from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from .models import Contact, Product, NetworkNode, EmployeeProfile


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["email", "country", "city", "street", "house_number"]
    list_filter = ["country", "city"]
    search_fields = ["email", "country", "city"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "model", "release_date"]
    list_filter = ["release_date"]
    search_fields = ["name", "model"]


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "node_type",
        "hierarchy_level",
        "supplier_link",
        "debt",
        "created_at",
    ]
    list_filter = ["node_type", "contact__city", "created_at"]
    search_fields = ["name", "contact__email"]
    actions = ["clear_debt"]

    def supplier_link(self, obj):
        if obj.supplier:
            url = reverse(
                "admin:electronics_networknode_change", args=[obj.supplier.id]
            )
            return format_html('<a href="{}">{}</a>', url, obj.supplier.name)
        return "-"

    supplier_link.short_description = "Поставщик"

    def hierarchy_level(self, obj):
        return obj.hierarchy_level

    hierarchy_level.short_description = "Уровень иерархии"

    @admin.action(description="Очистить задолженность выбранных объектов")
    def clear_debt(self, request, queryset):
        updated = queryset.update(debt=0)
        self.message_user(request, f"Задолженность очищена для {updated} объектов")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("supplier", "contact")


class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False
    verbose_name_plural = "Профиль сотрудника"


class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeProfileInline,)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "groups")


# Перерегистрируем User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "position", "phone"]
    list_filter = ["department", "position"]
    search_fields = ["user__username", "user__email", "department"]
