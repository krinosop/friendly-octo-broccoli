from django.contrib.auth.models import User
from theater.models import Director
from django.contrib.auth.hashers import make_password

# Создаем пользователя
user = User.objects.create_user(
    username='director',
    email='director@theater.com',
    password='director123',
    first_name='Иван',
    last_name='Иванов'
)

# Создаем режиссера и связываем с пользователем
director = Director.objects.create(
    user=user,
    first_name='Иван',
    last_name='Иванов',
    date_of_birth='1980-01-01',
    gender='M',
    contact_info='+7 (999) 999-99-99',
    years_of_experience=10
)

print("Режиссер успешно создан!")
print("Логин: director")
print("Пароль: director123") 