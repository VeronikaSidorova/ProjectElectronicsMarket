from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from electronics.models import EmployeeProfile


class Command(BaseCommand):
    help = "Создает тестовых сотрудников для системы"

    def handle(self, *args, **options):
        employees = [
            {
                "username": "supply_manager",
                "email": "supply@electronics.com",
                "password": "supply123",
                "department": "Поставки",
                "position": "Менеджер по поставкам",
            },
            {
                "username": "product_manager",
                "email": "products@electronics.com",
                "password": "products123",
                "department": "Продукты",
                "position": "Менеджер по продуктам",
            },
            {
                "username": "network_analyst",
                "email": "analyst@electronics.com",
                "password": "analyst123",
                "department": "Аналитика",
                "position": "Аналитик сети",
            },
        ]

        for emp_data in employees:
            if not User.objects.filter(username=emp_data["username"]).exists():
                user = User.objects.create_user(
                    username=emp_data["username"],
                    email=emp_data["email"],
                    password=emp_data["password"],
                    is_staff=True,
                    is_active=True,
                    first_name=emp_data["position"].split()[-1],  # Для демонстрации
                )

                # Создаем профиль сотрудника
                EmployeeProfile.objects.create(
                    user=user,
                    department=emp_data["department"],
                    position=emp_data["position"],
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создан сотрудник: {emp_data["username"]} ({emp_data["position"]})'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'Сотрудник {emp_data["username"]} уже существует'
                    )
                )
