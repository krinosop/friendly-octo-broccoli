from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.test import TestCase
import time

class TheaterSeleniumTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Настройка Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=service)
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://127.0.0.1:8000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_login_functionality(self):
        # Тест неудачного входа
        self.driver.get(f"{self.base_url}/login/")
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        username_input.send_keys("wrong_user")
        password_input.send_keys("wrong_pass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Проверка сообщения об ошибке
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-danger"))
        )
        self.assertIn("Неверное имя пользователя или пароль", error_message.text)

        # Тест успешного входа
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        username_input.clear()
        password_input.clear()
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Проверка успешного входа
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/home/")
        )
        self.assertIn("home", self.driver.current_url)

    def test_create_performance(self):
        # Вход в систему
        self.driver.get(f"{self.base_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("admin")
        self.driver.find_element(By.NAME, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Переход к созданию спектакля
        self.driver.get(f"{self.base_url}/performances/create/")
        
        # Заполнение формы
        self.driver.find_element(By.NAME, "play").send_keys("Test Play")
        self.driver.find_element(By.NAME, "date").send_keys("2025-04-10 19:00")
        self.driver.find_element(By.NAME, "tickets_available").send_keys("100")
        self.driver.find_element(By.NAME, "ticket_price").send_keys("1000")
        
        # Отправка формы
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Проверка успешного создания
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/performances/")
        )
        self.assertIn("performances", self.driver.current_url)

    def test_delete_performance(self):
        # Вход в систему
        self.driver.get(f"{self.base_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("admin")
        self.driver.find_element(By.NAME, "password").send_keys("admin123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        # Переход к списку спектаклей
        self.driver.get(f"{self.base_url}/performances/")
        
        # Нажатие на кнопку удаления первого спектакля
        delete_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.btn-danger"))
        )
        delete_button.click()
        
        # Подтверждение удаления
        confirm_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
        )
        confirm_button.click()
        
        # Проверка успешного удаления
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/performances/")
        )
        self.assertIn("performances", self.driver.current_url) 