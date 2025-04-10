from django.contrib.auth.models import User

# Создаем суперпользователя
User.objects.create_superuser(
    username='superadmin',
    email='superadmin@example.com',
    password='admin123'
)

print("Суперпользователь успешно создан!")
print("Логин: superadmin")
print("Пароль: admin123") 