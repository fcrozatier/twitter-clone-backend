from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = "accounts"

    def ready(self) -> None:
        print("Importing the signals !!!!!!!!")
        import accounts.signals
