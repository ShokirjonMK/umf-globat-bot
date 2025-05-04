from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from truck.views import TelegramWebhookView
urlpatterns = [
    path('bot/webhook/', TelegramWebhookView.as_view(), name="telegram_webhook"), 
    path('', admin.site.urls, name="truck_admin"), 
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
