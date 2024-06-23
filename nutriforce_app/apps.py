from django.apps import AppConfig


class NutriforceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nutriforce_app'


class CheckoutConfig(AppConfig):
    name = 'checkout'

    def ready(self):
        import checkout.signals