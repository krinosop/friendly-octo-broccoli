from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

# Create your models here.

GENDER_CHOICES = [
    ('M', 'Мужской'),
    ('F', 'Женский'),
]

GENRE_CHOICES = [
    ('drama', 'Драма'),
    ('comedy', 'Комедия'),
    ('tragedy', 'Трагедия'),
]

class Director(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Пол')
    years_of_experience = models.IntegerField(verbose_name='Опыт работы (лет)')
    contact_info = models.TextField(verbose_name='Контактная информация')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Режиссер'
        verbose_name_plural = 'Режиссеры'

class Play(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    director = models.ForeignKey(Director, on_delete=models.CASCADE, verbose_name='Режиссер')
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, verbose_name='Жанр')
    duration = models.IntegerField(verbose_name='Продолжительность (минут)')
    description = models.TextField(verbose_name='Описание')
    venue_image = models.ImageField(upload_to='play_venues/', null=True, blank=True, verbose_name='Изображение площадки')

    class Meta:
        verbose_name = 'Спектакль'
        verbose_name_plural = 'Спектакли'
        ordering = ['title']

    def clean(self):
        if not self.title:
            raise ValueError('Название спектакля не может быть пустым')
        if self.duration <= 0:
            raise ValueError('Продолжительность спектакля должна быть положительным числом')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('play_detail', kwargs={'pk': self.pk})

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Пол', default='M')
    contact_info = models.TextField(verbose_name='Контактная информация')
    plays = models.ManyToManyField(Play, through='ActorRole', verbose_name='Спектакли')

    class Meta:
        verbose_name = 'Актер'
        verbose_name_plural = 'Актеры'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ActorRole(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, verbose_name='Актер')
    play = models.ForeignKey(Play, on_delete=models.CASCADE, verbose_name='Спектакль')
    role_name = models.CharField(max_length=100, verbose_name='Название роли')
    role_info = models.TextField(verbose_name='Справочная информация')

    class Meta:
        verbose_name = 'Роль актера'
        verbose_name_plural = 'Роли актеров'

    def __str__(self):
        return f"{self.actor} - {self.role_name} в {self.play}"

class Casting(models.Model):
    STATUS_CHOICES = [
        ('P', 'В процессе'),
        ('A', 'Принят'),
        ('R', 'Отклонен'),
    ]
    
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, related_name='castings')
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name='castings', null=True, blank=True)
    role = models.CharField(max_length=100)
    casting_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    class Meta:
        verbose_name = 'Кастинг'
        verbose_name_plural = 'Кастинги'
        ordering = ['-casting_date']

    def __str__(self):
        return f"{self.actor} - {self.role}"

class Performance(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Запланировано'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершено'),
    ]
    
    play = models.ForeignKey(Play, on_delete=models.CASCADE, related_name='performances')
    date = models.DateTimeField()
    tickets_available = models.IntegerField(default=100)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    actors = models.ManyToManyField(Actor, related_name='performances')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name='Статус')

    class Meta:
        ordering = ['date']
        verbose_name = 'Представление'
        verbose_name_plural = 'Представления'

    def __str__(self):
        return f"{self.play.title} - {self.date.strftime('%d.%m.%Y %H:%M')}"
