from django.apps import AppConfig


class CatalogConfig(AppConfig):
    verbose_name = "Библиотека"
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalog'