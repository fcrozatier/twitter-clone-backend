from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = "api"

    def ready(self) -> None:
        print("Importing the signals !!!!!!!!")
        import api.signals
