from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)

    def setUp(self):
        self.guest_client = Client()

    def test_about_author(self):
        guest_client = Client()
        response = guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def setUp(self):
        self.guest_client = Client()

    def test_technology(self):
        guest_client = Client()
        response = guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
