from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from theater.models import Director

class Command(BaseCommand):
    help = 'Creates a director user'

    def handle(self, *args, **options):
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

        self.stdout.write(self.style.SUCCESS('Режиссер успешно создан!'))
        self.stdout.write('Логин: director')
        self.stdout.write('Пароль: director123') 