import os
import telebot
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from rest_framework import generics
from .models import ScheduleInterview
from .serializers import ScheduleInterviewSerializer



# 📌 Telegram BOT TOKEN
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = f"https://umf.madami.uz/bot/webhook/"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

from bot import handlers

def setup_bot():
    print("✅ Bot konfiguratsiya qilinmoqda...")
    handlers.main_handlers(bot)
    print("✅ Barcha handlerlar muvaffaqiyatli yuklandi!")



setup_bot()  

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    authentication_classes = []  
    permission_classes = []    

    def post(self, request, *args, **kwargs):
        try:
            json_data = request.body.decode('utf-8')
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            return JsonResponse({"status": "ok"}, status=200)
        except Exception as e:
            print(f"⚠️ Exception: {e}")
            return JsonResponse({"status": "error"}, status=500)


# ✅ Webhook’ni sozlash
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")





class ScheduleInterviewListCreateView(generics.ListCreateAPIView):
    queryset = ScheduleInterview.objects.all()
    serializer_class = ScheduleInterviewSerializer
