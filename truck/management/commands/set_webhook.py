from django.core.management.base import BaseCommand

from truck.views import set_webhook



class Command(BaseCommand):
    help = "Telegram bot uchun webhook’ni o‘rnatish"

    def handle(self, *args, **kwargs):
        set_webhook()
