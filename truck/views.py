import os
import telebot
import time
from requests.exceptions import ReadTimeout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View



# 📌 Telegram BOT TOKEN
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = f"https://umf.madami.uz/webhook/"

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 📌 Bot uchun handlerlar
from bot import handlers

# ✅ Handlerlarni faqat bir marta yuklash uchun setup_bot() funksiyasini ishlatamiz
def setup_bot():
    print("✅ Bot konfiguratsiya qilinmoqda...")
    handlers.main_handlers(bot)
    print("✅ Barcha handlerlar muvaffaqiyatli yuklandi!")



setup_bot()  # ✅ Tugmachalar noto‘g‘ri yuklanmasligi uchun

@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    """ Webhook orqali Telegram botni boshqarish """
    def post(self, request, *args, **kwargs):
        try:
            json_data = request.body.decode('utf-8')
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            return JsonResponse({"status": "ok"}, status=200)

        except ReadTimeout:
            print("⚠️ Telegram API ReadTimeout xatosi. 5 soniyadan keyin qayta urinib ko‘ramiz.")
            time.sleep(5)  # 5 soniya kutish
            return JsonResponse({"status": "retry"}, status=500)

        except Exception as e:
            print(f"⚠️ Noma’lum xato: {e}")
            return JsonResponse({"status": "error"}, status=500)

# ✅ Webhook’ni sozlash
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL}")
