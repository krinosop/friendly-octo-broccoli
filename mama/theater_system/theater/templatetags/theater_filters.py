from django import template

register = template.Library()

@register.filter
def get_genre_display(value):
    GENRE_CHOICES = {
        'C': 'Комедия',
        'D': 'Драма',
        'T': 'Трагедия',
        'M': 'Мюзикл'
    }
    return GENRE_CHOICES.get(value, value)

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 