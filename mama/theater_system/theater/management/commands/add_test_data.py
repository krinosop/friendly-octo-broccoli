from django.core.management.base import BaseCommand
from theater.models import Actor, Performance, Play
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Adds test data to the database'

    def handle(self, *args, **options):
        # Создаем новых актеров
        actors_data = [
            {'first_name': 'Анна', 'last_name': 'Петрова', 'date_of_birth': '1990-05-15', 'gender': 'F', 'contact_info': '+7 (999) 123-45-67'},
            {'first_name': 'Михаил', 'last_name': 'Соколов', 'date_of_birth': '1988-08-22', 'gender': 'M', 'contact_info': '+7 (999) 234-56-78'},
            {'first_name': 'Елена', 'last_name': 'Морозова', 'date_of_birth': '1995-03-10', 'gender': 'F', 'contact_info': '+7 (999) 345-67-89'}
        ]

        for actor_data in actors_data:
            actor = Actor.objects.create(**actor_data)
            self.stdout.write(self.style.SUCCESS(f'Created actor: {actor.first_name} {actor.last_name}'))

        # Получаем существующие спектакли
        plays = Play.objects.all()

        # Создаем новые представления
        base_date = datetime.now()
        for i, play in enumerate(plays[:2]):  # Берем первые два спектакля
            for j in range(3):  # Для каждого спектакля создаем по 3 представления
                performance_date = base_date + timedelta(days=i*7 + j*2)  # Разные даты для разных спектаклей
                performance = Performance.objects.create(
                    play=play,
                    date=performance_date,
                    tickets_available=100
                )
                self.stdout.write(self.style.SUCCESS(f'Created performance: {play.title} on {performance_date}')) 