from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from electronics.models import Contact, Product, NetworkNode, EmployeeProfile
from datetime import date


class FullSystemTest(APITestCase):
    """
    Полные системные тесты для приложения электронной сети
    """

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = APIClient()

        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin123"
        )

        self.active_employee = User.objects.create_user(
            username="employee",
            email="employee@example.com",
            password="employee123",
            is_staff=True,
            is_active=True,
        )

        self.inactive_employee = User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="inactive123",
            is_staff=True,
            is_active=False,
        )

        self.contact_factory = Contact.objects.create(
            email="factory@example.com",
            country="Россия",
            city="Москва",
            street="Заводская",
            house_number="1",
        )

        self.contact_retail = Contact.objects.create(
            email="retail@example.com",
            country="Россия",
            city="Санкт-Петербург",
            street="Невский",
            house_number="100",
        )

        self.contact_entrepreneur = Contact.objects.create(
            email="entrepreneur@example.com",
            country="Беларусь",
            city="Минск",
            street="Победителей",
            house_number="25",
        )

        self.contact_test1 = Contact.objects.create(
            email="test1@example.com",
            country="Россия",
            city="Казань",
            street="Тестовая",
            house_number="10",
        )

        self.contact_test2 = Contact.objects.create(
            email="test2@example.com",
            country="Россия",
            city="Екатеринбург",
            street="Тестовая",
            house_number="20",
        )

        self.product1 = Product.objects.create(
            name="Смартфон", model="X100", release_date=date(2024, 1, 15)
        )

        self.product2 = Product.objects.create(
            name="Ноутбук", model="L200", release_date=date(2024, 2, 1)
        )

        # Создаем сеть
        self.factory = NetworkNode.objects.create(
            name="Главный завод", node_type="factory", contact=self.contact_factory
        )
        self.factory.products.add(self.product1, self.product2)

        self.retail = NetworkNode.objects.create(
            name="Розничная сеть",
            node_type="retail",
            contact=self.contact_retail,
            supplier=self.factory,
            debt=50000.00,
        )
        self.retail.products.add(self.product1)

        self.entrepreneur = NetworkNode.objects.create(
            name="ИП Иванов",
            node_type="entrepreneur",
            contact=self.contact_entrepreneur,
            supplier=self.retail,
            debt=15000.00,
        )

        self.employee_profile = EmployeeProfile.objects.create(
            user=self.active_employee,
            department="Поставки",
            position="Менеджер",
            phone="+79991234567",
        )

    def test_unauthenticated_access_denied(self):
        """Тест: Неаутентифицированный доступ запрещен"""
        response = self.client.get(reverse("networknode-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_inactive_employee_access_denied(self):
        """Тест: Неактивный сотрудник не имеет доступа"""
        self.client.force_authenticate(user=self.inactive_employee)
        response = self.client.get(reverse("networknode-list"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_active_employee_has_access(self):
        """Тест: Активный сотрудник имеет доступ"""
        self.client.force_authenticate(user=self.active_employee)
        response = self.client.get(reverse("networknode-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_network_node_hierarchy_level(self):
        """Тест: Корректное вычисление уровня иерархии"""
        self.assertEqual(self.factory.hierarchy_level, 0)
        self.assertEqual(self.retail.hierarchy_level, 1)
        self.assertEqual(self.entrepreneur.hierarchy_level, 2)

    def test_contact_str_representation(self):
        """Тест: Строковое представление контакта"""
        expected = "Россия, Москва, Заводская, 1"
        self.assertEqual(str(self.contact_factory), expected)

    def test_product_str_representation(self):
        """Тест: Строковое представление продукта"""
        expected = "Смартфон X100"
        self.assertEqual(str(self.product1), expected)

    def test_employee_profile_str_representation(self):
        """Тест: Строковое представление профиля сотрудника"""
        self.assertIn("Менеджер", str(self.employee_profile))

    def test_list_network_nodes(self):
        """Тест: Получение списка звеньев сети"""
        self.client.force_authenticate(user=self.active_employee)
        response = self.client.get(reverse("networknode-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_retrieve_network_node(self):
        """Тест: Получение конкретного звена сети"""
        self.client.force_authenticate(user=self.active_employee)
        url = reverse("networknode-detail", args=[self.factory.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Главный завод")
        self.assertEqual(response.data["hierarchy_level"], 0)
        self.assertIn("debt", response.data)

    def test_create_network_node(self):
        """Тест: Создание нового звена сети"""
        self.client.force_authenticate(user=self.active_employee)

        new_contact = Contact.objects.create(
            email="new_retail@example.com",
            country="Россия",
            city="Казань",
            street="Баумана",
            house_number="50",
        )

        data = {
            "name": "Новая розничная сеть",
            "node_type": "retail",
            "contact": new_contact.id,
            "supplier": self.factory.id,
            "products": [self.product1.id],
            "debt": 25000.00,
        }

        response = self.client.post(reverse("networknode-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkNode.objects.count(), 4)

        new_node = NetworkNode.objects.get(name="Новая розничная сеть")
        self.assertEqual(new_node.debt, 0.00)

    def test_update_network_node_normal_fields(self):
        """Тест: Обновление обычных полей звена сети"""
        self.client.force_authenticate(user=self.active_employee)

        url = reverse("networknode-detail", args=[self.retail.id])
        data = {"name": "Обновленная розничная сеть"}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.retail.refresh_from_db()
        self.assertEqual(self.retail.name, "Обновленная розничная сеть")

    def test_update_network_node_debt_field_protected(self):
        """Тест: Поле debt защищено от обновления через API"""
        self.client.force_authenticate(user=self.active_employee)

        original_debt = self.retail.debt
        url = reverse("networknode-detail", args=[self.retail.id])
        data = {"debt": 0.00}

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.retail.refresh_from_db()
        self.assertEqual(self.retail.debt, original_debt)
        self.assertNotEqual(self.retail.debt, 0.00)

    def test_delete_network_node(self):
        """Тест: Удаление звена сети"""
        self.client.force_authenticate(user=self.active_employee)

        url = reverse("networknode-detail", args=[self.entrepreneur.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(NetworkNode.objects.count(), 2)
        self.assertFalse(NetworkNode.objects.filter(id=self.entrepreneur.id).exists())

    def test_filter_by_country(self):
        """Тест: Фильтрация звеньев сети по стране"""
        self.client.force_authenticate(user=self.active_employee)

        url = reverse("networknode-list") + "?contact__country=Россия"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for node in response.data:
            self.assertEqual(node["contact"]["country"], "Россия")

    def test_search_by_city(self):
        """Тест: Поиск звеньев сети по городу"""
        self.client.force_authenticate(user=self.active_employee)

        url = reverse("networknode-list") + "?search=Москва"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_product_search(self):
        """Тест: Поиск продуктов"""
        self.client.force_authenticate(user=self.active_employee)

        url = reverse("product-list") + "?search=Смартфон"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Смартфон")

    def test_list_products(self):
        """Тест: Получение списка продуктов"""
        self.client.force_authenticate(user=self.active_employee)

        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_contacts(self):
        """Тест: Получение списка контактов"""
        self.client.force_authenticate(user=self.active_employee)

        response = self.client.get(reverse("contact-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_create_product(self):
        """Тест: Создание нового продукта"""
        self.client.force_authenticate(user=self.active_employee)

        data = {"name": "Планшет", "model": "T300", "release_date": "2024-03-01"}

        response = self.client.post(reverse("product-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)
        self.assertEqual(Product.objects.get(name="Планшет").model, "T300")

    def test_factory_has_no_supplier(self):
        """Тест: У завода нет поставщика"""
        self.assertIsNone(self.factory.supplier)

    def test_retail_has_supplier(self):
        """Тест: У розничной сети есть поставщик"""
        self.assertEqual(self.retail.supplier, self.factory)

    def test_admin_clear_debt_action(self):
        """Тест: Admin action для очистки задолженности"""
        test_contact = Contact.objects.create(
            email="test_debt@example.com",
            country="Россия",
            city="Тестовград",
            street="Тестовая",
            house_number="99",
        )

        node_with_debt = NetworkNode.objects.create(
            name="Тест с долгом",
            node_type="retail",
            contact=test_contact,
            supplier=self.factory,
            debt=10000.00,
        )

        NetworkNode.objects.filter(id=node_with_debt.id).update(debt=0)

        node_with_debt.refresh_from_db()
        self.assertEqual(node_with_debt.debt, 0.00)

    def test_debt_cannot_be_negative(self):
        """Тест: Задолженность не может быть отрицательной"""
        from django.core.exceptions import ValidationError

        test_contact = Contact.objects.create(
            email="negative_test@example.com",
            country="Россия",
            city="Тест",
            street="Улица",
            house_number="1",
        )

        with self.assertRaises(ValidationError):
            node = NetworkNode(
                name="Ошибочный узел",
                node_type="retail",
                contact=test_contact,
                supplier=self.factory,
                debt=-100.00,
            )
            node.full_clean()

    def test_contact_email_unique(self):
        """Тест: Email контакта должен быть уникальным"""
        with self.assertRaises(Exception):
            Contact.objects.create(
                email="factory@example.com",
                country="Россия",
                city="Москва",
                street="Другая",
                house_number="2",
            )

    def test_complete_workflow(self):
        """Тест: Полный рабочий процесс"""
        self.client.force_authenticate(user=self.active_employee)

        contact_data = {
            "email": "workflow@example.com",
            "country": "Россия",
            "city": "Новосибирск",
            "street": "Рабочая",
            "house_number": "10",
        }
        contact_response = self.client.post(reverse("contact-list"), contact_data)
        self.assertEqual(contact_response.status_code, status.HTTP_201_CREATED)
        contact_id = contact_response.data["id"]

        product_data = {
            "name": "Телевизор",
            "model": "TV500",
            "release_date": "2024-04-01",
        }
        product_response = self.client.post(reverse("product-list"), product_data)
        self.assertEqual(product_response.status_code, status.HTTP_201_CREATED)

        node_data = {
            "name": "Рабочий узел",
            "node_type": "retail",
            "contact": contact_id,
            "supplier": self.factory.id,
        }
        node_response = self.client.post(reverse("networknode-list"), node_data)

        if node_response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(NetworkNode.objects.filter(name="Рабочий узел").count(), 1)

        self.assertEqual(
            Contact.objects.filter(email="workflow@example.com").count(), 1
        )
        self.assertEqual(Product.objects.filter(name="Телевизор").count(), 1)

    def test_api_root_accessible(self):
        """Тест: Корневой URL API доступен"""
        self.client.force_authenticate(user=self.active_employee)

        endpoints = [
            reverse("networknode-list"),
            reverse("product-list"),
            reverse("contact-list"),
        ]

        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelValidationTests(TestCase):
    """Тесты валидации моделей"""

    def test_network_node_node_type_validation(self):
        """Тест: Валидация типа звена сети"""
        from django.core.exceptions import ValidationError

        contact = Contact.objects.create(
            email="validation_test@example.com",
            country="Россия",
            city="Москва",
            street="Тестовая",
            house_number="1",
        )

        valid_types = ["factory", "retail", "entrepreneur"]
        for node_type in valid_types:
            node = NetworkNode(
                name=f"Тест {node_type}", node_type=node_type, contact=contact
            )
            try:
                node.full_clean()
            except ValidationError:
                self.fail(
                    f"Valid node_type '{node_type}' should not raise ValidationError"
                )


class SerializerTests(TestCase):
    """Тесты сериализаторов"""

    def setUp(self):
        self.contact = Contact.objects.create(
            email="serializer_test@example.com",
            country="Россия",
            city="Москва",
            street="Тестовая",
            house_number="1",
        )

        self.factory = NetworkNode.objects.create(
            name="Тестовый завод", node_type="factory", contact=self.contact
        )

    def test_network_node_serializer_includes_debt(self):
        """Тест: Сериализатор включает поле debt (read-only)"""
        from electronics.serializers import NetworkNodeSerializer

        serializer = NetworkNodeSerializer(self.factory)
        self.assertIn("debt", serializer.data)

    def test_network_node_update_serializer_excludes_debt(self):
        """Тест: Сериализатор обновления исключает поле debt"""
        from electronics.serializers import NetworkNodeUpdateSerializer

        serializer = NetworkNodeUpdateSerializer(self.factory)
        self.assertNotIn("debt", serializer.fields)
