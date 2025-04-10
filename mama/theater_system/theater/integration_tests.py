from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Director, Play, Performance
from datetime import datetime, timedelta

class TheaterIntegrationTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя-админа
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='admin12345'
        )
        
        # Создаем тестового обычного пользователя
        self.regular_user = User.objects.create_user(
            username='user_test',
            email='user@test.com',
            password='user12345'
        )
        
        # Создаем тестового режиссера и пьесу
        self.director = Director.objects.create(
            first_name='Test',
            last_name='Director',
            date_of_birth='1980-01-01',
            gender='M',
            contact_info='test@test.com',
            years_of_experience=10
        )
        
        self.play = Play.objects.create(
            title='Test Play',
            description='Test Description',
            director=self.director,
            genre='drama',
            duration=120
        )
        
        # Инициализируем клиент для тестов
        self.client = Client()

    def test_login_functionality(self):
        """Тест функциональности входа в систему"""
        # Тестируем неправильный логин
        response = self.client.post(reverse('login'), {
            'username': 'wrong_user',
            'password': 'wrong_password'
        })
        self.assertNotEqual(response.status_code, 302)  # Не должно быть редиректа
        
        # Тестируем правильный логин админа
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'admin12345'
        })
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        self.assertTrue(response.url.startswith(reverse('home')))

    def test_create_performance(self):
        """Тест создания нового представления"""
        # Логинимся как админ
        self.client.login(username='admin_test', password='admin12345')
        
        # Данные для нового представления
        performance_data = {
            'play': self.play.id,
            'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '19:00',
            'tickets_available': 100,
            'ticket_price': 1000,
            'status': 'scheduled'
        }
        
        # Пробуем создать представление
        response = self.client.post(reverse('performance_create'), performance_data)
        self.assertEqual(response.status_code, 302)  # Должен быть редирект
        
        # Проверяем, что представление создано
        self.assertTrue(Performance.objects.filter(play=self.play).exists())

    def test_delete_performance(self):
        """Тест удаления представления"""
        # Создаем тестовое представление
        performance = Performance.objects.create(
            play=self.play,
            date=datetime.now() + timedelta(days=1),
            time='19:00',
            tickets_available=100,
            ticket_price=1000,
            status='scheduled'
        )
        
        # Пробуем удалить без авторизации
        response = self.client.post(reverse('performance_delete', kwargs={'pk': performance.id}))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа
        self.assertTrue(Performance.objects.filter(id=performance.id).exists())  # Представление не удалено
        
        # Логинимся как админ
        self.client.login(username='admin_test', password='admin12345')
        
        # Пробуем удалить с правами админа
        response = self.client.post(reverse('performance_delete', kwargs={'pk': performance.id}))
        self.assertEqual(response.status_code, 302)  # Редирект после успешного удаления
        self.assertFalse(Performance.objects.filter(id=performance.id).exists())  # Представление удалено 