from django.apps import AppConfig


class EventsParserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'events_parser'
    verbose_name = 'Парсер событий МПГУ'
