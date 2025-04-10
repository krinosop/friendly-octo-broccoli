from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from theater.models import Director, Actor, Play, Casting
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates test data for the theater system'

    def handle(self, *args, **kwargs):
        # Создаем группы пользователей
        director_group, _ = Group.objects.get_or_create(name='Director')
        actor_group, _ = Group.objects.get_or_create(name='Actor')
        self.stdout.write('Created user groups')

        # Создаем пользователей
        user1 = User.objects.create_user('director1', 'director1@example.com', 'password123')
        user2 = User.objects.create_user('director2', 'director2@example.com', 'password123')
        user3 = User.objects.create_user('actor1', 'actor1@example.com', 'password123')
        user4 = User.objects.create_user('actor2', 'actor2@example.com', 'password123')
        self.stdout.write('Created users')

        # Добавляем пользователей в группы
        director_group.user_set.add(user1, user2)
        actor_group.user_set.add(user3, user4)
        self.stdout.write('Added users to groups')

        # Создаем режиссеров
        director1 = Director.objects.create(
            user=user1,
            first_name='Иван',
            last_name='Петров',
            date_of_birth='1980-01-01',
            gender='M',
            contact_info='director1@example.com',
            years_of_experience=15
        )

        director2 = Director.objects.create(
            user=user2,
            first_name='Мария',
            last_name='Иванова',
            date_of_birth='1985-05-15',
            gender='F',
            contact_info='director2@example.com',
            years_of_experience=10
        )
        self.stdout.write('Created directors')

        # Создаем актеров
        actor1 = Actor.objects.create(
            user=user3,
            first_name='Алексей',
            last_name='Сидоров',
            date_of_birth='1990-03-20',
            gender='M',
            contact_info='actor1@example.com'
        )

        actor2 = Actor.objects.create(
            user=user4,
            first_name='Елена',
            last_name='Смирнова',
            date_of_birth='1992-07-10',
            gender='F',
            contact_info='actor2@example.com'
        )
        self.stdout.write('Created actors')

        # Создаем спектакли
        play1 = Play.objects.create(
            title='Гамлет',
            description='Трагедия Уильяма Шекспира',
            director=director1,
            genre='D',
            duration=180
        )

        play2 = Play.objects.create(
            title='Чайка',
            description='Пьеса А.П. Чехова',
            director=director2,
            genre='D',
            duration=150
        )
        self.stdout.write('Created plays')

        # Создаем кастинги
        casting1 = Casting.objects.create(
            actor=actor1,
            play=play1,
            role='Гамлет',
            casting_date=timezone.now(),
            status='A'
        )

        casting2 = Casting.objects.create(
            actor=actor2,
            play=play2,
            role='Нина Заречная',
            casting_date=timezone.now(),
            status='P'
        )
        self.stdout.write('Created castings')

        self.stdout.write(self.style.SUCCESS('Successfully created test data')) 