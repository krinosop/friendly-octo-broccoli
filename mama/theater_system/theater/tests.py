from django.test import TestCase, Client, LiveServerTestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from .models import Director, Play, Actor, Performance, ActorRole, Casting
from django.utils import timezone
from datetime import timedelta, date, datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from webdriver_manager.chrome import ChromeDriverManager
from django.conf import settings
import os
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

class TheaterTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя-администратора
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Создаем обычного пользователя
        self.regular_user = User.objects.create_user(
            username='user',
            password='testpass123'
        )
        
        # Создаем тестового режиссера
        self.director = Director.objects.create(
            first_name='Иван',
            last_name='Петров',
            date_of_birth='1980-01-01',
            gender='M',
            contact_info='test@test.com',
            years_of_experience=10
        )
        
        # Создаем тестовый спектакль
        self.play = Play.objects.create(
            title='Тестовый спектакль',
            description='Тестовое описание',
            director=self.director,
            genre='D',
            duration=120
        )
        
        # Создаем тестового актера
        self.actor = Actor.objects.create(
            first_name='Петр',
            last_name='Иванов',
            date_of_birth='1990-01-01',
            gender='M',
            contact_info='actor@test.com'
        )
        
        # Создаем тестовое представление
        self.performance = Performance.objects.create(
            play=self.play,
            date=timezone.now() + timedelta(days=1),
            tickets_available=100,
            ticket_price=1000.00
        )
        self.performance.actors.add(self.actor)
        
        self.client = Client()

    def test_play_creation(self):
        """Тест создания спектакля"""
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('play_create'), {
            'title': 'Новый спектакль',
            'description': 'Описание',
            'director': self.director.id,
            'genre': 'D',
            'duration': 120
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Play.objects.filter(title='Новый спектакль').exists())

    def test_play_validation(self):
        """Тест валидации данных спектакля"""
        with self.assertRaises(ValueError):
            Play.objects.create(
                title='',  # Пустое название
                description='Test Description',
                director=self.director,
                genre='D',
                duration=-120  # Отрицательная продолжительность
            )

    def test_actor_role_assignment(self):
        """Тест назначения роли актеру"""
        role = ActorRole.objects.create(
            actor=self.actor,
            play=self.play,
            role_name='Главная роль',
            role_info='Информация о роли'
        )
        self.assertEqual(str(role), 'Петр Иванов - Главная роль в Тестовый спектакль')
        self.assertEqual(self.actor.plays.first(), self.play)

    def test_performance_creation(self):
        """Тест создания представления"""
        self.client.login(username='admin', password='testpass123')
        future_date = timezone.now() + timedelta(days=7)
        response = self.client.post(reverse('performance_create'), {
            'play': self.play.id,
            'date': future_date.strftime('%Y-%m-%d %H:%M:%S'),
            'tickets_available': 200,
            'ticket_price': 1500.00,
            'actors': [self.actor.id],
            'status': 'scheduled'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Performance.objects.filter(play=self.play, tickets_available=200).exists())

    def test_admin_access(self):
        """Тест прав доступа администратора"""
        # Проверяем доступ админа
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('play_delete', args=[self.play.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Проверяем запрет доступа обычному пользователю
        self.client.login(username='user', password='testpass123')
        response = self.client.get(reverse('play_delete', args=[self.play.pk]))
        self.assertEqual(response.status_code, 302)  # Редирект на страницу входа

class ActorIntegrationTests(TestCase):
    def setUp(self):
        # Create test user with director permissions
        self.user = User.objects.create_user(
            username='testdirector',
            password='testpass123'
        )
        self.director_group = Group.objects.create(name='Director')
        self.user.groups.add(self.director_group)
        self.user.save()
        
        # Create test director
        self.director = Director.objects.create(
            first_name='Test',
            last_name='Director',
            date_of_birth=date(1990, 1, 1),
            gender='M',
            contact_info='test@example.com',
            years_of_experience=5
        )
        
        # Create test play
        self.play = Play.objects.create(
            title='Test Play',
            description='Test Description',
            director=self.director,
            genre='D',
            duration=120
        )
        
        # Set up test client
        self.client = Client()
        self.client.login(username='testdirector', password='testpass123')

    def test_actor_creation_flow(self):
        """Test the complete flow of creating an actor"""
        # Create actor
        response = self.client.post(reverse('actor_create'), {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1995-01-01',
            'gender': 'M',
            'contact_info': 'john@example.com'
        })
        
        # Check if actor was created and redirected to actor list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('actor_list'))
        
        # Verify actor exists in database
        actor = Actor.objects.get(first_name='John', last_name='Doe')
        self.assertEqual(actor.contact_info, 'john@example.com')
        
        # Check actor detail page
        response = self.client.get(reverse('actor_detail', args=[actor.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')

    def test_actor_deletion_flow(self):
        """Test the complete flow of deleting an actor"""
        # Create actor first
        actor = Actor.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(1995, 1, 1),
            gender='F',
            contact_info='jane@example.com'
        )
        
        # Delete actor
        response = self.client.post(reverse('actor_delete', args=[actor.pk]))
        
        # Check if actor was deleted and redirected to actor list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('actor_list'))
        
        # Verify actor no longer exists in database
        with self.assertRaises(Actor.DoesNotExist):
            Actor.objects.get(pk=actor.pk)

    def test_actor_list_view(self):
        """Test actor list view with search and filters"""
        # Create test actors
        Actor.objects.create(
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1995, 1, 1),
            gender='M',
            contact_info='john@example.com'
        )
        Actor.objects.create(
            first_name='Jane',
            last_name='Smith',
            date_of_birth=date(1995, 1, 1),
            gender='F',
            contact_info='jane@example.com'
        )
        
        # Test search functionality
        response = self.client.get(reverse('actor_list') + '?search=John')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertNotContains(response, 'Jane Smith')
        
        # Test gender filter
        response = self.client.get(reverse('actor_list') + '?gender=F')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'John Doe')
        self.assertContains(response, 'Jane Smith')

class ActorIntegrationSeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # Initialize Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.maximize_window()
        
        # Setup static files
        settings.STATIC_ROOT = os.path.join(settings.BASE_DIR, 'static')
        settings.STATICFILES_DIRS = []
        if not os.path.exists(settings.STATIC_ROOT):
            os.makedirs(settings.STATIC_ROOT)
        from django.core.management import call_command
        call_command('collectstatic', interactive=False, verbosity=0)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Create superuser for testing
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client.login(username='admin', password='admin123')
        
    def test_actor_workflow(self):
        # Test actor creation workflow
        try:
            # Open login page
            print("Opening login page...")
            self.selenium.get(f'{self.live_server_url}/admin/login/')
            
            # Login
            print("Logging in...")
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('admin')
            password_input.send_keys('admin123')
            self.selenium.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
            
            # Navigate to actor creation
            print("Navigating to actor creation page...")
            self.selenium.get(f'{self.live_server_url}/actors/create/')
            
            # Fill the form
            print("Filling actor creation form...")
            self.selenium.find_element(By.NAME, 'name').send_keys('John Doe')
            self.selenium.find_element(By.NAME, 'age').send_keys('30')
            Select(self.selenium.find_element(By.NAME, 'gender')).select_by_value('M')
            self.selenium.find_element(By.NAME, 'experience').send_keys('5')
            
            # Submit the form
            print("Submitting form...")
            self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            
            # Wait for redirect and verify
            print("Waiting for redirect...")
            WebDriverWait(self.selenium, 10).until(
                EC.url_to_be(f'{self.live_server_url}/actors/')
            )
            
            # Verify actor was created
            self.assertTrue(Actor.objects.filter(name='John Doe').exists())
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise

    def test_actor_search_and_filter(self):
        # Create test actors
        print("Creating test actors...")
        Actor.objects.create(name='John Smith', age=30, gender='M', experience=5)
        Actor.objects.create(name='Jane Doe', age=25, gender='F', experience=3)
        
        try:
            # Login
            print("Logging in...")
            self.selenium.get(f'{self.live_server_url}/admin/login/')
            username_input = self.selenium.find_element(By.NAME, 'username')
            password_input = self.selenium.find_element(By.NAME, 'password')
            username_input.send_keys('admin')
            password_input.send_keys('admin123')
            self.selenium.find_element(By.CSS_SELECTOR, '[type="submit"]').click()
            
            # Navigate to actor list
            print("Navigating to actor list...")
            self.selenium.get(f'{self.live_server_url}/actors/')
            
            # Test search functionality
            print("Testing search functionality...")
            search_input = self.selenium.find_element(By.NAME, 'search')
            search_input.send_keys('John')
            search_input.send_keys(Keys.RETURN)
            
            # Check search results
            print("Checking search results...")
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'actor-list'))
            )
            actors_found = self.selenium.find_elements(By.CLASS_NAME, 'actor-item')
            self.assertEqual(len(actors_found), 1)
            self.assertIn('John Smith', actors_found[0].text)
            
            # Test gender filter
            print("Testing gender filter...")
            Select(self.selenium.find_element(By.NAME, 'gender')).select_by_value('F')
            self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            
            # Check filter results
            print("Checking filter results...")
            WebDriverWait(self.selenium, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'actor-list'))
            )
            actors_filtered = self.selenium.find_elements(By.CLASS_NAME, 'actor-item')
            self.assertEqual(len(actors_filtered), 1)
            self.assertIn('Jane Doe', actors_filtered[0].text)
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise

class ModelTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Создаем тестового режиссера
        self.director = Director.objects.create(
            first_name='Иван',
            last_name='Петров',
            date_of_birth='1980-01-01',
            gender='M',
            contact_info='test@test.com',
            years_of_experience=10
        )
        
        # Создаем тестовый спектакль
        self.play = Play.objects.create(
            title='Тестовый спектакль',
            description='Тестовое описание',
            director=self.director,
            genre='D',
            duration=120
        )
        
        # Создаем тестового актера
        self.actor = Actor.objects.create(
            first_name='Петр',
            last_name='Иванов',
            date_of_birth='1990-01-01',
            gender='M',
            contact_info='actor@test.com'
        )
        
        # Создаем тестовую роль
        self.actor_role = ActorRole.objects.create(
            actor=self.actor,
            play=self.play,
            role_name='Главная роль',
            role_info='Информация о роли'
        )
        
        # Создаем тестовый кастинг
        self.casting = Casting.objects.create(
            actor=self.actor,
            play=self.play,
            role='Тестовая роль',
            status='P'
        )
        
        # Создаем тестовое представление
        self.performance = Performance.objects.create(
            play=self.play,
            date=timezone.now() + timedelta(days=1),
            tickets_available=100,
            ticket_price=1000.00,
            status='scheduled'
        )
        self.performance.actors.add(self.actor)

    def test_director_str(self):
        """Тест строкового представления режиссера"""
        self.assertEqual(str(self.director), 'Иван Петров')

    def test_play_str(self):
        """Тест строкового представления спектакля"""
        self.assertEqual(str(self.play), 'Тестовый спектакль')

    def test_actor_str(self):
        """Тест строкового представления актера"""
        self.assertEqual(str(self.actor), 'Петр Иванов')

    def test_actor_role_str(self):
        """Тест строкового представления роли актера"""
        expected = 'Петр Иванов - Главная роль в Тестовый спектакль'
        self.assertEqual(str(self.actor_role), expected)

    def test_casting_str(self):
        """Тест строкового представления кастинга"""
        self.assertEqual(str(self.casting), 'Петр Иванов - Тестовая роль')

    def test_performance_str(self):
        """Тест строкового представления представления"""
        expected_date = self.performance.date.strftime('%d.%m.%Y %H:%M')
        self.assertEqual(str(self.performance), f'Тестовый спектакль - {expected_date}')

    def test_play_absolute_url(self):
        """Тест получения абсолютного URL спектакля"""
        expected_url = reverse('play_detail', kwargs={'pk': self.play.pk})
        self.assertEqual(self.play.get_absolute_url(), expected_url)

    def test_actor_plays_relationship(self):
        """Тест связи между актером и спектаклями"""
        self.assertEqual(self.actor.plays.count(), 1)
        self.assertEqual(self.actor.plays.first(), self.play)

    def test_performance_actors_relationship(self):
        """Тест связи между представлением и актерами"""
        self.assertEqual(self.performance.actors.count(), 1)
        self.assertEqual(self.performance.actors.first(), self.actor)

    def test_director_validation(self):
        """Тест валидации данных режиссера"""
        with self.assertRaises(Exception):
            Director.objects.create(
                first_name='Test',
                last_name='Director',
                date_of_birth='invalid_date',
                gender='X',  # Неверный пол
                contact_info='test@test.com',
                years_of_experience=-1  # Отрицательный опыт
            )

    def test_play_validation(self):
        """Тест валидации данных спектакля"""
        with self.assertRaises(ValueError):
            Play.objects.create(
                title='',  # Пустое название
                description='Test Description',
                director=self.director,
                genre='Invalid',
                duration=-120  # Отрицательная продолжительность
            )

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
            date=timezone.now() + timedelta(days=1),
            tickets_available=100,
            ticket_price=1000.00,
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
