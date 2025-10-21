from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Contact(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    country = models.CharField(max_length=100, verbose_name="Страна")
    city = models.CharField(max_length=100, verbose_name="Город")
    street = models.CharField(max_length=200, verbose_name="Улица")
    house_number = models.CharField(max_length=10, verbose_name="Номер дома")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return f"{self.country}, {self.city}, {self.street}, {self.house_number}"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    model = models.CharField(max_length=200, verbose_name="Модель")
    release_date = models.DateField(verbose_name="Дата выхода на рынок")

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return f"{self.name} {self.model}"


class NetworkNode(models.Model):
    NODE_TYPES = (
        ("factory", "Завод"),
        ("retail", "Розничная сеть"),
        ("entrepreneur", "Индивидуальный предприниматель"),
    )

    name = models.CharField(max_length=200, verbose_name="Название")
    node_type = models.CharField(
        max_length=20, choices=NODE_TYPES, verbose_name="Тип звена"
    )
    contact = models.OneToOneField(
        Contact, on_delete=models.CASCADE, verbose_name="Контакты"
    )
    products = models.ManyToManyField(Product, verbose_name="Продукты")
    supplier = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Поставщик",
        related_name="children",
    )
    debt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Задолженность перед поставщиком",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Звено сети"
        verbose_name_plural = "Звенья сети"

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.name}"

    @property
    def hierarchy_level(self):
        """Вычисляет уровень иерархии"""
        if self.supplier is None:
            return 0
        return self.supplier.hierarchy_level + 1


class EmployeeProfile(models.Model):
    """Профиль сотрудника с дополнительной информацией"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_profile"
    )
    department = models.CharField(max_length=100, blank=True, verbose_name="Отдел")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.position}"
