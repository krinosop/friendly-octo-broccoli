from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.contrib.auth.models import User
from theater.models import Director, Play, Performance
from datetime import datetime, timedelta
import time

@tag('selenium')
class TheaterSystemSeleniumTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

        # Создаем тестового пользователя
        cls.user = User.objects.create_user(
            username='admin_test',
            password='admin12345',
            is_staff=True
        )

        # Создаем тестового режиссера
        cls.director = Director.objects.create(
            user=cls.user,
            first_name='Test',
            last_name='Director',
            date_of_birth='1990-01-01',
            gender='M',
            contact_info='test@test.com',
            years_of_experience=5
        )

        # Создаем тестовый спектакль
        cls.play = Play.objects.create(
            title='Test Play',
            description='Test Description',
            director=cls.director,
            genre='drama',
            duration=120
        )

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_login_functionality(self):
        """Тест входа в систему"""
        # Открываем главную страницу
        self.selenium.get(f"{self.live_server_url}/")
        
        # Переходим на страницу входа
        login_link = self.selenium.find_element(By.LINK_TEXT, "Войти")
        login_link.click()

        # Вводим неверные данные
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        
        username_input.send_keys("wrong_user")
        password_input.send_keys("wrong_pass")
        
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Проверяем сообщение об ошибке
        error_message = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Пожалуйста, введите правильные имя пользователя и пароль", error_message.text)

        # Вводим правильные данные
        username_input.clear()
        password_input.clear()
        username_input.send_keys("admin_test")
        password_input.send_keys("admin12345")
        submit_button.click()

        # Проверяем успешный вход
        welcome_message = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "welcome-message"))
        )
        self.assertIn("Добро пожаловать", welcome_message.text)

    def test_create_performance(self):
        """Тест создания нового представления"""
        # Входим в систему
        self.selenium.get(f"{self.live_server_url}/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("admin_test")
        self.selenium.find_element(By.NAME, "password").send_keys("admin12345")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Переходим на страницу создания представления
        self.selenium.find_element(By.LINK_TEXT, "Представления").click()
        self.selenium.find_element(By.LINK_TEXT, "Добавить представление").click()

        # Заполняем форму
        self.selenium.find_element(By.NAME, "play").find_elements(By.TAG_NAME, "option")[1].click()
        self.selenium.find_element(By.NAME, "date").send_keys("2025-04-15T19:00")
        self.selenium.find_element(By.NAME, "tickets_available").send_keys("100")
        self.selenium.find_element(By.NAME, "ticket_price").send_keys("1000")
        status_select = self.selenium.find_element(By.NAME, "status")
        status_select.find_element(By.CSS_SELECTOR, "option[value='scheduled']").click()

        # Отправляем форму
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Проверяем успешное создание
        success_message = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("Представление успешно добавлено", success_message.text)

    def test_delete_performance(self):
        """Тест удаления представления"""
        # Создаем тестовое представление
        performance = Performance.objects.create(
            play=self.play,
            date=datetime.now() + timedelta(days=1),
            tickets_available=100,
            ticket_price=1000.00,
            status='scheduled'
        )

        # Входим в систему
        self.selenium.get(f"{self.live_server_url}/login/")
        self.selenium.find_element(By.NAME, "username").send_keys("admin_test")
        self.selenium.find_element(By.NAME, "password").send_keys("admin12345")
        self.selenium.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Переходим к списку представлений
        self.selenium.find_element(By.LINK_TEXT, "Представления").click()

        # Находим первое представление и удаляем его
        delete_link = self.selenium.find_element(By.CSS_SELECTOR, ".card a.btn-danger")
        delete_link.click()

        # Подтверждаем удаление
        confirm_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-danger"))
        )
        confirm_button.click()

        # Проверяем успешное удаление
        success_message = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("Представление успешно удалено", success_message.text) 